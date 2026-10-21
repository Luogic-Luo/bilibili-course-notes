# Note conventions

One Markdown file per course, one `##` section per video part, plus three
appendices. Written for an Obsidian vault, but plain Markdown is fine.

## File layout

```
<vault>/<course-slug>.md          the notes
<vault>/<course-slug>-transcripts/ raw ASR transcripts (pNN.txt) + README
```

The transcripts folder is searchable raw material; the notes are the study
artifact. Say where both live when you hand off.

## Per-section structure

```markdown
### 2.3 <part title> (P7)

**<one line naming the exam points of this part, in order>**

1. **<concept name>**
   - definition, terminology table, the properties that get tested
2. **<next concept>**
   - ...
```

Rules that make it study-efficient:

- **Bold the key terms and the numbers.** A reader should be able to skim the
  bold text and still catch the exam-relevant content.
- **Mark the exam weight** of each point: `计算题`, `概念辨析`, `下午题`,
  `送分题`. This is what tells the user where to spend time.
- **Put comparison points in a table** whenever the chapter contrasts two
  things (对称 vs 非对称加密, Prim vs Kruskal, B 树 vs B+ 树). Tables are
  scanned far faster than prose.
- **Give the formula, not just the name** (e.g. `平均访问时间 = 命中时 t1 +
  (1-命中率) x t2`), and say when a formula is frequently asked.
- **Add a one-line memory hook** for anything students routinely get wrong
  ("中序是钥匙，没有中序就定不下来").
- **Use the teacher's own examples** when the transcript has them - concrete
  analogies ("海底捞取号") survive review far better than abstractions.
- Keep the teacher's ordering once the full transcript is available. If a
  section was written from a head transcript plus subject-matter sources, say
  so at the end of the section rather than implying it is a transcript-faithful
  account.

## Worked example (abridged)

```markdown
### 2.3 树和二叉树、图（P7）

**1. 树的基本概念**
- 树是 n（n≥0）个结点的有限集合；**有且仅有一个根结点**；**树是 n 个结点、n−1 条边的图**。
- 术语：**结点的度**（子树个数）、**树的度**（各结点度的最大值）、**叶子结点**（度为 0）…

**2. 二叉树**
- 定义：每个结点**至多有两棵**子树（左右子树有顺序之分）。
- **关键性质（必背）**：
  - 第 i 层最多有 **2^(i−1)** 个结点；深度为 k 的二叉树最多 **2^k − 1** 个结点。
  - **完全二叉树**：n 个结点的完全二叉树**深度 = ⌊log₂n⌋+1**。
  - **任意二叉树中：叶子结点数 n₀ = 双分支结点数 n₂ + 1**（推导常考）。
- **遍历（高频）**：
  - 先序（根左右）、中序（左根右）、后序（左右根）、**层序**。
  - **由遍历序列唯一确定二叉树**：**先序 + 中序 → 唯一确定**；**中序 + 后序 → 唯一确定**；**先序 + 后序 → 不能唯一确定**。**记忆：中序是"钥匙"。**
- **B 树 / B+ 树**：**B 树所有结点都存关键字与记录指针，B+ 树只有叶结点存记录指针、且叶结点串成链表**——这是常考对比题。

**3. 图**
- **最小生成树**（n 个顶点 → n−1 条边）：
  - **Prim 算法**：O(n²)，适合**稠密图**。
  - **Kruskal 算法**：按边权升序加边，**避免成环**（并查集），适合**稀疏图**。
- **最短路径**：**Dijkstra（单源，边权为正）**、**Floyd（各顶点间，允许负权边）**。
```

## Appendices

- **附录 A - 分 P 索引**: table of P / title / duration / link to the section.
  Generate it from the manifest (`scripts/make_scaffold.py` writes a skeleton
  with this table already filled).
- **附录 B - 高频易错点速查**: two lists - calculation-type questions the
  user must drill, and concept pairs that are easy to confuse.
- **附录 C - 复习路线**: an ordered plan derived from the course's own
  weighting, ending with what to skip. Only add this if the course states its
  exam weighting; otherwise keep it generic.

## Self-check before shipping

- Re-read every formula and every "A vs B" claim against the transcript or an
  authoritative source. Drafting from a syllabus produces plausible-sounding
  errors (a real example: "先序 + 后序 uniquely determines a binary tree" -
  false, it needs 中序).
- Check internal consistency: the same fact stated twice in one file must not
  contradict itself.
