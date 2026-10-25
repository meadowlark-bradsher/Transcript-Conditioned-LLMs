#!/usr/bin/env python3
"""Test whether J02's ordering effect on Jev exceeds call-to-call noise.

Reads a runs.jsonl written by scripts/jev_experiment.py and reports:
  - two-way ANOVA on P_A = P(salmon | {salmon, shark}): permutation x list order
  - permutation tests that shuffle transcript-permutation labels within each
    list order, for the perm main effect and for the observed effect size
    (max - min cell mean), whose naive value is biased upward by noise alone
  - bootstrap CIs on each list order's effect size
  - whether the per-permutation profile replicates across list orders

Usage:
  python3 analysis/jev_j02_stats.py artifacts/run_outputs/jev/<stamp>/runs.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

N_PERM = 10_000
N_BOOT = 10_000
SEED = 20261025


def load(path: Path) -> pd.DataFrame:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    df = pd.DataFrame(rows)
    df = df[df["study"] == "J02"].copy()
    df["perm"] = df["perm_id"].astype(int)
    df["order"] = df["feature_order"].map(lambda f: "→".join(f))
    return df[["list_order_id", "perm", "order", "rep", "p_a_given_pair", "choice"]].rename(
        columns={"list_order_id": "list", "p_a_given_pair": "pa"}
    )


def effect_size(pa: np.ndarray, perm: np.ndarray) -> float:
    means = np.array([pa[perm == p].mean() for p in np.unique(perm)])
    return float(means.max() - means.min())


def f_stat(pa: np.ndarray, perm: np.ndarray) -> float:
    groups = [pa[perm == p] for p in np.unique(perm)]
    grand = pa.mean()
    k, n = len(groups), len(pa)
    ssb = sum(len(g) * (g.mean() - grand) ** 2 for g in groups)
    ssw = sum(((g - g.mean()) ** 2).sum() for g in groups)
    return (ssb / (k - 1)) / (ssw / (n - k))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", type=Path)
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)
    df = load(args.runs)
    lists = sorted(df["list"].unique())
    out = [f"# J02 noise analysis\n\nSource: `{args.runs}`  \nRows: {len(df)} "
           f"({df.groupby(['list', 'perm']).size().min()} reps per cell)\n"]

    # Cell table.
    cells = df.groupby(["list", "perm", "order"])["pa"].agg(["mean", "std", "count"]).reset_index()
    cells["se"] = cells["std"] / np.sqrt(cells["count"])
    out.append("## Cell means of P_A\n\n| list | perm | feature order | mean | SD | SE | P(choice = salmon) |\n|---|---|---|---|---|---|---|")
    for _, c in cells.iterrows():
        ps = (df[(df["list"] == c["list"]) & (df["perm"] == c["perm"])]["choice"] == "salmon").mean()
        out.append(f"| {c['list']} | {c['perm']} | {c['order']} | {c['mean']:.3f} | {c['std']:.3f} | {c['se']:.3f} | {ps:.2f} |")

    # Two-way ANOVA.
    model = smf.ols("pa ~ C(perm) * C(list)", data=df).fit()
    anova = sm.stats.anova_lm(model, typ=2)
    ss_total = anova["sum_sq"].sum()
    out.append("\n## Two-way ANOVA (P_A ~ perm × list)\n\n| term | df | F | p | η² |\n|---|---|---|---|---|")
    for term, r in anova.iterrows():
        if term == "Residual":
            out.append(f"| residual | {r['df']:.0f} | | | {r['sum_sq'] / ss_total:.3f} |")
        else:
            out.append(f"| {term} | {r['df']:.0f} | {r['F']:.2f} | {r['PR(>F)']:.2g} | {r['sum_sq'] / ss_total:.3f} |")
    out.append(f"\nWithin-cell SD (call-to-call noise): {np.sqrt(model.mse_resid):.4f}")

    # Per-list permutation tests and bootstrap CIs.
    out.append("\n## Ordering effect within each list order\n")
    out.append("Null: shuffle transcript-permutation labels within the list order. "
               "`null mean` is the effect size noise alone produces.\n")
    out.append("| list | effect (max−min) | 95% bootstrap CI | null mean | null 95th pct | p (effect) | F | p (F, permutation) |\n|---|---|---|---|---|---|---|---|")
    profiles = {}
    for lid in lists:
        sub = df[df["list"] == lid]
        pa, perm = sub["pa"].to_numpy(), sub["perm"].to_numpy()
        obs_e, obs_f = effect_size(pa, perm), f_stat(pa, perm)
        null_e, null_f = np.empty(N_PERM), np.empty(N_PERM)
        for i in range(N_PERM):
            sh = rng.permutation(perm)
            null_e[i], null_f[i] = effect_size(pa, sh), f_stat(pa, sh)
        boot = np.empty(N_BOOT)
        for i in range(N_BOOT):
            idx = np.concatenate([rng.choice(np.flatnonzero(perm == p), size=(perm == p).sum()) for p in np.unique(perm)])
            boot[i] = effect_size(pa[idx], perm[idx])
        lo, hi = np.percentile(boot, [2.5, 97.5])
        p_e = (1 + (null_e >= obs_e).sum()) / (1 + N_PERM)
        p_f = (1 + (null_f >= obs_f).sum()) / (1 + N_PERM)
        out.append(f"| {lid} | {obs_e:.3f} | {lo:.3f}..{hi:.3f} | {null_e.mean():.3f} | "
                   f"{np.percentile(null_e, 95):.3f} | {p_e:.4f} | {obs_f:.2f} | {p_f:.4f} |")
        profiles[lid] = sub.groupby("perm")["pa"].mean().sort_index().to_numpy()

    # Does the ordering profile replicate across list orders?
    if len(lists) == 2:
        a, b = profiles[lists[0]], profiles[lists[1]]
        r = float(np.corrcoef(a, b)[0, 1])
        out.append(f"\n## Replication of the per-permutation profile across list orders\n\n"
                   f"Pearson r between {lists[0]} and {lists[1]} cell means over the 6 permutations: **{r:.3f}**  \n"
                   f"Rank of permutations by mean P_A, {lists[0]}: {list(np.argsort(-a))}, {lists[1]}: {list(np.argsort(-b))}")
        means = df.groupby("list")["pa"].mean()
        out.append(f"\nList-order main effect: mean P_A {lists[0]} = {means[lists[0]]:.3f}, {lists[1]} = {means[lists[1]]:.3f}")

    report = "\n".join(out) + "\n"
    dest = args.runs.parent / "stats.md"
    dest.write_text(report)
    print(report)
    print(f"Wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
