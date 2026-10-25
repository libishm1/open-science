"""Shared task queue for a pool of local agents, with escalation between model tiers.

A job starts at tier 0. A worker takes any pending job whose tier is at or below its own.
If the attempt fails, the job moves up one tier. A job is done when it is solved, or when it
fails on the top tier. A single worker with no escalation gives the baseline for comparison.
"""

import threading
import time
from dataclasses import dataclass, field


@dataclass
class Job:
    key: str
    payload: object
    tier: int = 0
    running: bool = False
    done: bool = False
    solved_by: str | None = None
    attempts: list = field(default_factory=list)


def run_queue(jobs: list[Job], tiers: list[str], runner, escalate: bool = True) -> dict:
    """runner(model, job) -> dict with at least 'fixed' and 'rounds'."""
    cond = threading.Condition()
    top = len(tiers) - 1 if escalate else 0
    log: list[dict] = []

    def take(my_tier):
        with cond:
            while True:
                eligible = [j for j in jobs if not j.done and not j.running and j.tier <= my_tier]
                if eligible:
                    eligible[0].running = True
                    return eligible[0]
                if all(j.done for j in jobs):
                    return None
                cond.wait(timeout=1.0)

    def finish(job, model, tier, result):
        with cond:
            job.running = False
            job.attempts.append({"model": model, "tier": tier, "fixed": result["fixed"],
                                 "rounds": result["rounds"]})
            if result["fixed"]:
                job.done, job.solved_by = True, model
            elif tier < top:
                job.tier = tier + 1
            else:
                job.done = True
            cond.notify_all()

    def worker(tier, model):
        while True:
            job = take(tier)
            if job is None:
                return
            t0 = time.time()
            result = runner(model, job)
            log.append({"job": job.key, "model": model, "tier": tier, "fixed": result["fixed"],
                        "rounds": result["rounds"], "seconds": round(time.time() - t0, 1)})
            finish(job, model, tier, result)

    workers = [(i, m) for i, m in enumerate(tiers)] if escalate else [(0, tiers[0])]
    t0 = time.time()
    threads = [threading.Thread(target=worker, args=w) for w in workers]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    solved = sum(1 for j in jobs if j.solved_by)
    return {
        "wall_seconds": round(time.time() - t0, 1),
        "jobs": len(jobs),
        "solved": solved,
        "escalations": sum(1 for j in jobs if len(j.attempts) > 1),
        "solved_by_model": {m: sum(1 for j in jobs if j.solved_by == m) for _, m in workers},
        "per_job": [{"job": j.key, "solved_by": j.solved_by, "attempts": j.attempts} for j in jobs],
        "log": log,
    }
