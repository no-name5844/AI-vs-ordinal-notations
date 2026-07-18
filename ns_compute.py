"""
NS (Nonlinear Successor) 值计算器
基于 README.md 中的定义手算 S(α) = α th ℕ𝕊 和 f(α)

定义:
f(0) = 1
f(β+1) = f(β) * 2
f(α) = f(expand(α, 2))   (α 是极限序数)

1st ℕ𝕊 = 0  (即 S(0) = 0)
(α+1)th ℕ𝕊 = α th ℕ𝕊 + 1/f(α)  (即 S(α+1) = S(α) + 1/f(α))
α th ℕ𝕊 = lim_{n→ω} expand(α, n) th ℕ𝕊  (极限 α)

使用标准 Cantor 范式基本列:
expand(ω^β · (k+1), n) = ω^β · k + ω^{β-1} · n  (当 β 是后继)
                        = ω^β · k + ω^{β[n]}  (当 β 是极限)
等等。
"""

from fractions import Fraction
from typing import Callable

# 序数用整数/字符串表示
# 有限序数: 0, 1, 2, ...
# ω: "w"
# ω+1: "w+1"
# ω·2: "w*2"
# ω²: "w^2"
# 等等

def expand(alpha_str: str, n: int) -> str:
    """
    序数的标准基本列展开: alpha[n]
    支持: 有限序数, ω, ω+k, ω·k, ω², ω^ω, ε₀
    使用标准 Cantor 范式基本列
    """
    a = alpha_str.strip()
    
    # 有限序数: expand(k, n) 对后继无定义 (返回自身作为标记)
    if a.isdigit():
        k = int(a)
        return str(k)  # 有限序数的基本列就是自身 (后继无基本列)
    
    # ω: expand(ω, n) = n
    if a == 'w':
        return str(n)
    
    # ω + k: expand(ω+k, n) = ω + (k-1) + n (如果 k>0 是后继)
    # 实际上 expand(ω+k, n) = ω + (k-1) 对于后继，但我们处理为 expand(ω, n) 的推广
    # 标准定义: expand(ω·a + b, n) = ω·a + (b-1) + n (b>0 后继) 或更复杂
    
    # 简化为：解析加法
    if '+' in a:
        parts = a.split('+')
        base = '+'.join(parts[:-1])
        last = parts[-1].strip()
        if last.isdigit():
            k = int(last)
            if k > 0:
                return f"{base}+{k-1}+{n}" if base != 'w' else f"w+{k-1}+{n}"
    
    # ω·k (k>1): expand(ω·k, n) = ω·(k-1) + n
    if a.startswith('w*') and a[2:].isdigit():
        k = int(a[2:])
        if k > 1:
            return f"w*{k-1}+{n}"
    
    # ω^2: expand(ω², n) = ω·n
    if a == 'w^2':
        return f"w*{n}"
    
    # ω^ω: expand(ω^ω, n) = ω^n
    if a == 'w^w':
        return f"w^{n}"
    
    # ε₀: expand(ε₀, n) = ω^ω^...^ω (n层) 即 φ(ω↑↑n)
    if a == 'e0':
        # Approximate: ω^ω (when n=2), ω^ω^ω (when n=3), etc.
        return 'w^' * n + 'w'
    
    # 简单情形：未知则返回自身
    return a

