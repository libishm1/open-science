# Lean and Mathlib pitfalls

Part of the lean-verification skill. Load this file when a proof step fails for no obvious reason.

| Symptom | Likely cause | Fix |
|---|---|---|
| A lemma you need "does not exist" | It exists under another name | Search Mathlib with `exact?`, `apply?`, or by keyword in the docs before writing it |
| Inner product notation does not parse | Wrong bracket characters | Use the Mathlib notation `⟪x, y⟫` with the scope open |
| Docstring error at the top of a file | Docstring placed before the imports | Put module docstrings after the `import` lines |
| Extended non-negative reals behave oddly | `ℝ≥0∞` arithmetic needs its scope and lemmas | Open the `ENNReal` scope and use its lemmas; avoid mixing with `ℝ` casts carelessly |
| `rw` fails after `h ▸` | Motive cannot be inferred | Rewrite with `rw [h]` first, or use `subst` |
| A variable disappears after `rcases` | Pattern eliminated it by substitution | Name it in the pattern, or use `obtain ⟨x, hx, rfl⟩` deliberately |
| `omega` fails on something linear | A `set` or local definition hides the term | Unfold or `simp only` the definition before `omega` |
| Rational identity resists `ring` | Division needs non-zero facts | `field_simp` often closes it alone; supply the non-zero hypotheses |
| Build is slow after small edits | Large files recompile | Split files by topic; keep heavy imports out of small files |

General habits:

- Build after every few lines. Errors far from their cause cost the most time.
- Keep statements small and named. Combine them in a final theorem.
- Record each trap you hit in the progress log, so the next session avoids it.
