#!/usr/bin/env python3
"""
compare_to_paper.py — validate our CEC2017 D=10 results against the published
ARRDE paper (arXiv:2511.18429v2, Table A.9), which uses the SAME Minion/minionpy
backend and the SAME budget (Nmax = 1e4*D = 100000) and 51 runs.

For each shared algorithm and function it computes a Welch two-sample z-statistic
on the mean error (both sides n=51, with reported std), and a sign test for a
SYSTEMATIC direction.

Logic:
  - |z| < 2  : statistically consistent (same distribution, seeds differ)
  - 2-3      : borderline
  - > 3      : discrepant (worth a look)
  - Sign test: among non-trivial functions, if our budget were short we would be
    WORSE (higher error) on almost all of them. A ~50/50 split means seed noise.

Usage:
  python compare_to_paper.py exp/experiments/cec2017/d10 --algos ARRDE,jSO,j2020,NLSHADE-RSP
"""

import argparse
import csv
import math
import os

N = 51            # runs both sides
TRIVIAL = 1e-3    # mean error below this counts as "solved" (skip sign test)

# ── Paper Table A.9 (CEC2017 D=10): (mean, std) per function, n=51 ──
# F2 is excluded in the paper.
PAPER = {
 'ARRDE': {
  'f1':(0,0),'f3':(0,0),'f4':(0,0),'f5':(1.951,0.8803),'f6':(0,0),
  'f7':(12.23,0.9684),'f8':(1.814,0.9389),'f9':(0,0),'f10':(104.7,103.9),
  'f11':(0,0),'f12':(14.80,38.39),'f13':(3.584,2.067),'f14':(0.4300,1.831),
  'f15':(0.1596,0.1707),'f16':(0.5969,0.3502),'f17':(3.131,5.288),
  'f18':(0.6308,2.754),'f19':(0.02510,0.02782),'f20':(0.1859,0.2650),
  'f21':(104.7,20.11),'f22':(77.68,31.97),'f23':(283.7,70.95),
  'f24':(98.56,10.16),'f25':(242.4,121.9),'f26':(110.0,99.81),
  'f27':(389.1,0.1945),'f28':(262.2,96.19),'f29':(230.9,8.836),
  'f30':(395.5,6.674),
 },
 'jSO': {
  'f1':(0,0),'f3':(0,0),'f4':(0,0),'f5':(1.697,0.8655),'f6':(0,0),
  'f7':(12.03,0.5637),'f8':(1.717,0.9669),'f9':(0,0),'f10':(56.05,59.31),
  'f11':(0,0),'f12':(0.2673,0.1809),'f13':(0.6149,1.499),'f14':(0.03882,0.1922),
  'f15':(0.3216,0.2027),'f16':(0.5420,0.2484),'f17':(0.4349,0.3787),
  'f18':(0.2592,0.1989),'f19':(0.01137,0.01329),'f20':(0.06686,0.1415),
  'f21':(124.3,43.81),'f22':(100.0,0),'f23':(300.5,1.083),
  'f24':(232.1,110.7),'f25':(406.8,18.04),'f26':(300.0,0),
  'f27':(393.1,1.634),'f28':(305.6,39.34),'f29':(237.2,3.452),
  'f30':(394.5,0.05368),
 },
 'j2020': {
  'f1':(0,0),'f3':(0,0),'f4':(0.1755,0.2220),'f5':(3.305,1.521),'f6':(0,0),
  'f7':(15.02,1.970),'f8':(3.360,1.605),'f9':(0,0),'f10':(109.6,79.31),
  'f11':(1.805,1.646),'f12':(76.17,67.76),'f13':(6.531,2.398),
  'f14':(0.7325,0.6486),'f15':(1.154,0.7781),'f16':(8.234,20.21),
  'f17':(0.4904,0.5376),'f18':(0.6849,0.5906),'f19':(0.1353,0.3283),
  'f20':(0.01039,0.05220),'f21':(97.21,19.68),'f22':(56.94,38.99),
  'f23':(308.5,2.573),'f24':(126.7,55.32),'f25':(300.3,135.3),
  'f26':(166.5,121.9),'f27':(389.9,1.075),'f28':(285.8,73.46),
  'f29':(246.3,8.712),'f30':(633.5,164.3),
 },
 'NLSHADE-RSP': {
  'f1':(0,0),'f3':(0,0),'f4':(2.157e-4,1.391e-3),'f5':(3.556,1.048),'f6':(0,0),
  'f7':(14.44,1.579),'f8':(3.834,1.072),'f9':(0,0),'f10':(99.30,75.40),
  'f11':(0.6022,0.5582),'f12':(144.4,221.3),'f13':(5.042,2.537),
  'f14':(0.2333,0.4197),'f15':(0.1298,0.2770),'f16':(0.4971,0.1752),
  'f17':(0.2025,0.3313),'f18':(0.4278,0.3330),'f19':(0.02706,0.02412),
  'f20':(0,0),'f21':(94.12,23.53),'f22':(36.31,25.99),'f23':(240.9,126.4),
  'f24':(79.63,32.76),'f25':(386.1,57.79),'f26':(37.25,81.56),
  'f27':(383.7,53.99),'f28':(140.0,140.6),'f29':(243.9,12.78),
  'f30':(674.3,189.8),
 },
}


