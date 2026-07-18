# TraceMark AI 📝

> **项目理念**：这是一个专注于 **AI 分析记号** 的智能体项目。
> 本项目旨在通过轻量级文件结构，记录 AI 在分析过程中产生的逻辑记号、决策痕迹与数据快照。

## 📂 项目结构 (Structure)

| 文件/文件夹 | 说明 |
| :--- | :--- |
| `MEMORY.md` | **记忆文档**。存放长期积累的“记号”与上下文，位于根目录。 |
| `ANALYSIS.md` | **分析表**。Markdown 格式的实时分析表格与推理过程。 |
| `programs/` | **执行器目录**。存放处理逻辑的脚本（英文命名）。 |
| `README.md` | **总览日志**。本项目最重要的文档，**永不覆盖，只做追加**。 |

## 🎯 工作流 (Workflow)

1.  **读取记号**：从 `MEMORY.md` 加载历史分析记号。
2.  **执行分析**：在 `ANALYSIS.md` 中更新当前的分析表。
3.  **运行程序**：调用 `programs/` 中的脚本进行数据处理。
4.  **沉淀记录**：将结果作为新的“记号”追加到本文件底部。

## 📜 更新日志 (Changelog)

*遵循“只追加，不修改”原则，保留所有历史痕迹。*

### [2026-05-03]
- **项目启动**：确立 "AI 分析记号" 为核心目标。
- **结构设计**：确认使用 `MEMORY.md` 作为单一记忆源。
- **规范制定**：`README.md` 采用持续追加模式，避免重写。

---
### [Future Date]
- （在此处添加新的分析记号...）
# Ns(Nonlinear successo,by 1:送到本到(UTF-8) 2:nnc )
## 1.定义
### 1.1 辅助函数
$$ f(\alpha) = \begin{cases}
  1 & \alpha = 0 \\
  f(\beta)*2 & \alpha = \beta + 1 \\
  f(expand(\alpha,2)) & \lnot\exists \beta ( \alpha = \beta + 1) \\
\end{cases} (\alpha\in On)$$
### 1.2 定义
对于 $ \forall A(||A||\ge\aleph_0) $:
  1. $\alpha\,th\,A\in A $ 
  2. $1\,st,A =min A$
  3. $\alpha\,th\,A = min\{x \mid x > max\{\beta\,th\,A\mid \beta <\alpha \} \land x \in A\}$
   
对于$\mathbb{NS}$:
  1. $1\,th,\mathbb{NS} = 0$
  2. $\alpha+1\,th\,\mathbb{NS} = \alpha\,th\,\mathbb{NS}+\frac{1}{f(\alpha)}$
  3. $\alpha\,th\,\mathbb{NS} = lim_{n\to\omega} expand(\alpha,n) \,th\,\mathbb{NS} ,\lnot\exists \beta ( \alpha = \beta +1)$ 
  <!-- expand(\alpha,n) 即 \alpha[n]  --->
  <!-- 主体 -->
对于 $\psi(x) $:
  1. $ \psi(x) th\, \mathbb{NS} =x   $
# BM4
可用展开器`.\Program\expansion_tool.exe`
## 1.定义
合法矩阵（不一定标准型）满足：
1. 首列全 $0$：$S_{0,y}=0$；
2. 每列自上而下非增：$S_{x,y}\ge S_{x,y+1}$；
3. 同行不超前超 $1$：$S_{x,y}\le \max_{p<x}S_{p,y}+1$（空最大值为 $0$）。
极限表达式为$,(0),(0)(1),(0)(1,1),(0)(1,1,1),\dots$
## 2.展开
### 2.1 辅助函数
1. **父项** $p_k(m)$：取满足
   $$S_{p,k}<S_{m,k}\quad\text{且（}k>0\text{ 时）}\quad a_{k-1,m}(p)=1$$
   的最大 $p<m$。其中 $a_{k-1,m}(p)=1\iff\exists c\ge0:(p_{k-1})^c(m)=p$（列 $p$ 是列 $m$ 在 $k-1$ 行下的祖先）。约定 $(p_k)^0(m)=m$。
2. **上升度** $a_{k,m}(t)$：对坏部第 $m$ 列（$t$ 为坏根列标），
   $$a_{k,m}(t)=\begin{cases}1,& \exists c\ge0:(p_k)^c(m)=t\\0,& \text{否则}\end{cases}$$
3. **坏根** $r=p_z(X-1)$（末列 LNZ 的父项）；末列全 $0$ 则无坏根。
4. **好部 / 坏部**：$G=S_0+\cdots+S_{r-1}$，$B=S_r+\cdots+S_{X-2}$。
5. **阶差** $\Delta_k=\begin{cases}S_{X-1,k}-S_{r,k},& k<z\\0,& k\ge z\end{cases}$。
6. **副本** $B^{(i)}$ 第 $m$ 列：$B^{(i)}_{m,k}=B_{m,k}+a_{k,r+m}(r)\cdot\Delta_k\cdot i$。
### 2.2 expand 函数
$$
\begin{aligned}
\mathit{expand}((),n)&=n\\
\mathit{expand}(S+(0),n)&=\mathit{expand}(S,2n)\\
\mathit{expand}(S,n)&=\mathit{expand}\bigl(G+B^{(0)}+\cdots+B^{(n)},\;2n\bigr)\quad(\text{末列非全 }0)
\end{aligned}
$$
基本列前驱 $FS_n(S)=G+B^{(0)}+\cdots+B^{(n-1)}$。序数映射：
$$
\mathit{Trans}()=0,\quad \mathit{Trans}(S+(0,\dots,0))=\mathit{Trans}(S)+1,\quad \mathit{Trans}(M)=\sup\{\mathit{Trans}(FS_i(M))\mid i\in\mathbb N\}.
$$

---

### [2026-07-18]
- **分析启动**：NS vs BM4 对比分析。AI 通过 `expansion_tool.exe` 探索 BM4 基本列，手算 NS 定义。
- **BM4 基本列模式**：归纳为线性增长（如 `(0)(1)`→`(0)^n`）、周期重复（如 `(0)(1)(2)(1)`→`(0)(1)(2)` 块重复）、交错模式（如 `(0)(1,1)(2,1)`→`(2k)(2k+1,1)`）三类。
- **BM4 等价性发现**：`(0)(a₁,a₂,...) = (0,0)(a₁,a₂,...)`——前置 0 行不改变序数值。
- **BM4 排序**：`(0) < (0)(0) < (0)(1) < (0)(1)(2) < (0)(1,1) < (0)(1,1)(2) < (0)(1,1)(2,1) < (0)(1,1,1) < (0,0,0)(1,1,1)(2,2,0)`。
- **NS 数值计算**：S(1)=0, S(2)=1/2, S(n)=1-1/2^(n-1), S(ω)=1, S(ω·k)=1+Σ2/4^j, S(ω²)=5/3。
- **核心规律**：f(α) 在后继翻倍、在极限取 f(expand(α,2))；NS 非线性步长 = 1/f(α)。
- **对比结论**：NS 是"序数→实数"映射（依赖标准序数基本列），BM4 是自含基本列系统的"矩阵→序数"记号。两者性质不同，BM4 表达能力远超 NS 内部 expand 算符。
