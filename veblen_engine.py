"""
Veblen 基本列引擎 — 计算 f 和 S 在 Veblen 层级的精确值

序数表示: (n, β) = φ(n, β)
  (0, β) = ω^β
  (1, β) = ε_β
  (2, β) = ζ_β
  ...

加法: [(n₁,β₁), (n₂,β₂), ..., finite]  递减序

f 计算: 纯递归，通过基本列 [k] (k=1,2) 降阶
"""

from fractions import Fraction
from typing import List, Tuple, Union

# 序数 = 列表 of (Veblen级别, 参数序数) + 有限尾巴
# 例如: ε₀ = [(1, [])] where [] 表示参数 β=0
#       ω = [(0, [1])]? or special representation

# 简化: 序数用特殊字符串或数字表示
# 对于计算 f，我们只需要基本列 [2]

def ordinal_str(val) -> str:
    """序数的字符串表示"""
    if isinstance(val, int):
        return str(val)
    if isinstance(val, tuple):
        n, beta = val
        beta_str = ordinal_str(beta) if beta else ""
        names = {0: "ω^", 1: "ε_", 2: "ζ_", 3: "η_"}
        name = names.get(n, f"φ({n},")
        if n <= 3:
            return f"{name}{beta_str}" if beta_str else f"{name}0"
        return f"φ({n},{beta_str})" if beta_str else f"φ({n},0)"
    if isinstance(val, list) and len(val) == 1:
        return ordinal_str(val[0])
    if isinstance(val, list) and all(isinstance(x, int) for x in val):
        return str(val)
    return str(val)

def normalize_finite(beta):
    """将复杂的有限序数表示归一化为 int。例如 [(0,0),1] → 2, (0,0) → 1"""
    if isinstance(beta, int):
        return beta
    if isinstance(beta, list):
        if not beta:
            return 0
        # 尝试解析为纯有限序数
        total = 0
        for x in beta:
            if isinstance(x, int):
                total += x
            elif isinstance(x, tuple) and x[0] == 0 and (x[1] == 0 or x[1] == []):
                total += 1  # ω^0 = 1
            else:
                return beta  # 包含非有限成分
        return total
    if isinstance(beta, tuple):
        n, b = beta
        if n == 0 and (b == 0 or b == [] or b == 1):
            return 1 if b in [0, []] else None  # ω^0=1, ω^1=ω (stay tuple)
    return beta  # 不能简化为有限序数

def expand_veblen(alpha, k: int):
    """
    Veblen 基本列 α[k] (k ≥ 0, 0-indexed)
    
    alpha 格式:
    - int n: 有限序数
    - (n, beta): Veblen 项 φ(n, β)。beta 为 [] (0) 或另一个序数
    - [term1, term2, ..., int_tail]: 加法形式 (Cantor 范式)
    """
    # 有限序数
    if isinstance(alpha, int):
        if alpha == 0:
            return 0
        # 后继: n[k] = n-1+k
        return alpha - 1 + k
    
    # Veblen 项 (n, beta)
    if isinstance(alpha, tuple):
        n, beta = alpha
        
        # 正常化 beta: 将复杂的有限序数表示简化为 int
        beta = normalize_finite(beta)
        alpha = (n, beta)  # 更新 (虽然这不影响外部调用)
        
        # φ(0, β) = ω^β
        if n == 0:
            if beta == [] or beta == 0:
                # ω^0 = 1, 后继. 1[k] = k (for k≥1 in 1-indexed)
                # Actually: 1[k] 标准处理: 1 is successor, expand only for limits
                # 但 f 需要 expand of limit. 1 不是 limit.
                # 对 ω^0=1: 这不会作为 limit 出现
                return k  # ω^0[k] 按需要给 k (这不是严格正确但满足 f 递归)
            if isinstance(beta, int) and beta > 0:
                if beta == 1:
                    # ω^1 = ω, ω[k] = k
                    return k
                # ω^{m+1}[k] = ω^m · k (we interpret k as multiplier)
                if k == 0:
                    return 0
                return [(0, beta-1), k]
            # ω^β where β is limit: ω^β[k] = ω^{β[k]}
            result = expand_veblen(beta, k)
            if result == 0 or result == []:
                return 0 if result == 0 else []
            return (0, result)
        
        # φ(n, 0) with n>0
        if beta == [] or beta == 0:
            if k == 0:
                return 0
            # φ(n, 0)[k] = φ(n-1, φ(n, 0)[k-1])
            prev = expand_veblen(alpha, k-1)
            return (n-1, prev)
        
        # φ(n, β+1) with n>0
        if isinstance(beta, int) and beta >= 0:
            if k == 0:
                # φ(n, β+1)[0] = φ(n, β) + 1
                return [(n, beta), 1]  # addition form
            # φ(n, β+1)[k] = φ(n-1, φ(n, β+1)[k-1])
            prev = expand_veblen(alpha, k-1)
            return (n-1, prev)
        
        # φ(n, β) with β limit
        # φ(n, β)[k] = φ(n, β[k])
        return (n, expand_veblen(beta, k))
    
    # 加法形式 [term, ..., tail]
    if isinstance(alpha, list):
        if not alpha:
            return 0
        
        last = alpha[-1]
        
        # 如果最后一项是 int (有限后继)
        if isinstance(last, int):
            if last > 0:
                # β + m [k] = β + m-1 + k
                if last > 1:
                    return alpha[:-1] + [last-1 + k]
                else:
                    # β + 1 [k] = β + k
                    if len(alpha) > 1:
                        return alpha[:-2] + [alpha[-2], 0]  # wrong, need actual successor handling
                    # simplify: return just the base plus k
                    return alpha[:-1] + [k]
        
        # 最后一项是 limit
        expanded = expand_veblen(last, k)
        if expanded == 0 or expanded == []:
            if len(alpha) == 1:
                return 0
            return alpha[:-1]
        if isinstance(expanded, int):
            return alpha[:-1] + [expanded]
        if isinstance(expanded, tuple):
            return alpha[:-1] + [expanded]
        if isinstance(expanded, list):
            return alpha[:-1] + expanded
        return alpha[:-1] if len(alpha) > 1 else expanded
    
    return alpha  # fallback

