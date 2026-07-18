"""
NS_BM4 v2
"""
print("SCRIPT STARTED", flush=True)

import subprocess
from fractions import Fraction

TOOL = "Program/expansion_tool.exe"

def expand(expr, n):
    """BM4 展开: 返回第1到第n项的列表"""
    cmd = [TOOL, "bm4", "expand", "-e", expr, "-n", str(n)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    terms = []
    for line in r.stdout.split('\n'):
        if '[' in line and '=' in line:
            rhs = line.split('=', 1)[1].strip()
            terms.append(rhs)
    return terms

def cols(expr):
    """解析 BM4 表达式为列列表"""
    if not expr or not expr.strip():
        return []
    s = expr.strip()
    out = []
    d = start = 0
    for i, c in enumerate(s):
        if c == '(':
            if d == 0: start = i
            d += 1
        elif c == ')':
            d -= 1
            if d == 0: out.append(s[start:i+1])
    return out

def is_succ(expr):
    """末列是否全零"""
    c = cols(expr)
    if not c: return False
    last = c[-1].strip('()')
    return last and all(p.strip() == '0' for p in last.split(','))

def pred(expr):
    """去掉末列"""
    return ''.join(cols(expr)[:-1])

f_m = {}
def f(expr):
    k = expr.strip()
    if k in f_m: return f_m[k]

    if k == '':
        # Trans(()) = 0, f(0) = 1
        f_m[k] = 1
        return 1

    if k == '(0)':
        # Trans((0)) = 1. (0) 是 () 的后继, f(1) = f(0)·2 = 2
        f_m[k] = f('') * 2
        return f_m[k]

    if is_succ(k):
        r = f(pred(k)) * 2
        f_m[k] = r
        return r

    # 极限: f(M) = f(M[2])
    terms = expand(k, 2)
    expanded = terms[1] if len(terms) >= 2 else (terms[0] if terms else '')
    if not expanded:
        expanded = pred(k) if is_succ(k) else ''
    r = f(expanded)
    f_m[k] = r
    return r

S_m = {}
def S(expr):
    k = expr.strip()
    if k in S_m: return S_m[k]

    if k == '(0)':
        S_m[k] = Fraction(0, 1)
        return Fraction(0, 1)

    if k == '':
        S_m[k] = Fraction(0, 1)
        return Fraction(0, 1)

    if is_succ(k):
        p = pred(k)
        r = S(p) + Fraction(1, f(p))
        S_m[k] = r
        return r

    # 极限: 用前 20 项近似
    terms = expand(k, 20)
    last = Fraction(0, 1)
    for t in terms:
        if t:
            last = S(t)
    S_m[k] = last
    return last

if True:
    # f
    print("--- f 值 ---")
    for t in ['', '(0)', '(0)(0)', '(0)(1)', '(0)(1,1)']:
        print(f"  f({t:18s}) = {f(t)}")
    # S
    print("--- S 值 ---")
    for t in ['(0)','(0)(0)','(0)(1)','(0)(1,1)']:
        print(f"  S({t:18s}) = {float(S(t)):.10f}")
