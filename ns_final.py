"""
NS 复位级联的完整图景

关键发现: ψ(x) th ℕ𝕊 = x → S 必须满射 ℝ⁺ → S 无界!

复位机制是无界增长的来源:
  每个"大层次极限"序数通过基本列[2]追溯到 ε₀,
  f = f(ε₀) = 4, 贡献 8/9.

BM4 → NS 对应 (基于结构对比):
  (0)(1,1)     → ε₀     S ≈ 2.733  (S(ω^ω)+8/9)
  (0)(1,1)(2,1) → ζ₀     S ≈ 2.788  (S(ε_ω)+小量)
  (0)(1,1,1)   → φ_ω(0)  S ≈ 2.788
  更高表达式    → Γ₀     S ≈ 3.677  (再+8/9!)
  再高         → SVO    S ≈ 4.566
  ...
"""

from fractions import Fraction

print("=" * 70)
print("NS 复位级联: 完整的 S 增长图景")
print("=" * 70)

# 基础贡献
S_ww = Fraction(1, 1)
for k in range(1, 6):
    S_ww += Fraction(8, 3 * 2**(2**k))

# 非复位 Veblen 贡献
veblen_small = Fraction(1, 18) + Fraction(1, 4608)

RESET_CONTRIB = Fraction(8, 9)  # 每次复位贡献

reset_names = [
    "ε₀      [BM4: (0)(1,1)]",
    "Γ₀      [BM4: ?]",
    "SVO     [BM4: ?]",
    "LVO     [BM4: ?]",
    "BHO     [BM4: ?]",
]

S = S_ww  # S(ω^ω)
print(f"\\n{'层':<25s} {'贡献':<15s} {'累积 S':<15s}")
print("-" * 55)
print(f"{'S(ω^ω)':<25s} {'':<15s} {float(S):.6f}")

# ε₀ 复位
S += RESET_CONTRIB
print(f"{reset_names[0]:<25s} {'+8/9':<15s} {float(S):.6f}")

# Veblen 非复位层
S += veblen_small
print(f"{'Veblen(ζ,η,...)':<25s} {'+1/18+1/4608...':<15s} {float(S):.6f}")

# Γ₀, SVO, LVO, BHO 连续复位
for i in range(1, 5):
    S += RESET_CONTRIB
    print(f"{reset_names[i]:<25s} {'+8/9':<15s} {float(S):.6f}")

print(f"\\n═══════════════════════════════════════════════")
print("关键结论:")
print(f"  1. ψ(x) 的逆定义 → S 必然无界")
print(f"  2. 复位机制 (f→4) 是 S 增长的引擎")
print(f"  3. 每次层次极限复位贡献 8/9 ≈ 0.889")
print(f"  4. S 的增长 ≈ S(ω^ω) + N·8/9 (N=复位次数)")
print(f"  5. BM4 表达式越高 → 对应序数越大 → S 越大")
