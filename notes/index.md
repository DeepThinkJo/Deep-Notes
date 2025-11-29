# Deep Notes

Welcome to **Deep Notes – DeepThinkJo**.

Deep Notes is my personal, textbook-style knowledge base.  
It collects concise, carefully curated notes on:

- **Mathematics**
- **Computer Science**
- **Artificial Intelligence**

Each note is written not as a casual memo, but as a *mini textbook page*:  
formal structure first, then my own explanations and intuitions.

---

## 1. What is Deep Notes?

Deep Notes is a long-term project with three main goals:

1. **Rebuild core concepts in my own words**  
   Especially for Mathematics, I write definitions, theorems, and proofs in LaTeX,  
   then add my own commentary under each block.

2. **Keep everything version-controlled and reproducible**  
   Notes are written in Notion, synced automatically to GitHub as Markdown,  
   and published here via MkDocs + GitHub Pages.

3. **Expose my learning process publicly**  
   Anyone (including future me) can browse, search, and build on top of this knowledge.

---

## 2. How to Use This Site

Use the navigation to browse by category:

- **Mathematics**  
  - Textbook-style notes with formal Definition / Theorem / Proof blocks.  
  - Each block is followed by my own explanation in plain language.

- **Computer Science**  
  - Programming, data structures, algorithms.  
  - Conceptual explanations, pseudocode, and sometimes implementations.

- **Artificial Intelligence**  
  - Machine Learning and Deep Learning concepts.  
  - Focus on mechanisms, math behind models, and practical intuition.

Each note follows a consistent internal structure:

1. **Overview** – Why this concept matters and where it appears.  
2. **Key Concepts** – Core definitions, ideas, and objects.  
3. **Main Content** – Detailed explanations, derivations, examples, and proofs.  
4. **Summary** – Final recap and future review points.

---

## 3. Structure of the Notes

### 3.1 Mathematics

Mathematics notes are written in a textbook-like style.

- Formal **Definition / Theorem / Lemma / Corollary / Proof** blocks (using LaTeX)
- Below each block there is a short **“Your Explanation”** section  
  where I restate the idea in my own words and intuition.

Typical topics include:

- Linear Algebra (vector spaces, linear transformations, matrices, eigenvalues, …)  
- Calculus (limits, derivatives, integrals, series, …)  
- Probability and Statistics (random variables, distributions, estimators, …)

Conceptually, a page often looks like this:

```text
Definition
  -> my explanation

Theorem
  -> my explanation

Proof
  -> proof intuition

Example
  -> my interpretation


---

# ✅ **Part 3/4 — Structure of Notes (CS & AI)**

```markdown
---

### 3.2 Computer Science

CS notes focus on:

- Data structures and algorithms  
- Complexity and invariants  
- Implementation details (mainly Python, sometimes C)

Typical content includes:

- Problem definition  
- Algorithm idea and pseudocode  
- Complexity analysis  
- Sample implementation  
- My own explanation of *why it works* and *how to think about it*.

---

### 3.3 Artificial Intelligence

AI notes are centered around:

- Machine learning concepts (loss functions, optimization, regularization, …)  
- Deep learning architectures (MLP, CNN, RNN, Transformer, …)  
- Training dynamics and practical tricks.

Each AI note usually contains:

- Intuitive description of the model or method  
- Mathematical formulation (when needed)  
- Mechanism / forward–backward process  
- Example or simple experiment idea  
- Summary of when to use it and why.

---

## 4. Workflow: From Notion to This Site

The content on this site is not written directly in Markdown.

Instead, the workflow is:

1. I write notes in **Notion**, inside a structured database.  
2. A **sync script** reads the Notion database via API and exports pages as Markdown.  
3. The Markdown files are stored in the `notes/` folder of the **Deep_Notes** repository.  
4. **MkDocs** builds this site from those Markdown files.  
5. GitHub Actions automatically deploys the site to GitHub Pages.

This means:

- Every note here has a corresponding Notion page.  
- Updates in Notion eventually propagate here.  
- Everything is version-controlled and open.

---

## 5. Roadmap

This project is still evolving. Planned improvements include:

- Better navigation by topic and difficulty level  
- A consistent style for all mathematics notes  
- More examples and diagrams for abstract concepts  
- Improved theming and typography (e.g. MkDocs Material)  
- Search and SEO tuning for easier discovery

---

## 6. About DeepThinkJo

I am **DeepThinkJo (조승환)**,  
a learner aiming to become an AI engineer and researcher.

Deep Notes is my way of:

- Thinking slowly and precisely about core ideas  
- Making my learning process transparent  
- Building a personal reference that I can trust and reuse

If you are reading this, you are welcome to explore, learn, and build on these notes.
