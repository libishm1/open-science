"""Command line for the local agent workbench.

Commands:
  setup        pull the public skill repositories, optionally import local skills, write config
  doctor       check the environment and print the next command for each gap
  skills       list | find QUERY | show NAME [--section TITLE]
  pdf          extract FILE [-o OUT.md]
  diagram      build SPEC.json [-o OUTDIR]
  review       prisma SCREENING.csv [-o OUT.md]
  loop         run PROJECT [--model M] [--skill NAME]
  queue        run PROJECT_DIR [--pool | --single MODEL] [-o OUT.json]
"""

import argparse
import os
import json
import shutil
import sys
from pathlib import Path

from . import config, diagrams, doctor, pdf, review, skills, sources


def cmd_setup(args) -> int:
    cfg = config.load_config()
    if args.ref:
        for item in args.ref:
            name, _, ref = item.partition("=")
            for src in cfg["sources"]:
                if src["name"] == name:
                    src["ref"] = ref
    config.save_config(cfg)
    ok_all = True
    if args.pull or not config.bundled_skills_dir().is_dir():
        for src in cfg["sources"]:
            ok, msg = sources.sync_source(src)
            ok_all &= ok
            print(msg)
    else:
        print("using the bundled skills (no network needed); use --pull to refresh from the public repositories")
    if args.local_skills:
        imported = import_local(Path(args.local_skills))
        print(f"local skills imported: {imported}")
    print(f"config: {config.config_path()}")
    return 0 if ok_all else 1


def cmd_bundle(args) -> int:
    record = sources.build_bundle()
    print(f"bundled {len(record['skills'])} owned skill(s) from {len(record['sources'])} source(s)")
    for s in record["sources"]:
        print(f"  {s['name']} @ {s['ref']} {s['commit'][:12]}")
    return 0


def import_local(src_dir: Path) -> int:
    """Copy skill folders from a local directory into LAWB_HOME. Nothing is written into the repository."""
    dest = config.local_skills_dir()
    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    for folder in sorted(p for p in src_dir.iterdir() if p.is_dir()):
        if not (folder / "SKILL.md").is_file():
            continue
        target = dest / folder.name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(folder, target, ignore=shutil.ignore_patterns("__pycache__", "node_modules", ".git"))
        count += 1
    return count


def cmd_skills(args) -> int:
    if args.action == "list":
        found = skills.discover()
        for name in sorted(found):
            s = found[name]
            print(f"{name:34s} {s.origin:34s} {s.description[:70]}")
        print(f"{len(found)} skill(s)")
        return 0
    if args.action == "find":
        for s in skills.find(args.query):
            print(f"{s.name}  ({s.origin})")
        return 0
    if args.action == "show":
        found = skills.discover()
        if args.name not in found:
            print(f"no skill named {args.name!r}; try: python -m lawb skills list", file=sys.stderr)
            return 1
        skill = found[args.name]
        print(skill.section(args.section) if args.section else skill.text)
        return 0
    return 2


def cmd_pdf(args) -> int:
    out = Path(args.out) if args.out else None
    md = pdf.extract(Path(args.file), out)
    if not out:
        print(md)
    else:
        print(f"wrote {out}")
    return 0


def cmd_diagram(args) -> int:
    result = diagrams.build(Path(args.spec), Path(args.out))
    for k, v in result.items():
        if v:
            print(f"{k}: {v}")
    return 0


