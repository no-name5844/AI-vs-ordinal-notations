# TraceMark 记忆文档

## 2026-07-18: NS vs BM4 分析启动

### 工具情况
- 展开器：`Program/expansion_tool.exe`（GoogologyLib C++）
  - 支持 `ns expand/compare`、`bm4 expand/compare/is_standard`
  - NS 的 expand 仅支持极限表达式（如 `w`），不支持后继；compare 支持完整序数语法（`w+1`、`w^2`、`w^w`...）
  - BM4 完全支持 expand/compare/is_standard
  - **NS 工具不充分，主要靠定义手算**

### BM4 基本列规律
- 末列全零 → 后继；末列有非零 → 极限
- 基本列模式分为三类：线性增长、周期重复、交错模式
- **等价性**：前置 0 行不改变序数值：`(0)(1,1) = (0,0)(1,1)` 等

### NS 核心规律（2026-07-18 修正：1-indexed）
- **索引从 1 开始**：$S(1)=1\text{st }\mathbb{NS}=0$
- 有限序数：$S(n)=1-1/2^{n-1}$，收敛到 $S(\omega)=1$
- $f(\omega\cdot k)=4^k$
- $S(\omega\cdot k)$ 收敛到 $S(\omega^2)=5/3$
- NS 使用标准序数基本列，$f$ 函数控制非线性步长

### 对比结论
- NS 是"序数→实数"映射，BM4 是"矩阵→序数"记号
- NS 不定义自己的基本列，依赖标准序数算术中的 expand 算符
- BM4 的序数表达能力远超 NS 内部 expand 能处理的序数