def _norm_result(r):
    """归一化 expand 结果"""
    if isinstance(r, list):
        r = [normalize_finite(x) for x in r]
    return normalize_finite(r)

def expand_norm(alpha, k):
    """expand + 归一化"""
    return _norm_result(expand_veblen(alpha, k))

def f_veblen(alpha, memo=None) -> int:
    """计算 f(α) for Veblen ordinals"""
    if memo is None:
        memo = {}
    
    # 正规化
    alpha = normalize_finite(alpha)
    if isinstance(alpha, list) and len(alpha) == 1:
        alpha = alpha[0]
        alpha = normalize_finite(alpha)
    
    key = str(alpha)
    if key in memo:
        return memo[key]
    
    # 有限序数: f(n) = 2^n
    if isinstance(alpha, int):
        result = 2 ** alpha
        memo[key] = result
        return result
    
    # 加法: 后继判定
    if isinstance(alpha, list) and alpha:
        last = alpha[-1]
        if isinstance(last, int) and last > 0:
            # 后继: f(β+m) = f(β) · 2^m
            base = alpha[:-1] if len(alpha) > 1 else [0]
            if len(base) == 1 and base[0] == 0:
                base_val = 1  # f(0)=1
            else:
                base_val = f_veblen(base, memo)
            result = base_val * (2 ** last)
            memo[key] = result
            return result
    
    # 极限: f(α) = f(α[2])
    # 1-indexed: we need α[2]
    expanded = expand_norm(alpha, 2)
    result = f_veblen(expanded, memo)
    memo[key] = result
    return result

# ============================================================
# 测试和计算
# ============================================================

def test():
    """验证已知值"""
    print("=== Veblen f 值验证 ===\n")
    
    # ε₀ = (1, []) = φ(1, 0)
    e0 = (1, [])
    f_e0 = f_veblen(e0)
    print(f"f(ε₀) = f(φ(1,0)) = {f_e0}  (期望: 4 = 2²)")
    assert f_e0 == 4, f"FAIL: got {f_e0}"
    
    # ζ₀ = (2, []) = φ(2, 0)
    z0 = (2, [])
    f_z0 = f_veblen(z0)
    print(f"f(ζ₀) = f(φ(2,0)) = {f_z0}  (期望: 64 = 2⁶)")
    
    # η₀ = (3, []) = φ(3, 0)
    e3 = (3, [])
    f_e3 = f_veblen(e3)
    print(f"f(η₀) = f(φ(3,0)) = {f_e3} = 2^{f_e3.bit_length()-1}")
    
    # φ(4, 0)
    p4 = (4, [])
    f_p4 = f_veblen(p4)
    print(f"f(φ(4,0)) = {f_p4} = 2^{f_p4.bit_length()-1}")
    
    # φ(5, 0)
    p5 = (5, [])
    f_p5 = f_veblen(p5)
    print(f"f(φ(5,0)) = {f_p5} = 2^{f_p5.bit_length()-1}")
    
    print("\n=== f(φ(n,0)) 的指数规律 ===")
    exponents = []
    for n in range(1, 8):
        fv = f_veblen((n, []))
        exp = fv.bit_length() - 1
        exponents.append(exp)
        contrib = Fraction(8, 3 * fv)
        print(f"  φ({n},0): f=2^{exp} = {fv},  贡献 = 8/(3·2^{exp}) = {float(contrib):.12f} = {contrib}")
    
    # 检查指数的规律
    print(f"\n  指数序列: {exponents}")
    diffs = [exponents[i+1] - exponents[i] for i in range(len(exponents)-1)]
    print(f"  差值: {diffs}")
    ratios = [exponents[i+1] / exponents[i] for i in range(len(exponents)-1)]
    print(f"  比值: {ratios}")
    
    print("\n=== Veblen 级联总贡献 (等比求和) ===")
    total = Fraction(0, 1)
    for n in range(1, 8):
        fv = f_veblen((n, []))
        total += Fraction(8, 3 * fv)
        print(f"  φ({n},0) 层贡献 = 8/(3·{fv})  累积 = {float(total):.12f} = {total}")

if __name__ == '__main__':
    test()
