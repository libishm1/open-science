# Git and code projects

Default rules for research software, websites and analysis repositories. A project can opt into more autonomy by saying so explicitly in its own `AGENTS.md`, `CLAUDE.md` or `Guardrails.txt`; read those files first in every new project.

## Permission ladder

1. **Read and assess.** "Check the differences but don't change anything; give me insights."
2. **Propose**, with a compatibility check: "tell me if it is incompatible before implementing".
3. **Implement the minimum**: "make only necessary changes to the repo".
4. **Commit and push only on request.**

## Git rules

- Do not push or pull unless asked. Do not change the main branch unless asked; work on a feature branch.
- Use the researcher's configured git identity; never invent one.
- The default branch is `main` from the first push.
- Every commit gets a unique message describing what it did.
- Before committing in a shared worktree, check `git status` for `MM` entries: other people's staged work can ride along. Unstage anything that is not yours.
- Always pause for destructive actions: force-push, `reset --hard`, branch deletion, production data, external messages, spending money and system-wide installs.
- Never commit secrets (see [environment-windows.md](environment-windows.md)).
- Never commit copyrighted full-text papers, purchased books or vendor manuals, in any branch.

## README conventions

- The README header matches the repository name, and so does the HTML document title (so the browser tab shows it).
- The first push includes a README with a one-paragraph summary, features, getting started and controls.
- Update the README before a push only for major new features, setup or controls.

## Working style in code sessions

- Be brief; avoid long summaries and filler.
- Do not compact the context unless asked.
- Plan first for anything non-trivial: "make a plan of execution and research first, then write".
- Add human-in-the-loop test steps and known-bugs documentation every time.
- Keep a living `HANDOFF.md` and, for larger repos, an agent wiki with an index that lets an agent load only the context for its task.

## Deploying static sites

GitHub Pages blank or 404: check Vite `base`, the deploy folder, missing assets, browser cache, and whether Pages is enabled for Actions.
