// expansion_tool — a multi-call command-line front-end for the GoogologyLib
// ordinal / large-number notations.
//
// Invocation model (per the requirements spec):
//
//     <notation> <command> [options...]
//
// The notation is taken from argv[0]'s basename (multi-call binary style,
// like git / BusyBox): copy or symlink the binary to a notation name such as
// `prss` or `knuth`, then run `prss expand -e "(0,1,2)" -n 3`. A single
// generic binary named `expansion_tool` is also built; when invoked under that
// generic name it expects the notation as its FIRST argument
// (`expansion_tool prss expand ...`) for convenience.
//
// Commands:
//   expand      <notation> expand -e <expr> -n <count> [-e <expr> -n <count> ...]
//   compare     <notation> compare -e <expr1> -e <expr2> [-e <expr3> ...]
//   is_standard <notation> is_standard -e <expr1> [-e <expr2> ...]
//   help        <notation> help
//
// Global behaviour:
//   * single-shot argument parsing; the process exits immediately after.
//   * on a bad command / argument, an error is printed to stderr and the
//     process exits with a non-zero status.
//   * normal output goes to stdout; diagnostics go to stderr.

#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <map>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "googology/core/Notation.hpp"
#include "googology/core/Capability.hpp"
#include "googology/core/OrdinalNotation.hpp"
#include "googology/notations/number/knuth/Knuth.hpp"
#include "googology/notations/number/conway/Conway.hpp"
#include "googology/notations/ordinal/sequence/difference/prss/Prss.hpp"
#include "googology/notations/ordinal/sequence/difference/epsilon_ss/EpsilonSS.hpp"
#include "googology/notations/ordinal/veblen/weakveblen/WeakVeblen.hpp"
#include "googology/notations/ordinal/ns/Ns.hpp"

namespace g = googology;
using g::Notation;
using g::OrdinalNotation;
using g::Op;

// ----------------------------------------------------------------------------
// Notation registry (factory)
// ----------------------------------------------------------------------------

static const std::vector<std::string>& knownNotations() {
    static const std::vector<std::string> names = {
        "knuth", "conway", "prss",
        "epsilon_p_ss", "epsilon_omega_ss",
        "weak_veblen", "ns"};
    return names;
}

static bool isKnownNotation(const std::string& name) {
    const auto& n = knownNotations();
    return std::find(n.begin(), n.end(), name) != n.end();
}

static std::unique_ptr<Notation> createNotation(const std::string& name) {
    if (name == "knuth")        return std::make_unique<g::number::Knuth>();
    if (name == "conway")       return std::make_unique<g::number::Conway>();
    if (name == "prss")         return std::make_unique<g::ordinal::Prss>();
    if (name == "epsilon_p_ss") return std::make_unique<g::ordinal::EpspSS>();
    if (name == "epsilon_omega_ss") return std::make_unique<g::ordinal::EpsOmegaSS>();
    if (name == "weak_veblen")  return std::make_unique<g::ordinal::WeakVeblen>();
    if (name == "ns")           return std::make_unique<g::ordinal::Ns>();
    return nullptr;
}

// ----------------------------------------------------------------------------
// Standard-form detection
//
// The library's normalize() rewrites *this to the canonical form and returns
// true on success (legal expression) / false on failure (non-standard, *this
// restored). A *canonical* standard expression is left unchanged by normalize,
// so we decide "is standard" as: normalize() succeeded AND the rendered form
// is unchanged. We run the check on a freshly-reconstructed probe (the
// notation's to_string() round-trips through string_to_it for every notation
// wired here), leaving the caller's object untouched.
// ----------------------------------------------------------------------------

static bool isStandard(const Notation& n) {
    auto probe = createNotation(n.name());
    if (!probe) return false;
    probe->string_to_it(n.to_string());        // reconstruct from its rendered form
    std::string before = n.to_string();
    auto* on = dynamic_cast<OrdinalNotation*>(probe.get());
    if (!on) return false;                      // only ordinal-sequence notations
    bool ok = on->normalize();
    std::string after = probe->to_string();
    return ok && (before == after);
}

