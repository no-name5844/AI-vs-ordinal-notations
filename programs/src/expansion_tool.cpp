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
#include "googology/notations/real_sequence/ns/Ns.hpp"
#include "googology/notations/ordinal/matrix/bms/BMS.hpp"

namespace g = googology;
using g::Notation;
using g::OrdinalNotation;
using g::Ordinal;
using g::Op;

// ----------------------------------------------------------------------------
// Notation registry (factory)
// ----------------------------------------------------------------------------

static const std::vector<std::string>& knownNotations() {
    static const std::vector<std::string> names = {
        "knuth", "conway", "prss",
        "epsilon_p_ss", "epsilon_omega_ss",
        "weak_veblen", "ns",
        "bm4", "bm1", "bm3.3"};
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
    if (name == "ns")           return std::make_unique<g::real_sequence::Ns>();
    if (name == "bm4")          return std::make_unique<g::ordinal::BM4>();
    if (name == "bm1")          return std::make_unique<g::ordinal::BM1>();
    if (name == "bm3.3")        return std::make_unique<g::ordinal::BM3_3>();
    return nullptr;
}

// ----------------------------------------------------------------------------
// Standard-form detection
//
// The library's OrdinalNotation::is_standard() runs the §12 generic decision
// engine (design.md §12): a downward BFS seeded from the notation's master
// limit expression (roots()), using only the notation's own compare() /
// expand() / clone() / roots(). We run it on a freshly-reconstructed probe
// (to_string() round-trips through string_to_it for every wired notation),
// leaving the caller's object untouched.
// ----------------------------------------------------------------------------

static bool isStandard(const Notation& n) {
    auto probe = createNotation(n.name());
    if (!probe) return false;
    probe->string_to_it(n.to_string());        // reconstruct from its rendered form
    auto* on = dynamic_cast<OrdinalNotation*>(probe.get());
    if (!on) return false;                      // only ordinal-sequence notations
    return on->is_standard();                   // §12 generic decision engine
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
// ns (n,m-Ns, n fixed to 10) — evaluate f(β)=n^β at an ordinal index β read
// from ANOTHER notation's expression. The user only needs the n=10 term, so
// n is hard-wired to 10 and we emit a single f-term (no sequence expansion).
//   ns expand -e <baseNotation> <expression> [-e <baseNotation> <expression> ...]
// Index sources currently wired: "ord" (ω-language), "weak_veblen" (its
// internal Ordinal), "ns" (its own index). Other ordinal notations
// (prss/bms/...) need a notation->Ordinal bridge that is intentionally NOT
// wired yet (see user directive 2026-07-18).
// ----------------------------------------------------------------------------

static Ordinal notationToOrdinal(Notation* n) {
    if (auto* w = dynamic_cast<g::ordinal::WeakVeblen*>(n)) return w->ord();
    if (auto* ns = dynamic_cast<g::real_sequence::Ns*>(n)) return ns->index();
    if (auto* on = dynamic_cast<OrdinalNotation*>(n))
        fail("index source '" + on->name() + "' is not yet wired to an ordinal "
             "(supported: ord, weak_veblen, ns)");
    fail("notation has no ordinal value");
    return Ordinal();   // unreachable
}

static std::vector<std::pair<std::string, std::string>>
parseNsIndices(const std::vector<std::string>& args) {
    std::vector<std::pair<std::string, std::string>> out;
    size_t i = 0;
    while (i < args.size()) {
        if (args[i] != "-e")
            fail("unexpected token '" + args[i] + "' in ns (expected -e)");
        if (i + 2 >= args.size())
            fail("'-e' for ns requires '<baseNotation> <expression>'");
        std::string base = args[++i];
        std::string expr = args[++i];
        ++i;
        if (i + 1 < args.size() && args[i] == "-n") i += 2; // optional, ignored
        out.push_back({base, expr});
    }
    if (out.empty())
        fail("ns requires at least one -e <baseNotation> <expression>");
    return out;
}

static int cmdNsF(const std::vector<std::string>& args) {
    auto idxs = parseNsIndices(args);
    std::ostringstream out;
    for (const auto& kv : idxs) {
        const std::string& base = kv.first;
        const std::string& expr = kv.second;

        Ordinal beta;
        if (base == "ord" || base == "ns") {
            try { beta = Ordinal::parse(expr); }
            catch (const std::exception& e) {
                fail("cannot parse ordinal '" + expr + "': " + e.what());
            }
        } else {
            auto bn = createNotation(base);
            if (!bn) fail("unknown index source notation '" + base + "'");
            try { bn->string_to_it(expr); }
            catch (const std::exception& e) {
                fail("cannot parse '" + expr + "' as " + base + ": " + e.what());
            }
            beta = notationToOrdinal(bn.get());
        }

        g::real_sequence::Ns ns(10, 2);   // n = 10 固定; 只取该项
        ns.setIndex(beta);

        out << "# ns (n=10): index β = " << beta.to_string()
            << "   (source: " << base << " " << expr << ")\n";
        // 只取 n=10 时该项 f(β)=10^β，不输出累加求和的其他项。
        out << "  f(β) = 10^β = " << ns.f(beta) << "\n";
    }
    std::cout << out.str();
    return 0;
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
              << "    For 'ns' (n,m-Ns, n fixed to 10) the -e flag takes TWO arguments\n"
              << "    '<baseNotation> <expression>': the ordinal index β is read from\n"
              << "    that notation's expression. Supported index sources: ord (ω-language),\n"
              << "    weak_veblen, ns. Output is the single term f(β)=10^β (n fixed\n"
              << "    to 10); no accumulated sum of other terms is printed.\n\n"
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
    if (notation == "ns" && (command == "expand" || command == "f"))
        return cmdNsF(args);
    if (command == "expand")      { return cmdExpand(notation, args); }
    if (command == "compare")     { return cmdCompare(notation, args); }
    if (command == "is_standard") { return cmdIsStandard(notation, args); }

    std::cerr << "error: unknown command '" << command << "'.\n";
    std::cerr << "Run '" << notation << " help' for usage.\n";
    return 2;
}