def read_summary(path):
    out = {}
    with open(path, newline='') as fh:
        for row in csv.DictReader(fh):
            out[row['func']] = (float(row['mean']), float(row['std']))
    return out


def welch_z(m1, s1, m2, s2, n=N):
    se = math.sqrt(s1 * s1 / n + s2 * s2 / n)
    d = m1 - m2
    if se < 1e-12:
        if abs(d) < 1e-9:
            return 0.0
        return float('inf')
    return d / se


def compare(algo, our_dir):
    ref = PAPER[algo]
    path = os.path.join(our_dir, algo, 'maxevals_100000', 'summary.csv')
    if not os.path.isfile(path):
        print(f"  [{algo}] missing {path}")
        return
    ours = read_summary(path)

    print(f"\n── {algo} : ours vs ARRDE-paper Table A.9 (CEC2017 D10, 100k) ──")
    print(f"{'func':>5}  {'our mean':>12}  {'paper mean':>12}  {'z':>7}   flag")
    consistent = border = discrepant = 0
    worse = better = 0           # among non-trivial functions
    for func in sorted(ref, key=lambda x: int(x[1:])):
        if func not in ours:
            continue
        om, os_ = ours[func]
        pm, ps = ref[func]
        z = welch_z(om, os_, pm, ps)
        az = abs(z)
        if az == float('inf'):
            flag = 'EXACT-DIFF'; discrepant += 1
        elif az < 2:
            flag = 'ok'; consistent += 1
        elif az < 3:
            flag = 'borderline'; border += 1
        else:
            flag = 'DISCREPANT'; discrepant += 1
        # sign test only where at least one side is non-trivial
        if max(om, pm) > TRIVIAL:
            if om > pm:
                worse += 1
            elif om < pm:
                better += 1
        zs = '  inf' if az == float('inf') else f'{z:6.2f}'
        print(f"{func:>5}  {om:12.4e}  {pm:12.4e}  {zs}   {flag}")

    ntot = consistent + border + discrepant
    print(f"  consistency (|z|): ok {consistent}/{ntot}, "
          f"borderline {border}, discrepant {discrepant}")
    nontriv = worse + better
    if nontriv:
        # binomial tail: P(>= worse | p=0.5) — crude systematic-bias check
        k, n = worse, nontriv
        p_tail = sum(math.comb(n, i) for i in range(k, n + 1)) / (2 ** n)
        print(f"  sign test (non-trivial funcs={nontriv}): ours worse {worse}, "
              f"ours better {better}  |  P(>= that many worse if 50/50) = "
              f"{p_tail:.3f}")
        if p_tail < 0.05:
            print("    → SYSTEMATICALLY worse — would be consistent with a "
                  "short budget / weaker config.")
        else:
            print("    → no systematic direction — consistent with seed-only "
                  "variation (same budget & config).")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('our_dir', help='e.g. exp/experiments/cec2017/d10')
    ap.add_argument('--algos', default='ARRDE,jSO,j2020,NLSHADE-RSP')
    args = ap.parse_args()
    print("Validation: our CEC2017 D10 @100k  vs  ARRDE paper Table A.9 "
          "(same minionpy backend, same budget, 51 runs).")
    for algo in [a.strip() for a in args.algos.split(',') if a.strip()]:
        if algo not in PAPER:
            print(f"\n  [{algo}] not in paper (no reference) — skipped")
            continue
        compare(algo, args.our_dir)


if __name__ == '__main__':
    main()