// ----------------------------------------------------------------------------
// Small helpers
// ----------------------------------------------------------------------------

[[noreturn]] static void fail(const std::string& msg) {
    std::cerr << "error: " << msg << "\n";
    std::exit(2);
}

static long long parseCount(const std::string& s) {
    try {
        size_t pos = 0;
        long long v = std::stoll(s, &pos);
        if (pos != s.size()) throw std::invalid_argument("trailing characters");
        if (v < 1) throw std::invalid_argument("count must be >= 1");
        return v;
    } catch (const std::exception& e) {
        fail("invalid -n value '" + s + "' (" + e.what() + ")");
    }
}

static std::string basenameOf(const std::string& path) {
    size_t p = path.find_last_of("/\\");
    std::string s = (p == std::string::npos) ? path : path.substr(p + 1);
    if (s.size() >= 4 && s.substr(s.size() - 4) == ".exe")
        s = s.substr(0, s.size() - 4);
    return s;
}

// Parse a list of `-e <expr>` flags. Requires at least minCount entries.
static std::vector<std::string> parseExprList(const std::vector<std::string>& args,
                                              size_t minCount,
                                              const std::string& cmd) {
    std::vector<std::string> exprs;
    size_t i = 0;
    while (i < args.size()) {
        if (args[i] != "-e")
            fail("unexpected token '" + args[i] + "' in '" + cmd + "' (expected -e)");
        if (i + 1 >= args.size())
            fail("'-e' requires an expression argument");
        exprs.push_back(args[++i]);
        ++i;
    }
    if (exprs.size() < minCount) {
        std::string need = (minCount == 1) ? "at least one" :
            "at least " + std::to_string(minCount);
        fail("'" + cmd + "' requires " + need + " -e <expr> argument(s)");
    }
    return exprs;
}

// Parse pairs of `-e <expr> -n <count>` (strict alternation, repeatable).
static void parseExpandPairs(const std::vector<std::string>& args,
                             std::vector<std::pair<std::string, long long>>& out) {
    size_t i = 0;
    while (i < args.size()) {
        if (args[i] != "-e")
            fail("unexpected token '" + args[i] + "' in 'expand' (expected -e)");
        if (i + 1 >= args.size())
            fail("'-e' requires an expression argument");
        std::string expr = args[++i];
        if (i + 1 >= args.size() || args[i + 1] != "-n")
            fail("expected '-n <count>' after '-e " + expr + "'");
        i += 2; // now positioned on the -n value
        if (i >= args.size())
            fail("'-n' requires a count argument");
        long long count = parseCount(args[i]);
        out.push_back({expr, count});
        ++i;
    }
    if (out.empty())
        fail("'expand' requires at least one -e <expr> -n <count> pair");
}

// ----------------------------------------------------------------------------
// Commands
// ----------------------------------------------------------------------------

static int cmdExpand(const std::string& notation, const std::vector<std::string>& args) {
    std::vector<std::pair<std::string, long long>> pairs;
    parseExpandPairs(args, pairs);

    std::ostringstream out;
    bool firstBlock = true;
    for (const auto& pr : pairs) {
        const std::string& expr = pr.first;
        long long count = pr.second;

        auto base = createNotation(notation);
        if (!base) fail("unknown notation '" + notation + "'");
        if (!base->can(Op::Expand))
            fail("notation '" + notation + "' does not support expand()");

        bool canSucc = base->can(Op::Successor);
        bool canStd  = base->can(Op::Normalize);

        if (!firstBlock) out << "\n";
        firstBlock = false;
        out << "# expand: " << expr << "  ->  " << count << " term(s)\n";

        for (long long k = 1; k <= count; ++k) {
            try {
                auto term = createNotation(notation);
                term->string_to_it(expr);
                term->expand(k);   // A[k] (fundamental term) / k-th rewrite step
                out << expr << "[" << k << "] = " << term->to_string();
                if (canSucc || canStd) {
                    auto* on = dynamic_cast<OrdinalNotation*>(term.get());
                    if (canSucc && on)
                        out << "\n    successor: " << (on->isSuccessor() ? "yes" : "no");
                    if (canStd && on)
                        out << "\n    standard:  " << (isStandard(*term) ? "yes" : "no");
                }
                out << "\n";
            } catch (const std::exception& e) {
                fail("failed to expand '" + expr + "' to term " + std::to_string(k) +
                     ": " + e.what());
            }
        }
    }
    std::cout << out.str();
    return 0;
}

