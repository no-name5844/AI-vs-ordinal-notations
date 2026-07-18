"""
NS 继续推高: ω^ω 之后
使用 ns_engine 的 f 递归计算，手动推导 S 的级联结构。

核心原理:
  每个极限序数 λ 初始化一个几何级数块
  块内步长: 1/f(λ), 1/(2f(λ)), 1/(4f(λ)), ...
  块收敛: 2/f(λ)
  下一层 λ': f(λ') = f(expand(λ', 2))

只需追踪三点: S(λ) 的值、f(λ)、以及从 λ 到下一个极限的路径。
"""

from fractions import Fraction
import sys
sys.path.insert(0, '.')
from ns_engine import f_of, expand, S_of

def trace(alpha: str, S_val: Fraction, levels: int = 3, sub_levels: int = 3):
    """
    从 α 开始，展示级联结构。
    α: 起始极限序数
    S_val: S(α) 的值
    levels: 展示多少个大块
    sub_levels: 每个大块内展示多少个子块
    """
    memo_f = {}
    cur = alpha
    s = S_val
    
    print(f"\n{'='*60}")
    print(f"  从 {alpha} 开始 (S = {float(s):.10f})")
    print(f"{'='*60}")
    
    for L in range(levels):
        f_start = f_of(cur, memo_f)
        block_conv = Fraction(2, f_start)
        
        # 展示后继步骤
        print(f"\n  块 {L+1}: {cur} → 下一极限 (f={f_start}, 块收敛={block_conv})")
        tmp_s = s
        tmp_cur = cur
        denoms = []
        for i in range(min(sub_levels, 5)):
            f_cur = f_of(tmp_cur, memo_f)
            d = f_cur
            denoms.append(d)
            tmp_s = tmp_s + Fraction(1, d)
            # 下一序数
            if tmp_cur.isdigit():
                nxt = str(int(tmp_cur) + 1)
            elif '+' in tmp_cur:
                parts = tmp_cur.rsplit('+', 1)
                beta = parts[0].strip()
                last = parts[1].strip()
                if last.isdigit():
                    nxt = f"{beta}+{int(last)+1}"
                else:
                    nxt = f"{tmp_cur}+1"
            else:
                nxt = f"{tmp_cur}+1"
            exp_str = " + ".join([f"1/{d}" for d in denoms])
            print(f"    +1/{d:<6d} → S({nxt:20s}) = {float(tmp_s):.12f}  [{exp_str}]")
            tmp_cur = nxt
        
        s = s + block_conv
        print(f"    ... → 极限 S = {float(s):.12f}")
        
        # 下一块的序数
        if cur == 'w^w':
            cur = 'w^w+w'
        elif cur.endswith('+w'):
            base = cur[:-2]
            # 尝试解析 ω^... 的系数
            cur = base + '+w*2' if base else 'w^w+w*2'
        elif '+w*' in cur:
            # 增加系数
            import re
            m = re.search(r'\+w\*(\d+)$', cur)
            if m:
                c = int(m.group(1))
                base = cur[:-(len(f'+w*{c}'))]
                cur = f"{base}+w*{c+1}"
            else:
                cur = cur + '+w'
        elif cur == 'w^w+1':
            cur = 'w^w+w'
        else:
            cur = cur + '+w'
        
        if L == levels - 1:
            break


# 手动定义更高级的序数
# 使用递归 f 计算

def compute_higher():
    """计算 ω^ω 以上的 S 值"""
    
    # S(ω^ω) = 17/9
    # f(ω^ω) = f(exp(ω^ω, 2)) = f(ω²) = 16
    
    S_ww = Fraction(17, 9)
    
    trace('w^w', S_ww, levels=4, sub_levels=4)
    
    print("\n" + "=" * 60)
    print("  关键高层序数值")
    print("=" * 60)
    
    # 手动计算关键点
    # ω^ω → ω^ω+ω: f=16, conv=1/8
    S_www = S_ww + Fraction(1, 8)  # 145/72
    print(f"  S(ω^ω+ω) = 17/9 + 1/8 = 145/72 ≈ {float(S_www):.10f}")
    
    # ω^ω+ω → ω^ω+ω·2: f(ω^ω+ω) = f(ω^ω+2) = f(ω^ω)·4 = 64
    # conv = 2/64 = 1/32
    f_www_w = 64
    S_www_w2 = S_www + Fraction(2, f_www_w)
    print(f"  f(ω^ω+ω) = {f_www_w}, conv = 1/32")
    print(f"  S(ω^ω+ω·2) = {float(S_www_w2):.10f}")
    
    # ω^ω 层级的总贡献 (像 ω² → ω³ 那样)
    # 子块: f=16, 64, 256, 1024, ...
    # 总贡献: 2/16 + 2/64 + 2/256 + ... = 1/8 · (1/(1-1/4)) = 1/6
    total_ww_level = Fraction(1, 6)
    S_www_w = S_ww + total_ww_level  # ω^(ω+1)
    print(f"\n  ω^ω 层总贡献 = 1/8 + 1/32 + 1/128 + ... = 1/6")
    print(f"  S(ω^(ω+1)) = 17/9 + 1/6 = 17/9 + 3/18 = {17*2+3}/18 = 37/18")
    
    S_wpw = Fraction(17, 9) + Fraction(1, 6)
    print(f"    = {float(S_wpw):.10f}")
    
    # ω^(ω+1) 之后: 类似于 ω 层级但是移动后的
    # f(ω^(ω+1)) = f(expand(ω^(ω+1), 2)) = f(ω^ω · 2)
    # expand(ω^ω · 2, 2) = ω^ω + ω²
    # f(ω^ω · 2) = f(ω^ω + ω²) = ... 
    # 这需要逐步递归
    
    # 简化: ω^(ω+1) 到 ω^(ω·2) 的模式
    # 类似 ω 到 ω² 的模式，但 f 更大
    f_wpw = f_of('w^w*2', {}) if False else 16  # 先手动
    
    # 实际上，我们需要计算 f(ω^ω · 2)
    print(f"\n  f(ω^ω · 2) 的计算:")
    exp = expand('w^w*2', 2)
    print(f"    expand(ω^ω · 2, 2) = {exp}")
    # expand(ω^ω · 2, n) 在标准的 Cantor 范式里: ω^ω[n] = ω^n
    # 所以 ω^ω · c [n] = ω^ω · (c-1) + ω^n
    # ω^ω · 2 [2] = ω^ω + ω² = w^w + w^2
    
    # f(ω^ω + ω²): 
    # expand(ω^ω + ω², 2) = ω^ω + ω·2
    f_ww_w2 = f_of('w^w+w^2', {})
    print(f"    f(ω^ω + ω²) = {f_ww_w2}")
    print(f"    f(ω^(ω+1)) = f(ω^ω · 2) = f(ω^ω + ω²) = {f_ww_w2}")
    
    # 检查这个值是否和 f(ω²) 一样
    print(f"    (对比: f(ω²) = {f_of('w^2', {})})")


if __name__ == '__main__':
    compute_higher()
