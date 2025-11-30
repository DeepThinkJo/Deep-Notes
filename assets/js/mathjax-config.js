// assets/js/mathjax-config.js

window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    macros: {
      // Basic Sets
      N: "\\mathbb{N}",
      Z: "\\mathbb{Z}",
      Q: "\\mathbb{Q}",
      R: "\\mathbb{R}",
      C: "\\mathbb{C}",
      F: "\\mathbb{F}",

      set: ["\\left\\{\\,#1\\,\\right\\}", 1],
      suchthat: "\\;\\middle|\\;",

      // Vectors / Matrices
      vect: ["\\mathbf{#1}", 1],
      mat:  ["\\mathbf{#1}", 1],
      vec:  ["\\mathbf{#1}", 1],
      T: "^{\\mathsf{T}}",
      trans: "^{\\mathsf{T}}",
      inv: "^{-1}",
      evec: ["\\mathbf{e}_{#1}", 1],

      // Subspace Operators
      Span:  "\\operatorname{Span}",
      Ker:   "\\operatorname{Ker}",
      Range: "\\operatorname{Range}",
      Nul:   "\\operatorname{Nul}",
      Col:   "\\operatorname{Col}",
      Row:   "\\operatorname{Row}",
      Null:  "\\operatorname{Nul}",
      nullity: "\\operatorname{nullity}",
      rank:    "\\operatorname{rank}",

      // Other linear algebra
      diag: "\\operatorname{diag}",
      tr:   "\\operatorname{tr}",
      inner: ["\\left\\langle #1, #2 \\right\\rangle", 2],
      norm:  ["\\left\\lVert #1 \\right\\rVert", 1],
      abs:   ["\\left\\lvert #1 \\right\\rvert", 1],

      // Calculus
      ddx: "\\frac{\\mathrm{d}}{\\mathrm{d}x}",
      ddy: ["\\frac{\\mathrm{d}}{\\mathrm{d}#1}", 1],
      pdx: "\\frac{\\partial}{\\partial x}",
      pdy: "\\frac{\\partial}{\\partial y}",
      pd:  ["\\frac{\\partial #1}{\\partial #2}", 2],

      grad: "\\nabla",
      divergence: "\\operatorname{div}",
      curl: "\\operatorname{curl}",

      // Probability
      Prob: "\\mathbb{P}",
      E:    "\\mathbb{E}",
      Var:  "\\operatorname{Var}",
      Cov:  "\\operatorname{Cov}",
      Corr: "\\operatorname{Corr}",
      indep: "\\perp\\!\\!\\!\\perp",
      rv:   ["\\mathsf{#1}", 1],

      // Misc
      id:    "\\operatorname{id}",
      dom:   "\\operatorname{dom}",
      codom: "\\operatorname{codom}",
      Rnn:   "\\mathbb{R}^{n \\times n}",
      Rmn:   "\\mathbb{R}^{m \\times n}",
      GL:    "\\operatorname{GL}",
      Sym:   "\\operatorname{Sym}",
      defeq: "\\vcentcolon=",
      eqdef: "=\\vcentcolon",
      st:    "\\;\\text{s.t.}\\;",
      eps:   "\\varepsilon",

      argmin: "\\mathop{\\operatorname*{arg\\,min}}",
      argmax: "\\mathop{\\operatorname*{arg\\,max}}",

      important: ["\\mathbf{#1}", 1],
      term:      ["\\mathit{#1}", 1]
    }
  },
  svg: {
    fontCache: 'global'
  }
};
