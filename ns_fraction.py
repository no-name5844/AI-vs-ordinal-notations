"""
NS (Nonlinear Successor) — 加权分数展开计算器

定义 (1-indexed):
  f(0) = 1
  f(β+1) = f(β) · 2
  f(α) = f(expand(α, 2))    (α 为极限序数)

  S(1) = 1st ℕ𝕊 = 0
  S(α+1) = S(α) + 1/f(α)     (后继)
  S(λ) = lim_{n→ω} S(λ[n])   (极限)

使用加权分数展开形式呈现: S(α) = 0 + 1/2 + 1/4 + 1/8 + ...
每个后继步 = 1/f(β)，f 在每次后继翻倍。

在极限点处:
  - S(λ) = lim S(λ[n])
  - S(λ) 之后的新步长 = 1/f(λ)，其中 f(λ) = f(expand(λ, 2))
  - 从 λ 到下一个极限的收敛增量 = 1/f(λ) · 2
"""

from fractions import Fraction
from typing import List, Tuple

# ========== 序数基本列 ==========

def expand(alpha_str: str, n: int) -> str:
    """标准序数基本列 α[n]。返回序数的字符串表示。"""
    a = alpha_str.strip()
    
    # 有限序数: expand(k, n) = k-1+n (k≥1 后继的情况)
    # 对极限有限序数无定义
    if a.isdigit():
        return a  # 不适用
    
    # ω: ω[n] = n
    if a == 'w':
        return str(n)
    
    # ω·k (k>1): ω·k[n] = ω·(k-1) + n
    if a.startswith('w*') and a[2:].isdigit():
        k = int(a[2:])
        if k > 1:
            return f"w*{k-1}+{n}"
    
    # ω²: ω²[n] = ω·n
    if a == 'w^2':
        return f"w*{n}"
    
    # ω^k (k>2): ω^k[n] = ω^{k-1} · n
    if a.startswith('w^') and a[2:].isdigit():
        k = int(a[2:])
        if k > 2:
            return f"w^{k-1}*{n}"
    
    # ω^ω: ω^ω[n] = ω^n  
    if a == 'w^w':
        return f"w^{n}"
    
    # ω^ω·k + ... : 简单情况
    # ω^(k+1): ω^(k+1)[n] = ω^k · n
    if a.startswith('w^('):
        # 暂不支持
        pass
    
    return a

# ========== f 计算 ==========

# 基本列规则：对于常见的极限序数，expand(α, 2) 的值
EXPAND_2 = {
    'w': '2',
    'w*2': 'w+2',
    'w*3': 'w*2+2',
    'w*4': 'w*3+2',
    'w^2': 'w*2',
    'w^3': 'w^2*2',
    'w^w': 'w^2',
}

def f_val(alpha: str) -> int:
    """计算 f(α)。假设 α 已经归一化。"""
    a = alpha.strip()
    
    # 纯数字: f(k) = 2^k
    if a.isdigit():
        return 2 ** int(a)
    
    # 特殊已知值
    if a in EXPAND_2:
        return f_val(EXPAND_2[a])
    
    # 后继: α = β + k
    if '+' in a:
        parts = [p.strip() for p in a.split('+')]
        # 取最后一部分
        last = parts[-1]
        if last.isdigit():
            k = int(last)
            if k > 0:
                # α = β + k = (β + k-1) + 1
                if k > 1:
                    beta = '+'.join(parts[:-1]) + f"+{k-1}" if parts[:-1] else f"{k-1}"
                else:
                    beta = '+'.join(parts[:-1]) if parts[:-1] else '0'
                # f(β+1) = f(β) * 2，所以 f(β+k) = f(β) * 2^k
                # 但我们需要的是 f(α) = f(α-1) * 2，逐个来
                # 简化：f(β+k) = f(β) * 2^k
                base = '+'.join(parts[:-1]) if parts[:-1] else '0'
                return f_val(base) * (2 ** k)
    
    return 1  # fallback

# ========== 分数展开形式 ==========

def fraction_sum_str(terms: List[Fraction]) -> str:
    """将分数列表格式化为展开形式。"""
    if not terms:
        return "0"
    parts = []
    for t in terms:
        if t.numerator == 1:
            parts.append(f"1/{t.denominator}")
        else:
            parts.append(f"{t.numerator}/{t.denominator}")
    return " + ".join(parts)

def geo_series_label(start: Fraction) -> str:
    """为几何级数生成标签: 1/4 + 1/8 + 1/16 + ..."""
    return f"Σ(1/{start.denominator} + 1/{start.denominator*2} + ...)"