def f(alpha_str: str, memo: dict = None) -> Fraction:
    """
    计算 f(α):
    f(0) = 1
    f(β+1) = f(β) * 2
    f(limit α) = f(expand(α, 2))
    """
    if memo is None:
        memo = {}
    if alpha_str in memo:
        return memo[alpha_str]
    
    a = alpha_str.strip()
    
    # f(0) = 1
    if a == '0':
        result = Fraction(1, 1)
        memo[a] = result
        return result
    
    # 后继: α = β + 1
    if a.isdigit():
        k = int(a)
        if k > 0:
            result = f(str(k-1), memo) * 2
            memo[a] = result
            return result
    
    # ω: 极限，f(ω) = f(expand(ω, 2)) = f(2)
    if a == 'w':
        result = f(expand('w', 2), memo)
        memo[a] = result
        return result
    
    # ω + k 或更复杂的表达式: 先判断是否为后继
    # 如果是后继形式: f(β+1) = f(β)·2
    # 如果是极限: f(α) = f(expand(α, 2))
    
    # 尝试解析加法
    if '+' in a:
        parts = a.split('+')
        # 检查最后一部分是否大于0
        last = parts[-1].strip()
        if last.isdigit():
            k = int(last)
            if k > 0:
                # 后继: α = (ω·a + (k-1)) + 1, 即 β = ω·a + (k-1)
                beta = '+'.join(parts[:-1])
                if k > 1:
                    beta = f"{beta}+{k-1}" if beta else f"{k-1}"
                else:
                    beta = beta if beta else '0'
                result = f(beta, memo) * 2
                memo[a] = result
                return result
    
    # 默认：极限序数
    result = f(expand(a, 2), memo)
    memo[a] = result
    return result

def S(alpha_str: str, memo_f: dict = None, memo_S: dict = None) -> Fraction:
    """
    计算 S(α) = α th ℕ𝕊
    
    S(0) = 0
    S(α+1) = S(α) + 1/f(α)
    S(limit α) = 由极限定义 (这里不直接计算极限本身，而是计算后继序列)
    """
    if memo_f is None:
        memo_f = {}
    if memo_S is None:
        memo_S = {}
    if alpha_str in memo_S:
        return memo_S[alpha_str]
    
    a = alpha_str.strip()
    
    # S(0) = 0
    if a == '0':
        result = Fraction(0, 1)
        memo_S[a] = result
        return result
    
    # 后继
    if a.isdigit():
        k = int(a)
        if k > 0:
            result = S(str(k-1), memo_f, memo_S) + Fraction(1, 1) / f(str(k-1), memo_f)
            memo_S[a] = result
            return result
    
    # ω 或更复杂
    if '+' in a:
        parts = a.split('+')
        last = parts[-1].strip()
        if last.isdigit():
            k = int(last)
            if k > 0:
                # 后继
                if k > 1:
                    beta = '+'.join(parts[:-1]) + f"+{k-1}" if parts[:-1] else f"{k-1}"
                else:
                    beta = '+'.join(parts[:-1]) if parts[:-1] else '0'
                    if not beta:
                        beta = '0'
                result = S(beta, memo_f, memo_S) + Fraction(1, 1) / f(beta, memo_f)
                memo_S[a] = result
                return result
    
    # 极限： S(α) = lim_{n→∞} S(expand(α, n))
    # 我们需要表示这个极限。对于分析目的，计算前 N 项的近似
    # 这里返回一个标记表示极限
    memo_S[a] = f"LIMIT({a})"
    return f"LIMIT({a})"

def S_limit_approx(alpha_str: str, max_n: int = 20, memo_f: dict = None, memo_S: dict = None) -> list:
    """
    对极限序数 α，计算 S(expand(α, n)) 的前 max_n 项来近似极限
    """
    results = []
    for n in range(1, max_n + 1):
        expanded = expand(alpha_str, n)
        val = S(expanded, memo_f, memo_S)
        results.append((n, expanded, val))
    return results