static int cmdCompare(const std::string& notation, const std::vector<std::string>& args) {
    std::vector<std::string> exprs = parseExprList(args, 2, "compare");

    auto proto = createNotation(notation);
    if (!proto) fail("unknown notation '" + notation + "'");
    if (!proto->can(Op::Compare))
        fail("comparison is undefined for notation '" + notation +
             "' (large-number notations are not orderable)");

    // Parse each expression and (where the notation defines a standard form)
    // enforce that it is in standard form before comparing.
    std::vector<std::unique_ptr<Notation>> items;
    items.reserve(exprs.size());
    for (const auto& e : exprs) {
        auto o = createNotation(notation);
        try {
            o->string_to_it(e);
        } catch (const std::exception& ex) {
            fail("cannot parse expression '" + e + "': " + ex.what());
        }
        if (o->can(Op::Normalize)) {
            if (!isStandard(*o))
                fail("expression '" + e + "' is not in standard form; "
                     "'compare' requires standard-form inputs");
            auto* on = dynamic_cast<OrdinalNotation*>(o.get());
            on->normalize();   // reduce to canonical form for a fair comparison
        }
        items.push_back(std::move(o));
    }

    // Stable descending sort (largest first). A pre-defined total order exists
    // for every ordinal notation wired here.
    std::vector<size_t> order(items.size());
    std::iota(order.begin(), order.end(), 0);
    std::stable_sort(order.begin(), order.end(), [&](size_t a, size_t b) {
        return items[a]->compare(*items[b]) > 0;   // a before b iff a > b
    });

    std::ostringstream out;
    for (size_t i = 0; i < order.size(); ++i) {
        out << items[order[i]]->to_string();
        if (i + 1 < order.size()) {
            int c = items[order[i]]->compare(*items[order[i + 1]]);
            out << (c > 0 ? " > " : " = ");   // descending => only > or =
        }
    }
    out << "\n";
    std::cout << out.str();
    return 0;
}

static int cmdIsStandard(const std::string& notation, const std::vector<std::string>& args) {
    std::vector<std::string> exprs = parseExprList(args, 1, "is_standard");

    auto proto = createNotation(notation);
    if (!proto) fail("unknown notation '" + notation + "'");
    if (!proto->can(Op::Normalize))
        fail("notation '" + notation + "' does not define a standard form "
             "(is_standard is only available for ordinal-sequence notations)");

    std::ostringstream out;
    for (const auto& e : exprs) {
        auto o = createNotation(notation);
        try {
            o->string_to_it(e);
        } catch (const std::exception& ex) {
            fail("cannot parse expression '" + e + "': " + ex.what());
        }
        bool std = isStandard(*o);
        out << e << (std ? " is standard" : " is not standard") << "\n";
    }
    std::cout << out.str();
    return 0;
}

// ----------------------------------------------------------------------------
// Help
// ----------------------------------------------------------------------------

