# expansion_tool — CLI front-end for GoogologyLib notations

A single command-line tool that drives any notation in `lib/GoogologyLib`
through four commands: `expand`, `compare`, `is_standard`, `help`.

## Invocation model

The notation is taken from **`argv[0]`'s basename** (multi-call binary style,
like `git` / BusyBox): copy or symlink the binary to a notation name, then run
it. A generic `expansion_tool` binary is also provided; when invoked under that
name it expects the notation as its **first** argument.

```
# multi-call style (recommended)
prss          expand -e "(0,1,2)" -n 3
knuth         expand -e "2 ^^ 3"  -n 2
epsilon_p_ss  compare -e "(1,4)" -e "(1,5)"
prss          is_standard -e "(0,1,2)"
prss          help

# generic binary
expansion_tool prss expand -e "(0,1,2)" -n 3
expansion_tool help          # lists known notations
```

Known notations: `knuth`, `conway`, `prss`, `epsilon_p_ss`, `epsilon_omega_ss`,
`weak_veblen`, `ns`.

## Commands

### expand
```
<notation> expand -e <expr> -n <count> [-e <expr> -n <count> ...]
```
Expands each `-e` expression to the `-n` terms. The k-th output term is the
k-th fundamental term `A[k]` (ordinal notations) or the result after `k` rewrite
steps (large-number notations, e.g. Knuth/Conway). One `-e` must be paired with
one `-n`; the pair may be repeated. If the notation defines a **successor check**
and/or a **standard form**, each term is annotated with `successor: yes/no` and
`standard: yes/no` where available.

### compare
```
<notation> compare -e <expr1> -e <expr2> [-e <expr3> ...]
```
Requires **at least two** `-e` expressions. All inputs must be in standard form
(a non-standard input is reported as an error). The expressions are sorted in
descending order and printed joined by `>` (strictly greater) or `=` (equal).
Comparison is only available for ordinal notations; large-number notations
report an error (order is undefined).

### is_standard
```
<notation> is_standard -e <expr1> [-e <expr2> ...]
```
Requires **at least one** `-e` expression. Each is tested for standard form and
printed as `<expr> is standard` or `<expr> is not standard`. Only ordinal-sequence
notations define a standard form.

### help
```
<notation> help
```
Prints the detailed usage for that notation (or, for the generic binary with no
notation, the list of notations).

## Global behaviour

* Arguments are parsed once; the process exits immediately after (no REPL).
* On a bad command / argument, an error is printed to **stderr** and the process
  exits with a **non-zero** status.
* Normal output goes to **stdout**.

## Build

```sh
cd programs
cmake -S . -B build -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Release
cmake --build build --target expansion_tool prss knuth conway \
      epsilon_p_ss epsilon_omega_ss weak_veblen ns
```

Binaries land in `programs/build/`. To use the multi-call style, copy/rename
`expansion_tool.exe` to a notation name, e.g. `cp expansion_tool.exe prss.exe`.

## Implementation notes

* `src/expansion_tool.cpp` — the whole CLI. It resolves the notation from
  `argv[0]`, dispatches to a command handler, and prints to stdout / stderr.
* Standard-form detection delegates to `OrdinalNotation::normalize()` (the
  library's shared, `baseVal_`-parameterized standard-form algorithm). `expand`
  reconstructs each term from its rendered form to test standard form without
  mutating the displayed term.
* `epsilon_p_ss` uses the default cap `p = 1` in the CLI. To use a different `p`,
  build a dedicated `my_symbol` binary that constructs `EpspSS(p, ...)`.

## Known limitation — standard-form detection

The library's shared `normalize()` is, per the project's own notation specs
(`spec/notations/prss.md` flags PrSS standard form as "**⚠ to be verified**"),
currently only recognizes trivial `n ≤ 2` sequences as standard form; its main
loop cannot grow the seed for longer inputs, so most 3+-element expressions are
reported as *not standard*. Consequently `compare` / `is_standard` will *error*
on rich inputs such as `(0,1,2)` even though they expand and compare fine.

This is a property of the **underlying notation library**, not the CLI: the CLI
faithfully implements the spec's "若非标准型, 应报错或跳过" (report error or skip
on non-standard input). Resolving it requires settling the open standard-form
semantics for PrSS / ε-SS in the library. The CLI is ready to pick up a corrected
`normalize()` automatically once it lands.
