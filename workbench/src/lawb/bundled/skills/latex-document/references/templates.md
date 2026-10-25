# LaTeX templates

Part of the latex-document skill. Copy one skeleton into `main.tex`.

## Article (journal or conference paper)

```latex
\documentclass[11pt]{article}
\usepackage[margin=2.5cm]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{siunitx}
\usepackage{amsmath, amssymb}
\usepackage[hidelinks]{hyperref}
\usepackage[numbers]{natbib}

\title{Title of the paper}
\author{First Author \and Second Author}
\date{}

\begin{document}
\maketitle

\begin{abstract}
One paragraph: problem, method, result, meaning.
\end{abstract}

\section{Introduction}
State the problem and the contribution.

\section{Method}
\begin{figure}[t]
  \centering
  \includegraphics[width=0.8\linewidth]{figures/overview.pdf}
  \caption{What the figure shows, in one sentence.}
  \label{fig:overview}
\end{figure}
Figure~\ref{fig:overview} shows the pipeline.

\section{Results}
\begin{table}[t]
  \centering
  \caption{Results.}
  \label{tab:results}
  \begin{tabular}{lS[table-format=2.1]}
    \toprule
    Case & {Value (\si{\milli\metre})} \\
    \midrule
    A & 12.3 \\
    B & 4.5 \\
    \bottomrule
  \end{tabular}
\end{table}

\section{Conclusion}

\bibliographystyle{plainnat}
\bibliography{references}
\end{document}
```

## Report

Use `\documentclass[11pt]{report}` and `\chapter{...}` for top-level parts. Add `\tableofcontents`
after `\maketitle`.

## Letter

```latex
\documentclass[11pt]{letter}
\signature{Your Name}
\address{Street \\ City}
\begin{document}
\begin{letter}{Recipient \\ Organisation \\ Address}
\opening{Dear Recipient,}
Body text.
\closing{Yours sincerely,}
\end{letter}
\end{document}
```