static void printGenericHelp() {
    std::cout << "expansion_tool — multi-call CLI front-end for GoogologyLib notations\n\n"
              << "USAGE (multi-call):\n"
              << "    <notation> <command> [options...]\n"
              << "  e.g.  prss expand -e \"(0,1,2)\" -n 3\n\n"
              << "USAGE (generic binary):\n"
              << "    expansion_tool <notation> <command> [options...]\n\n"
              << "Known notations:\n";
    for (const auto& n : knownNotations())
        std::cout << "    " << n << "\n";
    std::cout << "\nCommands: expand, compare, is_standard, help\n"
              << "Run '<notation> help' for command details.\n";
}

static void printNotationHelp(const std::string& notation) {
    std::cout << "expansion_tool — notation: " << notation << "\n\n"
              << "USAGE:\n"
              << "    " << notation << " expand -e <expr> -n <count> [-e <expr> -n <count> ...]\n"
              << "    " << notation << " compare -e <expr1> -e <expr2> [-e <expr3> ...]\n"
              << "    " << notation << " is_standard -e <expr1> [-e <expr2> ...]\n"
              << "    " << notation << " help\n\n"
              << "expand\n"
              << "    Expand each -e expression to the number of terms given by the\n"
              << "    following -n. One -e must be paired with one -n; the pair may be\n"
              << "    repeated. The k-th output term is the k-th fundamental term\n"
              << "    A[k] (ordinal notations) or the result after k rewrite steps\n"
              << "    (large-number notations). If the notation defines a successor\n"
              << "    check and/or a standard form, each term is annotated with\n"
              << "    'successor: yes/no' and 'standard: yes/no' where available.\n\n"
              << "compare\n"
              << "    Requires at least two -e expressions. All inputs must be in\n"
              << "    standard form (a non-standard input is reported as an error).\n"
              << "    The expressions are sorted in descending order and printed\n"
              << "    joined by ' > ' (strictly greater) or ' = ' (equal).\n\n"
              << "is_standard\n"
              << "    Requires at least one -e expression. Each expression is tested\n"
              << "    for standard form and printed as '<expr> is standard' or\n"
              << "    '<expr> is not standard'.\n\n"
              << "help\n"
              << "    Print this message.\n\n"
              << "Global: arguments are parsed once; the process exits immediately.\n"
              << "Errors go to stderr with a non-zero exit status.\n";
}

// ----------------------------------------------------------------------------
// main — resolve notation from argv[0], then dispatch.
// ----------------------------------------------------------------------------

int main(int argc, char** argv) {
    std::string prog = (argc > 0) ? basenameOf(argv[0]) : "expansion_tool";
    bool isGeneric = (prog == "expansion_tool");

    std::string notation;
    std::string command;
    std::vector<std::string> args;

    if (isGeneric) {
        // expansion_tool <notation> <command> [options...]
        if (argc < 2 || std::string(argv[1]) == "help") {
            printGenericHelp();
            return (argc < 2) ? 2 : 0;
        }
        notation = argv[1];
        if (argc < 3) {
            command = "help";   // `expansion_tool <notation>` -> notation help
        } else {
            command = argv[2];
            for (int i = 3; i < argc; ++i) args.push_back(argv[i]);
        }
    } else {
        // <notation> <command> [options...]  (multi-call: argv[0] is the notation)
        notation = prog;
        if (argc < 2) {
            command = "help";
        } else {
            command = argv[1];
            for (int i = 2; i < argc; ++i) args.push_back(argv[i]);
        }
    }

    if (!isKnownNotation(notation)) {
        std::cerr << "error: unknown notation '" << notation << "'.\n";
        std::cerr << "Known notations:";
        for (const auto& n : knownNotations()) std::cerr << " " << n;
        std::cerr << "\n";
        return 2;
    }

    if (command == "help")        { printNotationHelp(notation); return 0; }
    if (command == "expand")      { return cmdExpand(notation, args); }
    if (command == "compare")     { return cmdCompare(notation, args); }
    if (command == "is_standard") { return cmdIsStandard(notation, args); }

    std::cerr << "error: unknown command '" << command << "'.\n";
    std::cerr << "Run '" << notation << " help' for usage.\n";
    return 2;
}
