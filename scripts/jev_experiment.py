#!/usr/bin/env python3
"""Run the legacy transcript studies (LT01, LT02) against TypeSafe's Jev model.

Jev is a "System One" model: it takes a `state` plus typed questions and returns
a probability distribution over the options of a Choice question. That lets us
read P(secret | transcript) directly instead of sampling free text and parsing it.

Studies:
  J01  transcript reconstruction  (port of LT01)
  J02  transcript ordering effect (port of LT02), crossed with candidate-list order

Usage:
  export TYPESAFE_API_KEY=...
  python3 scripts/jev_experiment.py            # run both studies
  python3 scripts/jev_experiment.py --dry-run  # build + validate requests only

Outputs go to artifacts/run_outputs/jev/<timestamp>/ (see artifacts/README.md).
No third-party dependencies: the documented REST endpoint is called with urllib.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://api.typesafe.ai/v1/systemone"
REPO_ROOT = Path(__file__).resolve().parent.parent

# Toy domain, copied verbatim from notebooks/transcript_conditioning_demo.ipynb.
SECRETS = {
    "cat":       {"mammal": True,  "flies": False, "swims": False, "has_fur": True,  "fish": False, "predator": True,  "pet": True,  "barks": False},
    "dog":       {"mammal": True,  "flies": False, "swims": False, "has_fur": True,  "fish": False, "predator": True,  "pet": True,  "barks": True},
    "eagle":     {"mammal": False, "flies": True,  "swims": False, "has_fur": False, "fish": False, "predator": True,  "pet": False, "barks": False},
    "salmon":    {"mammal": False, "flies": False, "swims": True,  "has_fur": False, "fish": True,  "predator": False, "pet": False, "barks": False},
    "shark":     {"mammal": False, "flies": False, "swims": True,  "has_fur": False, "fish": True,  "predator": True,  "pet": False, "barks": False},
    "crocodile": {"mammal": False, "flies": False, "swims": True,  "has_fur": False, "fish": False, "predator": True,  "pet": False, "barks": False},
}
FEATURE_KEYS = list(next(iter(SECRETS.values())).keys())
QUESTIONS = {
    "mammal": "Is it a mammal?",
    "flies": "Does it fly?",
    "swims": "Does it swim?",
    "has_fur": "Does it have fur?",
    "fish": "Is it a fish?",
    "predator": "Is it a predator?",
    "pet": "Is it commonly kept as a pet?",
    "barks": "Does it bark?",
}

# LT02 setup, also verbatim.
EXPERIMENT_ANIMALS = ["cat", "dog", "eagle", "salmon", "shark"]
TARGET_PAIR = ("salmon", "shark")
QA_TRIPLET = [("mammal", False), ("flies", False), ("swims", True)]

# The contradictory transcript from LT01: mammal + fish + flies matches nothing.
CONTRADICTORY = [("mammal", True), ("fish", True), ("flies", True), ("barks", True)]


def build_transcript(feature_answers: list[tuple[str, bool]]) -> str:
    lines = []
    for feature, answer in feature_answers:
        lines.append(f"User: {QUESTIONS[feature]}")
        lines.append(f"Assistant: {'Yes.' if answer else 'No.'}")
    return "\n".join(lines)


def full_transcript(secret: str) -> list[tuple[str, bool]]:
    return [(f, SECRETS[secret][f]) for f in FEATURE_KEYS]


def feasible_set(feature_answers: list[tuple[str, bool]], candidates: list[str]) -> list[str]:
    return [s for s in candidates if all(SECRETS[s][f] == a for f, a in feature_answers)]


def build_state(candidates: list[str], transcript: str) -> str:
    # Same framing as the legacy build_prompt, minus the trailing "Assistant:" cue,
    # which belongs to a text-completion model rather than a typed question.
    return (
        "You are playing 20 questions. You have secretly chosen one of the following: "
        f"{', '.join(candidates)}.\n"
        "Here is the conversation so far:\n\n"
        f"{transcript}\n\n"
        "User: I give up. What was the secret?"
    )


def build_questions(candidates: list[str]) -> dict:
    # Criteria descriptions are deliberately content-free so they add no feature
    # evidence beyond the transcript. Dict order follows `candidates`.
    return {
        "secret": {
            "type": "choice",
            "instructions": "Which secret did the Assistant choose in this game of 20 questions?",
            "criteria": {c: f"The secret is the {c}." for c in candidates},
        },
        "consistent": {
            "type": "noul",
            "instructions": "Every Assistant answer in the conversation is consistent with at least one of the listed candidates.",
        },
    }


def call_jev(state: str, questions: dict, model: str, api_key: str, retries: int = 4) -> dict:
    body = json.dumps({"state": state, "model": model, "questions": questions}).encode()
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"HTTP {e.code}: {detail}") from e
        except urllib.error.URLError:
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise
    raise AssertionError("unreachable")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def plan_requests(n_reps: int) -> list[dict]:
    """Enumerate every request as a self-describing row; assert the logic first."""
    plan = []
    all_secrets = list(SECRETS)

    # J01: one full 8-question transcript per secret, plus the contradictory one.
    j01_cases = [(s, full_transcript(s)) for s in all_secrets] + [("<contradiction>", CONTRADICTORY)]
    for implied, fa in j01_cases:
        feas = feasible_set(fa, all_secrets)
        assert feas == ([] if implied == "<contradiction>" else [implied]), (implied, feas)
        for rep in range(n_reps):
            plan.append({
                "study": "J01", "implied": implied, "feasible_set": feas,
                "candidates": all_secrets, "list_order_id": "L0",
                "feature_order": [f for f, _ in fa], "feature_answers": fa, "rep": rep,
            })

    # J02: 6 transcript permutations x 2 candidate-list orders.
    list_orders = {"L0": EXPERIMENT_ANIMALS, "L1": list(reversed(EXPERIMENT_ANIMALS))}
    for list_id, candidates in list_orders.items():
        for perm_id, perm in enumerate(itertools.permutations(range(len(QA_TRIPLET)))):
            fa = [QA_TRIPLET[i] for i in perm]
            feas = feasible_set(fa, candidates)
            assert set(feas) == set(TARGET_PAIR), (perm_id, feas)
            for rep in range(n_reps):
                plan.append({
                    "study": "J02", "perm_id": perm_id, "perm_indices": list(perm),
                    "feasible_set": sorted(feas), "candidates": candidates,
                    "list_order_id": list_id, "feature_order": [f for f, _ in fa],
                    "feature_answers": fa, "rep": rep,
                })
    return plan


def summarize(rows: list[dict]) -> str:
    out = []
    j01 = [r for r in rows if r["study"] == "J01" and r["rep"] == 0]
    if j01:
        out.append("## J01 transcript reconstruction (rep 0)\n")
        out.append("| implied | Jev choice | P(implied) | confidence | consistent (noul) | match |")
        out.append("|---|---|---|---|---|---|")
        for r in j01:
            p = r["probabilities"].get(r["implied"], float("nan"))
            match = "n/a" if r["implied"] == "<contradiction>" else ("✓" if r["choice"] == r["implied"] else "✗")
            out.append(f"| {r['implied']} | {r['choice']} | {p:.3f} | {r['confidence']:.3f} | {r['consistent']:.3f} | {match} |")

    j02 = [r for r in rows if r["study"] == "J02"]
    if j02:
        a, b = TARGET_PAIR
        out.append(f"\n## J02 ordering effect: P({a} | {{{a},{b}}}) by permutation\n")
        out.append("| list order | perm | feature order | P_A mean | P_A min..max over reps | choice(s) |")
        out.append("|---|---|---|---|---|---|")
        effect = {}
        for list_id in sorted({r["list_order_id"] for r in j02}):
            means = []
            for perm_id in sorted({r["perm_id"] for r in j02}):
                rs = [r for r in j02 if r["list_order_id"] == list_id and r["perm_id"] == perm_id]
                pa = [r["p_a_given_pair"] for r in rs]
                m = sum(pa) / len(pa)
                means.append(m)
                choices = ",".join(sorted({r["choice"] for r in rs}))
                out.append(f"| {list_id} | {perm_id} | {'→'.join(rs[0]['feature_order'])} | {m:.3f} | {min(pa):.3f}..{max(pa):.3f} | {choices} |")
            effect[list_id] = max(means) - min(means)
        out.append("")
        for list_id, e in effect.items():
            out.append(f"- effect size (max − min mean P_A across perms), {list_id}: **{e:.3f}**")
        reps_spread = max(
            max(r["p_a_given_pair"] for r in j02 if (r["list_order_id"], r["perm_id"]) == k)
            - min(r["p_a_given_pair"] for r in j02 if (r["list_order_id"], r["perm_id"]) == k)
            for k in {(r["list_order_id"], r["perm_id"]) for r in j02}
        )
        out.append(f"- largest within-cell spread across repeated identical calls: {reps_spread:.3f} (API nondeterminism floor)")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="jev-latest")
    ap.add_argument("--reps", type=int, default=3, help="identical repeat calls per cell (checks determinism)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    plan = plan_requests(args.reps)
    n_j01 = sum(p["study"] == "J01" for p in plan)
    print(f"Planned {len(plan)} requests ({n_j01} J01, {len(plan) - n_j01} J02), model={args.model}")

    if args.dry_run:
        ex = plan[-1]
        print(json.dumps({"state": build_state(ex["candidates"], build_transcript(ex["feature_answers"])),
                          "model": args.model, "questions": build_questions(ex["candidates"])}, indent=2))
        return 0

    api_key = os.environ.get("TYPESAFE_API_KEY")
    if not api_key:
        print("TYPESAFE_API_KEY is not set.", file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out or REPO_ROOT / "artifacts" / "run_outputs" / "jev" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "config.json").write_text(json.dumps({
        "model_requested": args.model, "reps": args.reps, "api_url": API_URL,
        "secrets": SECRETS, "questions": QUESTIONS, "experiment_animals": EXPERIMENT_ANIMALS,
        "target_pair": TARGET_PAIR, "qa_triplet": QA_TRIPLET, "contradictory": CONTRADICTORY,
        "question_spec_example": build_questions(EXPERIMENT_ANIMALS),
    }, indent=2))

    rows = []
    a, b = TARGET_PAIR
    with open(out_dir / "runs.jsonl", "w") as f:
        for i, p in enumerate(plan):
            transcript = build_transcript(p["feature_answers"])
            state = build_state(p["candidates"], transcript)
            resp = call_jev(state, build_questions(p["candidates"]), args.model, api_key)
            sec, con = resp["answers"]["secret"], resp["answers"]["consistent"]
            probs = sec["probabilities"]
            pair_mass = probs.get(a, 0.0) + probs.get(b, 0.0)
            row = {
                **{k: v for k, v in p.items() if k != "feature_answers"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model_served": resp.get("model"),
                "transcript_id": _hash(transcript),
                "choice": sec["choice"], "confidence": sec.get("confidence"),
                "probabilities": probs, "consistent": con["noul"],
                "pair_mass": pair_mass,
                "p_a_given_pair": probs.get(a, 0.0) / pair_mass if pair_mass else None,
                "usage": resp.get("usage"),
            }
            rows.append(row)
            f.write(json.dumps(row) + "\n")
            f.flush()
            print(f"[{i + 1}/{len(plan)}] {p['study']} {p.get('implied', p.get('perm_id'))} "
                  f"{p['list_order_id']} r{p['rep']}: {sec['choice']} {json.dumps(probs)}")

    summary = summarize(rows)
    (out_dir / "summary.md").write_text(summary)
    print("\n" + summary)
    print(f"Wrote {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