def cmd_review(args) -> int:
    counts = review.prisma(Path(args.csv))
    md = review.to_markdown(counts)
    if args.out:
        Path(args.out).write_text(md, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(md)
    return 0


def _system_prompt(skill_name):
    if not skill_name:
        return None
    found = skills.discover()
    if skill_name not in found:
        raise SystemExit(f"no skill named {skill_name!r}")
    return "Use this skill document. Follow its steps.\n\n=== SKILL ===\n" + found[skill_name].text


def cmd_loop(args) -> int:
    from .llm import RouterClient
    from .pipeline import run_loop
    model = args.model or config.load_config()["models"]["tiers"][-1]
    result = run_loop(Path(args.project), RouterClient(), model, system=_system_prompt(args.skill))
    print(json.dumps({k: v for k, v in result.items() if k != "log"}, indent=2))
    for entry in result["log"]:
        print(entry)
    return 0 if result["fixed"] else 1


def cmd_queue(args) -> int:
    from .llm import RouterClient
    from .pipeline import run_loop
    from .queue import Job, run_queue
    projects = sorted(p for p in Path(args.project_dir).iterdir() if (p / "pipeline.json").is_file())
    if not projects:
        print("no project folders with pipeline.json found", file=sys.stderr)
        return 1
    cfg = config.load_config()
    tiers = cfg["models"]["tiers"] if not args.single else [args.single]
    escalate = not args.single
    system = _system_prompt(args.skill)
    client = RouterClient()
    jobs = [Job(key=p.name, payload=p) for p in projects]

    def runner(model, job):
        return run_loop(job.payload, client, model, system=system)

    result = run_queue(jobs, tiers, runner, escalate=escalate)
    out = Path(args.out) if args.out else Path(args.project_dir) / "queue_result.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"solved {result['solved']}/{result['jobs']} in {result['wall_seconds']}s; "
          f"escalations {result['escalations']}; by model {result['solved_by_model']}")
    print(f"wrote {out}")
    return 0


def cmd_keys(args) -> int:
    from . import secrets
    if args.action == "status":
        for provider, state, detail in secrets.status_rows():
            print(f"{provider.ljust(10)} {state.ljust(8)} {detail}")
        return 0
    if args.action == "set":
        if args.provider not in secrets.ENV_VARS:
            print("provider must be anthropic or openai", file=sys.stderr)
            return 2
        secrets.set_key(args.provider)
        print(f"{args.provider} key stored in the OS credential store. Cloud is enabled.")
        print("Test it with: python -m lawb cloud-check")
        return 0
    if args.action == "delete":
        removed = secrets.delete_key(args.provider)
        print(f"{args.provider} key removed" if removed else f"no {args.provider} key found")
        return 0
    if args.action in ("enable", "disable"):
        secrets.enable_cloud(args.action == "enable")
        print(f"cloud {'enabled' if args.action == 'enable' else 'disabled'}; no network call was made")
        return 0
    return 2


def cmd_cloud_log(args) -> int:
    from . import secrets
    rows = secrets.read_cloud_log(args.limit)
    if not rows:
        print("no cloud calls recorded")
    for r in rows:
        print(f"{r['time']}  {r['provider']:10s} {r['model']}")
    return 0


def cmd_cloud_check(args) -> int:
    """One short live call per provider that has a key. This is the only command that uses the network for cloud."""
    from . import llm, secrets
    ok = True
    for provider in secrets.ENV_VARS:
        key, _ = secrets.get_key(provider)
        if key is None:
            print(f"{provider}: no key; skipped")
            continue
        model = os.environ.get("LAWB_OPENAI_MODEL") if provider == "openai" else "claude-opus-5-5"
        if not model:
            print(f"{provider}: set LAWB_OPENAI_MODEL to a model id on your account, then re-run")
            ok = False
            continue
        try:
            reply = (llm.anthropic_chat(model, "Reply with the single word OK.", None, 16, api_key=key)
                     if provider == "anthropic" else
                     llm.openai_chat(model, "Reply with the single word OK.", None, 16, api_key=key))
            secrets.record_cloud_call(provider, model)
            print(f"{provider}: ok ({model})")
        except Exception as exc:
            print(f"{provider}: failed ({exc.__class__.__name__}); check the key or the model id")
            ok = False
    return 0 if ok else 1