- Verify every number in a table (durations, sizes, counts) against the
  manifest rather than by eye.
- Verify the markdown renders: no unclosed table rows, no stray backticks.

## Marking which pass a section is based on

Once a section is rewritten from a **full** transcript, it no longer matches the
textbook's ordering. Mark it so the reader knows:

- `### 2.3 树和二叉树、图（P7） 📖 按老师讲（完整转写）` - rewritten from the
  teacher's actual teaching order, with his examples.
- Unmarked sections are still built from the head transcript + syllabus, i.e.
  correct coverage but textbook ordering.

## Mark what the course did NOT cover

Teachers skip material that the textbook includes. Writing it as a normal exam
point overstates the course and misdirects revision time. Put it in a clearly
labelled block at the end of the section instead:

```markdown
> **⚠️ 本节课程未展开、但教材/考纲涉及的内容（自学补充）**
> 老师这节课**没有讲**：**字符编码（ASCII/GBK/UTF-8）**、**IEEE 754 的具体格式**……
> 这些属于教材延伸，**偶尔以选择题出现**；**本节重点是上面 3 个考点**。
```

Verified repeatedly on a 24-part exam course: sections routinely contained
material the teacher never mentioned (shortest path, key path, B-trees, ASCII
encoding, IEEE 754 bit layouts, Huffman-vs-B-tree). Marking the gaps is one of
the highest-value things the transcript gives you - it changes how the user
spends their hours.

## Preserve the teacher's own framing

- Keep his worked examples and analogies (a queue-numbering system for queues
  and algorithms; a 8-node tree used throughout a whole section).
- Keep his formulas, stated as he states them (`单元数 = 末地址 - 首地址 + 1`),
  and keep his "this is how you solve it" shortcuts (the "substitute the
  options" trick for matrices and grammars; "count the loops, +1" instead of
  McCabe's formula).
- Keep his emphasis markers (计算题 / 概念辨析 / 下午题 / 送分题).
- When the teacher states a fact you believe is wrong, write the fact
  correctly and note the discrepancy - do not silently reproduce the error.

## Real-world validation

This pipeline was run end-to-end on a 24-part, 13.5 h exam-prep course
(Bilibili `BV1rc411t71D`, 软考中级软件设计师). Results:

- **Wall time**: ~2 h of CPU on 16 cores for a full 24-part transcription
  (two parallel workers, RTF ~0.3 each). The `head` pass (6 min/part) took
  ~30 min and was enough to build the whole course's outline.
- **Yield**: the transcripts exposed that the teacher skipped large chunks of
  the textbook (shortest path, key path, B-trees, ASCII/GBK encoding, IEEE 754
  layouts, Haskell-style grammars and finite automata were taught; Dijkstra,
  Floyd, key path, max-flow, B/B+ trees, red-black trees, Huffman-vs-B-tree,
  thread scheduling, several scheduling algorithms, SPOLing, virtual memory
  paging details, 4NF/5NF, 2PL, OSI layer-device pairing, subnets and CIDR,
  KMP, BST/AVL, storage allocation, scope and operator precedence were NOT).
  Roughly 30-40% of what a syllabus-derived summary would have asserted was
  never taught. This is the single biggest value the transcript adds.
- **Bugs it caught in the draft notes**: a wrong traversal-uniqueness claim
  ("先序 + 后序 uniquely determines a binary tree" - false), a wrong exam
  structure claim (3 afternoon questions instead of 5), and a chapter whose
  entire subject matter was absent from the course.
- **Extra sections worth carrying**: the teacher gave concrete formulas
  (Cache `t_a = h*t_c + (1-h)*t_m`, `2^k >= n+k+1` for Hamming codes,
  `unit count = end - start + 1`, series/parallel reliability, P/V operations,
  banker's algorithm, page replacement, bitmap indexing, multimedia capacity,
  McCabe cyclomatic complexity), plus exam-taking heuristics (which afternoon
  question is worth what, and the "count the loops, +1" shortcut).

Workflow that worked:

1. `head` pass for all parts -> draft notes from it + the syllabus.
2. `rest` pass in the background.
3. Rewrite each section as its full transcript lands; mark it
   `📖 按老师讲（完整转写）`; add a "course did not cover this" block.
4. Keep the teacher's worked examples and shortcuts; keep his weighting.
5. Refresh a part-index table and a high-frequency/error-prone appendix at the end.
