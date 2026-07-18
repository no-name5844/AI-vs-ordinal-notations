"""
NS Veblen 完整级联 — 精确分数

猜想: f(φ(n,0)) = 2^{g(n)} 其中 g(n) = 2^{n+1} - 2
  n=1: g=2,    f=4       (ε₀, ✓)
  n=2: g=6,    f=64      (ζ₀, ✓)
  n=3: g=14,   f=16384   (η₀)
  n=4: g=30,   f≈1.07e9  (φ(4,0))
  n=5: g=62,   f≈4.61e18
  n=6: g=126,  f≈8.51e37
  n=7: g=254,  f≈2.89e76

每层 Veblen 内部级联 (等比, 公比 1/4):
  φ(n,0) 层总贡献 = 8/(3·f(φ(n,0))) · (1 + 1/4 + 1/16 + ...)
                 = 8/(3·f(φ(n,0))) · 4/3
                 = 32/(9·f(φ(n,0)))
                 = 32/(9·2^{g(n)})

Veblen 层级联总贡献 (所有 n≥1 求和):
  Σ_{n=1}^{∞} 32/(9·2^{g(n)})
  = 32/9 · (1/2² + 1/2⁶ + 1/2¹⁴ + 1/2³⁰ + ...)

  这收敛极快 (双指数衰减)
  实际 = 32/9 · (1/4 + 1/64 + 1/16384 + ...)
       = 8/9 + 1/18 + 1/4608 + ...
"""

from fractions import Fraction

print("=" * 70)
print("NS Veblen 完整级联 — 精确分数")
print("=" * 70)

total = Fraction(0, 1)
print(f"\n{'n':<4s} {'g(n)':<10s} {'f=2^g':<25s} {'层贡献=32/(9·f)':<30s} {'累积':<20s}")
print("-" * 90)

for n in range(1, 9):
    g = 2**(n+1) - 2
    fv = 2**g
    contrib = Fraction(32, 9 * fv)
    total += contrib
    contrib_float = float(contrib)
    total_float = float(total)
    
    if n <= 5:
        print(f"φ({n},0)  g={g:<8d} 2^{g:<23d} 32/(9·2^{g}) = {contrib}    Σ={total}")
    else:
        print(f"φ({n},0)  g={g:<8d} 2^{g:<23d} {contrib_float:.2e}                              ≈ {total_float:.10f}")

print(f"\nVeblen 级联总贡献 = {total} ≈ {float(total):.12f}")

print(f"\n分项:")
print(f"  ε 级联:  32/(9·2²) = 32/36 = 8/9")
print(f"  ζ 级联:  32/(9·2⁶) = 32/576 = 1/18")
print(f"  η 级联:  32/(9·2¹⁴) = 32/(9·16384) = 1/4608")

# 总 S 值
S_ww = Fraction(1, 1)
for k in range(1, 6):
    S_ww += Fraction(8, 3 * 2**(2**k))

S_total = S_ww + total
print(f"\nS(Γ₀) = S(ω^ω) + Veblen总贡献")
print(f"       ≈ {float(S_ww):.6f} + {float(total):.6f}")
print(f"       ≈ {float(S_total):.6f} = {S_total}")