# ===== 计算 =====
if __name__ == '__main__':
    memo_f = {}
    memo_S = {}
    
    print("=" * 60)
    print("NS (Nonlinear Successor) 计算")
    print("S(α) = α th ℕ𝕊")
    print("=" * 60)
    
    # 有限序数
    print("\n--- 有限序数 ---")
    for k in range(0, 11):
        print(f"  S({k:2d}) = {S(str(k), memo_f, memo_S)}")
        print(f"  f({k:2d}) = {f(str(k), memo_f)}")
    
    # ω
    print("\n--- ω ---")
    print(f"  f(ω) = f(2) = {f('w', memo_f)}")
    print()
    
    # S(ω) 的近似 (ω 的基本列是 n)
    print("  S(ω) = lim S(n):")
    for i in range(1, 11):
        print(f"    S({i}) = {S(str(i), memo_f, memo_S)}", end="")
        if i >= 2:
            print(f" = 2 - 1/2^{i-1} = {Fraction(2,1) - Fraction(1, 2**(i-1))}")
        else:
            print()
    print(f"  => S(ω) = 2")
    
    # ω+1 到 ω+5
    print("\n--- ω+k ---")
    # 手动计算 S(ω) 的近似值...实际上 S(ω) 由极限定义，但我们先把它当作 2
    S_w = Fraction(2, 1)
    f_w = f('w', memo_f)  # f(ω) = f(2) = 4
    
    print(f"  S(ω) ≈ {S_w}")
    print(f"  f(ω) = {f_w}")
    for k in range(1, 6):
        # S(ω+k) 需要知道 f(ω+k-1) 和 S(ω+k-1)
        # 这里手动递推
        pass
    
    # 更系统的计算：从 ω 开始的序列
    print("\n--- 从 ω 到 ω·2 的序列 ---")
    # 用递推计算 S(ω+k) 的值
    vals = [S_w]  # S(ω)
    for k in range(1, 16):
        prev_alpha = f"w+{k-1}" if k > 1 else "w"
        f_val = f(prev_alpha, memo_f)
        next_val = vals[-1] + Fraction(1, 1) / f_val
        vals.append(next_val)
        if k <= 5 or k in [10, 15]:
            print(f"  S(ω+{k}) = {next_val} = {float(next_val):.8f}")
            print(f"    f(ω+{k-1}) = {f_val}")
    
    # ω·2 
    print(f"\n  S(ω·2) ≈ S(ω+15) = {vals[-1]} = {float(vals[-1]):.8f}")
    print(f"  S(ω·2) 极限 ≈ 2 + Σ 1/(4·2^k) = 2 + 1/2 = 2.5")
    
    # f(ω·2)
    f_w2 = f('w*2', memo_f)
    print(f"  f(ω·2) = f(w+2) = {f_w2}")
    
    # ω·2 到 ω·3 的序列
    print("\n--- 从 ω·2 到 ω·3 的序列 ---")
    f_w2_val = f('w*2', memo_f)
    S_w2_approx = Fraction(5, 2)  # 2.5
    vals2 = [S_w2_approx]
    for k in range(1, 11):
        prev_alpha = f"w*2+{k-1}" if k > 1 else "w*2"
        f_val = f(prev_alpha, memo_f)
        next_val = vals2[-1] + Fraction(1, 1) / f_val
        vals2.append(next_val)
        if k <= 5 or k == 10:
            print(f"  S(ω·2+{k}) = {next_val} = {float(next_val):.8f}")
    
    print(f"\n  S(ω·3) ≈ S(ω·2+10) = {vals2[-1]} = {float(vals2[-1]):.8f}")
    print(f"  S(ω·3) 极限 ≈ 2.5 + Σ 1/(16·2^k) = 2.625")
    
    # 总结收敛模式
    print("\n" + "=" * 60)
    print("NS 收敛模式总结")
    print("=" * 60)
    print("""
    S(0)    = 0
    S(1)    = 1
    S(2)    = 1.5
    S(3)    = 1.75
    S(4)    = 1.875
    ...
    S(n)    = 2 - 1/2^{n-1}  (n ≥ 1)
    S(ω)    = 2
    
    f(ω) = 4
    S(ω+1)  = 2 + 1/4 = 2.25
    S(ω+2)  = 2.375
    ...
    S(ω·2)  = 2.5
    
    f(ω·2) = f(ω+2) = 16
    S(ω·2+1) = 2.5625
    ...
    S(ω·3)  = 2.625
    
    模式: S(ω·k) = 2 + Σ_{j=1}^{k-1} 2/4^j
    S(ω²)   = 2 + 2/3 = 8/3 ≈ 2.667
    
    一般规律：
    - 后继步长 = 1/f(α)，每次后继 f 翻倍
    - 极限点处的 f 值由 expand(α, 2) 决定
    - NS 值始终在 [0, 3) 内（？）
    """)