def cmd_models(args) -> int:
    from . import models
    if args.action == "recommend":
        rows = models.recommend(args.task)
        if not rows:
            print(models.load().get("note", "no recommendation"))
            return 1
        have = set(models.installed_models())
        for r in rows:
            mark = "installed" if r["model"] in have else "not installed"
            small = ", ".join(r.get("small", [])) or "-"
            print(f"{r['task']:11s} {r['model']:22s} ({mark})  smaller: {small}")
            print(f"            {r.get('why', '')}")
        return 0
    if args.action == "install":
        if not args.task:
            print("choose --task coding|math|literature|general|all", file=sys.stderr)
            return 2
        for model, status in models.install(args.task, dry_run=args.dry_run):
            print(f"{model:22s} {status}")
        return 0
    return 2


def build_parser():
    ap = argparse.ArgumentParser(prog="lawb", description="Local agent workbench (offline).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("setup", help="pull public skills, optional local import, write config")
    p.add_argument("--ref", action="append", help="override a source ref, NAME=REF (e.g. a branch under review)")
    p.add_argument("--local-skills", help="folder of your own skill folders to import locally")
    p.add_argument("--pull", action="store_true", help="refresh from the public repositories")
    p.set_defaults(fn=cmd_setup)

    p = sub.add_parser("bundle", help="rebuild the bundled skill snapshot from the pulled repositories")
    p.set_defaults(fn=cmd_bundle)

    p = sub.add_parser("doctor", help="check the environment")
    p.set_defaults(fn=lambda a: doctor.print_report())

    p = sub.add_parser("keys", help="store, check or remove cloud API keys (kept in the OS credential store)")
    p.add_argument("action", choices=["set", "status", "delete", "enable", "disable"])
    p.add_argument("provider", nargs="?", choices=["anthropic", "openai"])
    p.set_defaults(fn=cmd_keys)

    p = sub.add_parser("cloud-log", help="show the local record of cloud calls (no prompts or answers)")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(fn=cmd_cloud_log)

    p = sub.add_parser("cloud-check", help="one short live call per provider with a key")
    p.set_defaults(fn=cmd_cloud_check)

    p = sub.add_parser("models", help="recommended local models per task, and one-command install")
    p.add_argument("action", choices=["recommend", "install"])
    p.add_argument("--task", choices=["coding", "math", "literature", "general", "all"])
    p.add_argument("--dry-run", action="store_true", help="show what would be installed")
    p.set_defaults(fn=cmd_models)

    p = sub.add_parser("skills", help="list, find or show skills")
    p.add_argument("action", choices=["list", "find", "show"])
    p.add_argument("query", nargs="?", help="query for find, or skill name for show")
    p.add_argument("--section", help="show one level-2 section only")
    p.set_defaults(fn=lambda a: cmd_skills(argparse.Namespace(action=a.action, query=a.query,
                                                             name=a.query, section=a.section)))

    p = sub.add_parser("pdf", help="extract PDF text to markdown")
    p.add_argument("file")
    p.add_argument("-o", "--out")
    p.set_defaults(fn=cmd_pdf)

    p = sub.add_parser("diagram", help="build a Mermaid diagram from a JSON spec")
    p.add_argument("spec")
    p.add_argument("-o", "--out", default="diagrams")
    p.set_defaults(fn=cmd_diagram)

    p = sub.add_parser("review", help="derive PRISMA counts from a screening CSV")
    p.add_argument("csv")
    p.add_argument("-o", "--out")
    p.set_defaults(fn=cmd_review)

    p = sub.add_parser("loop", help="run the routed error loop on one project")
    p.add_argument("project")
    p.add_argument("--model")
    p.add_argument("--skill", help="skill name to put in the system prompt")
    p.set_defaults(fn=cmd_loop)

    p = sub.add_parser("queue", help="run the loop over a folder of projects with a pool of agents")
    p.add_argument("project_dir")
    p.add_argument("--single", help="run one model only, no escalation (baseline)")
    p.add_argument("--skill")
    p.add_argument("-o", "--out")
    p.set_defaults(fn=cmd_queue)
    return ap


def main(argv=None) -> int:
    # Windows consoles default to cp1252; skill text includes Tamil and symbols such as arrows.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    return args.fn(args)