def compute_block(label: str, S_start: Fraction, f_start: int, steps: int = 10) -> Tuple[List[str], Fraction, Fraction]:
    """
    计算一个后继块: 从 S_start 开始，步长初始为 1/f_start，每次后继步长减半。
    
    返回: (行列表, 最后S值, 该块的收敛极限超出量)
    """
    lines = []
    S = S_start
    step = Fraction(1, f_start)
    f_cur = f_start
    
    lines.append(f"--- {label} ---")
    lines.append(f"  f = {f_start}, 步长 = 1/{f_start}")
    
    sum_terms = []
    for i in range(steps):
        S = S + step
        sum_terms.append(step)
        conv = Fraction(2, f_start)  # 完整收敛量 = (1/f) · 2
        approx = float(S)
        lines.append(f"  +1/{f_cur}  →  S = {fraction_sum_str(sum_terms)}  ≈ {approx:.6f}")
        f_cur *= 2
        step = Fraction(1, f_cur)
    
    convergence = Fraction(2, f_start)  # 该块的完整收敛量
    S_limit = S_start + convergence
    lines.append(f"  收敛极限: S + {convergence} = {S_limit}")
    
    return lines, S, convergence

# ========== 主计算 ==========

def main():
    print("=" * 70)
    print("NS (Nonlinear Successor) — 加权分数展开")
    print("S(α) = α th ℕ𝕊")
    print("=" * 70)
    
    # === 块 0: 从 1 到 ω ===
    print("\n【块 0: 1 → ω】")
    print("  S(1) = 0")
    S_val = Fraction(0, 1)
    
    terms = []
    f_cur = 2  # f(1) = 2
    print(f"  f(1) = {f_cur}, 步长 = 1/{f_cur}")
    for k in range(2, 11):
        step = Fraction(1, f_cur)
        S_val = S_val + step
        terms.append(step)
        print(f"  +1/{f_cur}  →  S({k}) = 0 + {fraction_sum_str(terms)}  ≈ {float(S_val):.6f}")
        f_cur *= 2
    
    print(f"  ... 收敛 → S(ω) = 0 + 1/2 + 1/4 + 1/8 + ... = 1")
    S_w = Fraction(1, 1)
    
    # === 块 1: ω → ω·2 ===
    f_w = 4  # f(ω) = f(2) = 4
    print(f"\n【块 1: ω → ω·2】")
    print(f"  S(ω) = 1")
    print(f"  f(ω) = f(2) = {f_w}, 步长 = 1/{f_w}")
    
    terms = []
    f_cur = f_w
    S_val = S_w
    for k in range(1, 8):
        step = Fraction(1, f_cur)
        S_val = S_val + step
        terms.append(step)
        print(f"  +1/{f_cur}  →  S(ω+{k}) = 1 + {fraction_sum_str(terms)}  ≈ {float(S_val):.6f}")
        f_cur *= 2
    
    conv_1 = Fraction(2, f_w)  # 2/4 = 1/2
    print(f"  ... 收敛 → S(ω·2) = 1 + 1/4 + 1/8 + 1/16 + ... = 1 + {conv_1} = 3/2 = 1.5")
    S_w2 = S_w + conv_1
    
    # === 块 2: ω·2 → ω·3 ===
    f_w2 = f_val('w+2')  # f(ω·2) = f(ω+2) = f(ω)·4 = 16
    print(f"\n【块 2: ω·2 → ω·3】")
    print(f"  S(ω·2) = 1 + 1/2")
    print(f"  f(ω·2) = f(ω+2) = {f_w2}, 步长 = 1/{f_w2}")
    
    terms = []
    f_cur = f_w2
    S_val = S_w2
    for k in range(1, 8):
        step = Fraction(1, f_cur)
        S_val = S_val + step
        terms.append(step)
        print(f"  +1/{f_cur}  →  S(ω·2+{k}) = 1+1/2 + {fraction_sum_str(terms)}  ≈ {float(S_val):.6f}")
        f_cur *= 2
    
    conv_2 = Fraction(2, f_w2)  # 2/16 = 1/8
    print(f"  ... 收敛 → S(ω·3) = 1+1/2 + 1/16+1/32+... = 1+1/2 + {conv_2} = 13/8 = 1.625")
    S_w3 = S_w2 + conv_2
    
    # === ω² 的构建 ===
    print(f"\n【ω² 的构建：合并所有 ω·k 极限】")
    print(f"  S(ω·1) = 1")
    print(f"  S(ω·2) = 1 + 1/2")
    print(f"  S(ω·3) = 1 + 1/2 + 1/8")
    print(f"  S(ω·4) = 1 + 1/2 + 1/8 + 1/32")
    print(f"  S(ω·5) = 1 + 1/2 + 1/8 + 1/32 + 1/128")
    print(f"  ...")
    
    # S(ω²) = 1 + 1/2 + 1/8 + 1/32 + 1/128 + ...
    # = 1 + (1/2)/(1 - 1/4) ... wait:
    # 1/2 + 1/8 + 1/32 + 1/128 + ... = Σ_{j=1}^{∞} 1/(2·4^{j-1}) = (1/2)·(1/(1-1/4)) = (1/2)·(4/3) = 2/3
    print(f"  S(ω²) = 1 + 1/2 + 1/8 + 1/32 + 1/128 + ...")
    print(f"        = 1 + (1/2)/(1 - 1/4) = 1 + 2/3 = 5/3 ≈ 1.667")
    
    # === 块: ω² → ω²+ω ===
    f_w2_sq = 16  # f(ω²) = f(ω·2) = 16
    print(f"\n【块: ω² → ω²+ω】")
    print(f"  S(ω²) = 1 + 1/2 + 1/8 + 1/32 + ...")
    print(f"  f(ω²) = f(ω·2) = {f_w2_sq}, 步长 = 1/{f_w2_sq}")
    
    terms = []
    f_cur = f_w2_sq
    # 从 ω² 开始
    S_before_omega_sq = Fraction(5, 3)  # S(ω²)
    S_val = S_before_omega_sq
    for k in range(1, 6):
        step = Fraction(1, f_cur)
        S_val = S_val + step
        terms.append(step)
        print(f"  +1/{f_cur}  →  S(ω²+{k}) = S(ω²) + {fraction_sum_str(terms)}  ≈ {float(S_val):.6f}")
        f_cur *= 2
    
    conv_w2sq = Fraction(2, f_w2_sq)  # 2/16 = 1/8
    print(f"  ... 收敛 → S(ω²+ω) = S(ω²) + 1/16+1/32+... = 5/3 + {conv_w2sq} = 43/24 ≈ 1.792")
    
    # === 块: ω²+ω → ω²+ω·2 ===
    # f(ω²+ω) = f(expand(ω²+ω, 2)) = f(ω²+2)
    # expand(ω²+ω, n) = ω² + n, so expand(ω²+ω, 2) = ω²+2
    f_w2sq_w = f_val('w^2+2') if False else f_w2_sq * 4  # f(ω²+2) = f(ω²+1)·2 = f(ω²)·4 = 64
    print(f"\n【块: ω²+ω → ω²+ω·2】")
    print(f"  f(ω²+ω) = f(ω²+2) = f(ω²)·4 = {f_w2_sq * 4} = 64, 步长 = 1/64")
    
    f_next = f_w2_sq * 4
    conv_next = Fraction(2, f_next)  # 2/64 = 1/32
    print(f"  收敛 → S(ω²+ω·2) = S(ω²+ω) + 1/64+1/128+... = S(ω²+ω) + {conv_next}")
    S_w2sq_w2 = Fraction(43, 24) + conv_next  # 43/24 + 1/32 = (172+3)/96 = 175/96
    
    # === ω²·2 的构建 ===
    print(f"\n【ω²·2 的构建】")
    print(f"  S(ω²+ω·1) = 5/3 + 1/8 = 43/24")
    print(f"  S(ω²+ω·2) = 43/24 + 1/32 = 175/96")
    print(f"  S(ω²+ω·3) = 175/96 + 1/128")
    print(f"  S(ω²+ω·4) = (上一项) + 1/512")
    print(f"  ...")
    # S(ω²·2) = 43/24 + 1/32 + 1/128 + 1/512 + ...
    # = 43/24 + (1/32)/(1 - 1/4) = 43/24 + 1/24 = 44/24 = 11/6
    print(f"  S(ω²·2) = 43/24 + 1/32 + 1/128 + 1/512 + ...")
    print(f"          = 43/24 + (1/32)/(3/4) = 43/24 + 1/24 = 44/24 = 11/6")
    
    # === 总结 ===
    print(f"\n{'='*70}")
    print("NS 值总结（加权分数展开）")
    print(f"{'='*70}")
    print(f"""
    S(1)   = 0
    S(2)   = 0 + 1/2
    S(3)   = 0 + 1/2 + 1/4
    S(4)   = 0 + 1/2 + 1/4 + 1/8
    S(ω)   = 0 + 1/2 + 1/4 + 1/8 + 1/16 + ... = 1
    
    S(ω+1) = 1 + 1/4
    S(ω+2) = 1 + 1/4 + 1/8
    S(ω·2) = 1 + 1/4 + 1/8 + 1/16 + ... = 1 + 1/2
    
    S(ω·2+1) = 1+1/2 + 1/16
    S(ω·3)   = 1+1/2 + 1/16+1/32+1/64+... = 1+1/2+1/8
    
    S(ω²)    = 1 + 1/2 + 1/8 + 1/32 + 1/128 + ...
             = 1 + 2/3 = 5/3
    
    S(ω²+ω)  = 5/3 + 1/8 = 43/24
    S(ω²·2)  = 43/24 + 1/32 + 1/128 + ...
             = 11/6 ≈ 1.833
    """)

if __name__ == '__main__':
    main()
