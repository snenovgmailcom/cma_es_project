# MSC-fixed_sigma_lambda: joint basin-initialization ablation

This variant tests the combined contribution of basin-dependent initial
step size and population size in MSC-CMA-ES. The statistical report is pending.
The name refers to prescribed initialization rules; sigma0 is still drawn
separately for each topological restart.

For each executed topological restart, replace the two MSC initialization
rules with those used by the public NEA2+ v1.1 (28 September 2016):

$$
\sigma_u=\max\{0.025\sqrt D, Z\},\qquad
Z\sim\mathcal N\bigl(0.05\sqrt D,(0.025\sqrt D)^2\bigr),
$$

$$
\sigma_0=(u-l)\sigma_u,\qquad
\lambda=4+\lfloor3\ln D\rfloor.
$$

The normal draw is clipped at the lower bound, not resampled. NEA2+ uses
unit-cube coordinates; the supported CEC domains have equal width 200, so
the step size passed to MSC's CMA engine is `200 * sigma_u`. The original
basin-dependent sigma floor and population cap do not apply to these
replacement values. Bounds with unequal coordinate widths are rejected.

The runner subclasses `MSC_CMA` and overrides only `_run_cma`, replacing
the two arguments only when `phase == 'topo'`. The full algorithm continues
to own Phase-0 sampling, both NBC rules, staircase selection, small-first
basin ordering, starting points, exclusion, C/B scheduling, sample reuse,
stopping criteria, budget accounting and final refinement. The refinement
initialization rule is inherited; its numerical input may change because
it uses the final sigma of a preceding local search.

A separate `PCG64(SeedSequence([run_seed, 0x4E454132]))` stream supplies
one normal draw per executed topological restart. It does not consume the
MSC jitter RNG or the CMA engine's random stream. This reproduces the
NEA2+ initialization distribution, not its complete random trajectory.
MSC's existing CMA seed policy is inherited, including its seed-zero
behavior. This is an MSC ablation, not another implementation of NEA2+.

## Run

The first comparison uses the existing ablation setting: CEC2017, D=10,
100,000 nominal evaluations, 51 runs with logical seeds 0 through 50,
and all 29 valid functions (`f2` excluded).

From the repository root, with the benchmark environment active:

```bash
python ablations/benchmark/msc_fixed_sigma_lambda_ablation.py \
  --suite cec2017 --dim 10 --maxevals 100000 --runs 51 --jobs 51
```

For SLURM, from the same directory and active environment:

```bash
sbatch --job-name=msc-fixed-sigma-lambda --nodes=1 --ntasks=1 \
  --cpus-per-task=51 --export=ALL --output=msc-fixed-sigma-lambda-%j.log \
  --wrap='env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python -u ablations/benchmark/msc_fixed_sigma_lambda_ablation.py --suite cec2017 --dim 10 --maxevals 100000 --runs 51 --jobs 51'
```

`--functions` optionally selects comma-separated function numbers.
The runner also supports CEC2014, CEC2020 and CEC2022 with explicit
dimensions and budgets, or the project's existing suite budget defaults.
Existing result files are protected unless `--force` is specified.

## Recorded data and interpretation

Output directory:

```text
ablations/experiments/cec2017/d10/MSC-fixed_sigma_lambda/maxevals_100000/
```

Each PKL has `algorithm='MSC-fixed_sigma_lambda'`, raw terminal errors, improvements,
cycle summaries, pre-refinement errors and evaluation counts in the same
schema as the other ablations. `params['local_searches_per_seed']` stores
actual sigma0, population, final sigma, evaluation count, error and stop
reason for every local search, including refinement; outer indices match
`seeds`. The initialization formula, coordinate width and RNG policy are
also recorded. The existing FULL MSC batch-end budget convention is
preserved, with actual counts in `nfev_total_per_seed`.

The comparison tests sigma0 and lambda jointly. It does not identify their
separate effects or by itself explain the entire MSC-versus-NEA2+ gap.
Use the existing FULL MSC results as the reference; the common seed labels
do not justify a paired statistical test.

Source implementation of the replacement rules:
[`benchmark/nea2plus.py`](../../benchmark/nea2plus.py).
Runner: [`msc_fixed_sigma_lambda_ablation.py`](../benchmark/msc_fixed_sigma_lambda_ablation.py).

## Rename existing results

For runs previously saved as `NEA2-INIT`, execute from the repository root:

```bash
python analysis/rename_msc_fixed_sigma_lambda.py --apply
```

The migration renames result directories, PKL algorithm metadata and comparison
links. The recorded objective values, seeds and optimization histories are
preserved. Without `--apply`, the script previews the migration.
