# `analysis/` — Tables and figures

Scripts that turn the `experiments/` result tree
(`<suite>/d<dim>/<ALGO>/maxevals_<N>/{fK.pkl, summary.csv}`) into the tables and
figures of the paper. Run from the repository root.

## Module map

| File | Produces |
|---|---|
| `summary_grid_clean.py` | Per-dimension and per-class summed totals — SUM(mean), SUM(median), SUM(FBTC) — over a common cell set, with partial-coverage warnings. The per-dimension / per-class result tables. |
| `summary_grid.py` | Earlier/raw version of the summed grid (SUM(FBTC) plus per-target hit counts THR_k). |
| `compare.py` | Per-function significance versus a reference algorithm: Wilcoxon signed-rank with Benjamini–Hochberg FDR (`* = significantly better than the reference`). |
| `budget_slopes.py` | Per-function low-vs-high-budget slope panel for one (suite, dim, function class). |
| `fig_budget_slopes.py` | The composed multi-panel budget-slope figure (e.g. MSC-CMA-ES vs BIPOP-CMA-ES vs the best DE baseline). |
| `class_rank_figures.py` | Two publication figures: mean (Friedman-style) rank per algorithm, and a per-class heatmap of where the profile holds. |
| `make_cell_readme.py` | Regenerates the by-category `README.md` of a single result cell from its `.pkl` files. |
| `__init__.py` | Package marker. |

`FBTC` = fixed-budget target coverage: the mean per-target success rate over 51
log-uniformly spaced targets in `[1e-8, 1e+2]`, summed over the functions of a
class or dimension.

## Usage

The exact flags differ per script; pass `--help` to any of them. Representative
calls:

**Summed tables (per-dimension / per-class):**

```bash
python analysis/summary_grid_clean.py --csv <combined_summary.csv>
python analysis/summary_grid.py       --csv <combined_summary.csv>
```

**Per-function significance vs a reference (e.g. MSC-CMA-ES):**

```bash
python analysis/compare.py --help     # base directory, reference algo, metric, alpha
```

**Budget-slope figures:**

```bash
# single (suite, dim, class) panel
python analysis/budget_slopes.py --suite cec2017 --dim 10 \
    --low 100000 --high 1000000 --metric median --func-class composition --out figs

# composed multi-panel figure (the version used in the paper)
python analysis/fig_budget_slopes.py --suite cec2017 --dim 10 \
    --b-lo 100000 --b-hi 1000000 --algos MSC-CMA,BIPOP-CMA \
    --func-class composition --official 100000 --out figures/slopes_cec2017_d10.png
```

**Per-class rank / heatmap figures:**

```bash
python analysis/class_rank_figures.py --metric mean --out figs
```

**Regenerate a cell's README from its pkls:**

```bash
python analysis/make_cell_readme.py --base-dir experiments/cec2020/d5/MSC-CMA \
    --maxevals 50000
```

## Inputs and outputs

- **Inputs:** the per-cell results under `experiments/` (the `.pkl` per-seed
  errors and the `summary.csv` aggregates). The grid scripts read a combined
  CSV via `--csv`; the figure scripts read the `experiments/` tree directly via
  `--root` (default `experiments`).
- **Outputs:** the table scripts print to stdout; the figure scripts save PNGs
  (default directory `figs/`, or an explicit `--out` path).