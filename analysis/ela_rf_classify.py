"""
ela_rf_classify.py — pflacco ELA + RandomForest classifier.

v3: 3-way classification (smooth / hybrid / composition).

Class mapping for router decision:
  0 = smooth      (unimodal, basic) → T77 config
  1 = hybrid                         → P_H config
  2 = composition                    → T77 config

Note: Smooth and composition both map to T77 in current router. The 3-way
classifier is more informative for analysis (per-class confusion matrix),
even though deployment routing collapses to binary (T77 vs P_H).

Sampling: scipy.qmc.LatinHypercube (matches MSC basin_detector.py exactly,
enabling lossless Phase-0 reuse at deployment time).

Workflow:
  1. Compute pflacco features on all CEC2017/2020/2022 functions × N seeds
  2. 3-way ground truth mapping
  3. Leave-one-suite-out cross-validation with RandomForest
  4. Report per-class metrics + confusion matrix + binary collapse for routing

Usage:
  python ela_rf_classify.py                              # default: dim=10, M=500, lhs, 3 seeds
  python ela_rf_classify.py --sampler sobol              # Sobol sequence (future)
  python ela_rf_classify.py --sample-size 8500 --seeds 3
  python ela_rf_classify.py --save-features features.csv
  python ela_rf_classify.py --load-features features.csv # skip recomputation
  python ela_rf_classify.py --load-features features.csv --save-model router_rf.pkl

Runtime: ~70s at D=10 M=500 seeds=3 (LHS)
"""
import argparse
import time
import warnings
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

warnings.filterwarnings('ignore')


SUITE_CONFIG = {
    'cec2017': (100.0, 30),
    'cec2020': (100.0, 10),
    'cec2022': (100.0, 12),
}

GROUND_TRUTH = {
    'cec2020': {1: 'unimodal',
                2: 'basic', 3: 'basic', 4: 'basic',
                5: 'hybrid', 6: 'hybrid', 7: 'hybrid',
                8: 'composition', 9: 'composition', 10: 'composition'},
    'cec2017': {**{i: 'unimodal' for i in [1, 2, 3]},
                **{i: 'basic' for i in range(4, 11)},
                **{i: 'hybrid' for i in range(11, 21)},
                **{i: 'composition' for i in range(21, 31)}},
    'cec2022': {1: 'unimodal', 2: 'basic', 3: 'basic', 4: 'basic', 5: 'basic',
                6: 'hybrid', 7: 'hybrid', 8: 'hybrid',
                9: 'composition', 10: 'composition',
                11: 'composition', 12: 'composition'},
}

# 3-way class mapping for router
CLASS_MAP = {
    'unimodal':    0,  # smooth
    'basic':       0,  # smooth
    'hybrid':      1,  # hybrid
    'composition': 2,  # composition
}
CLASS_NAMES = {0: 'smooth', 1: 'hybrid', 2: 'composition'}
ROUTER_CONFIG = {0: 'T77', 1: 'P_H', 2: 'T77'}  # which MSC config to use


# ─────────────────────────────────────────────────────────────────────
# Sampling — MUST match algorithms/basin_detector.py sample_points()
# ─────────────────────────────────────────────────────────────────────
def sample_points_scipy(dim: int, n: int, lb: float, ub: float,
                        seed: int, method: str = 'lhs') -> np.ndarray:
    """
    Identical to algorithms/basin_detector.py::sample_points().
    Uses scipy.stats.qmc to ensure MSC Phase-0 reuse produces identical
    feature values.
    """
    from scipy.stats import qmc

    if method == 'lhs':
        sampler = qmc.LatinHypercube(d=dim, seed=seed)
        unit = sampler.random(n)
    elif method == 'sobol':
        sampler = qmc.Sobol(d=dim, scramble=False)
        unit = sampler.random(n)
    elif method == 'halton':
        sampler = qmc.Halton(d=dim, scramble=False)
        unit = sampler.random(n)
    else:
        raise ValueError(f"Unknown sampling method: {method!r}. "
                         f"Use 'lhs', 'sobol', or 'halton'.")

    lb_arr = np.full(dim, lb)
    ub_arr = np.full(dim, ub)
    return qmc.scale(unit, lb_arr, ub_arr)


def compute_features_one(args_tuple):
    """Compute pflacco features for one (suite, func, seed, sampler)."""
    suite, fnum, dim, M, seed, lb, ub, sampler_method = args_tuple

    import numpy as np
    import pandas as pd
    from pflacco.classical_ela_features import (
        calculate_ela_distribution,
        calculate_ela_meta,
        calculate_dispersion,
        calculate_nbc,
        calculate_information_content,
    )
    from minionpy import (CEC2017Functions, CEC2020Functions, CEC2022Functions)

    cls = {'cec2017': CEC2017Functions, 'cec2020': CEC2020Functions,
           'cec2022': CEC2022Functions}[suite]
    f = cls(fnum, dim)

    X_np = sample_points_scipy(dim, M, lb, ub, seed=seed,
                               method=sampler_method)
    X = pd.DataFrame(X_np, columns=[f'x{i}' for i in range(dim)])
    y = np.array(f(X_np.tolist())).ravel()

    feats = {}
    feats['suite'] = suite
    feats['fnum'] = fnum
    feats['seed'] = seed
    feats['sampler'] = sampler_method

    for fn_name, fn in [
        ('ela_distr', lambda: calculate_ela_distribution(X, y)),
        ('disp', lambda: calculate_dispersion(X, y)),
        ('nbc', lambda: calculate_nbc(X, y)),
        ('ic', lambda: calculate_information_content(X, y, seed=seed)),
        ('ela_meta', lambda: calculate_ela_meta(X, y)),
    ]:
        try:
            result = fn()
            for k, v in result.items():
                if 'costs_runtime' in k:
                    continue
                feats[k] = float(v) if isinstance(v, (int, float, np.integer, np.floating)) else v
        except Exception as e:
            feats[f'{fn_name}_error'] = str(e)

    return feats


def collect_all_features(suites, dim, M, seeds, jobs, sampler_method):
    """Collect features for all suites × functions × seeds in parallel."""
    tasks = []
    for suite in suites:
        bound, nfuncs = SUITE_CONFIG[suite]
        for fnum in range(1, nfuncs + 1):
            for seed in range(seeds):
                tasks.append((suite, fnum, dim, M, seed,
                              -bound, bound, sampler_method))

    print(f"Computing features for {len(tasks)} (suite, func, seed) "
          f"combinations using sampler='{sampler_method}'...")
    results = []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        futures = {ex.submit(compute_features_one, t): t for t in tasks}
        done = 0
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception as e:
                t = futures[fut]
                print(f"  ERROR on {t[0]}/f{t[1]}/seed{t[4]}: {e}")
            done += 1
            if done % 20 == 0:
                print(f"  {done}/{len(tasks)}  ({time.time()-t0:.0f}s)")

    print(f"Feature computation: {time.time()-t0:.1f}s total")
    return pd.DataFrame(results)


def classify_leave_suite_out(df):
    """Leave-one-suite-out RandomForest 3-way classification."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        confusion_matrix,
    )

    def to_class(row):
        gt = GROUND_TRUTH[row['suite']].get(row['fnum'], '?')
        return CLASS_MAP.get(gt, -1)

    df = df.copy()
    df['y_true'] = df.apply(to_class, axis=1)

    non_feat_cols = ['suite', 'fnum', 'seed', 'sampler', 'y_true']
    feat_cols = [c for c in df.columns if c not in non_feat_cols
                 and not c.endswith('_error')
                 and df[c].dtype in [np.float64, np.int64, np.float32, np.int32]]

    X_all = df[feat_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y_all = df['y_true'].values

    sampler_used = df['sampler'].iloc[0] if 'sampler' in df.columns else 'unknown'
    print(f"\nSampler:  {sampler_used}")
    print(f"Features used: {len(feat_cols)}")
    print(f"Samples total: {len(df)}")
    print(f"\nClass distribution:")
    for cls_id, cls_name in CLASS_NAMES.items():
        n = int((y_all == cls_id).sum())
        print(f"  {cls_id} ({cls_name:<12s} → {ROUTER_CONFIG[cls_id]:<3s}): "
              f"{n}/{len(y_all)} ({100*n/len(y_all):.1f}%)")

    suites = sorted(df['suite'].unique())
    all_results = []
    binary_router_results = []

    print("\n" + "=" * 72)
    for held_out in suites:
        train_mask = df['suite'] != held_out
        test_mask = df['suite'] == held_out

        X_train = X_all[train_mask].values
        y_train = y_all[train_mask]
        X_test = X_all[test_mask].values
        y_test = y_all[test_mask]

        rf = RandomForestClassifier(n_estimators=200, max_depth=8,
                                    random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        print(f"\n--- Test on {held_out.upper()} (train on others) ---")
        print(f"  Accuracy:    {acc*100:.1f}%")
        print(f"  F1 (macro):  {f1_macro*100:.1f}%")
        print(f"  F1 (weighted): {f1_weighted*100:.1f}%")

        # Per-class metrics
        for cls_id in [0, 1, 2]:
            cls_mask = y_test == cls_id
            if cls_mask.sum() == 0:
                continue
            cls_recall = (y_pred[cls_mask] == cls_id).sum() / cls_mask.sum()
            pred_mask = y_pred == cls_id
            cls_precision = ((y_test == cls_id) & pred_mask).sum() / max(pred_mask.sum(), 1)
            print(f"    {CLASS_NAMES[cls_id]:<12s} ({ROUTER_CONFIG[cls_id]}): "
                  f"prec={cls_precision*100:>5.1f}%  rec={cls_recall*100:>5.1f}%  "
                  f"n={int(cls_mask.sum())}")

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2])
        print(f"\n  Confusion matrix (rows=truth, cols=predicted):")
        print(f"                pred_smooth  pred_hybrid  pred_compos")
        for cls_id, cls_name in CLASS_NAMES.items():
            row = cm[cls_id]
            print(f"  {cls_name:<12s}    {row[0]:>5d}        {row[1]:>5d}        {row[2]:>5d}")

        # Binary collapse for ROUTER decision (P_H vs T77)
        y_test_router = (y_test == 1).astype(int)
        y_pred_router = (y_pred == 1).astype(int)
        router_acc = accuracy_score(y_test_router, y_pred_router)
        router_prec = precision_score(y_test_router, y_pred_router, zero_division=0)
        router_rec = recall_score(y_test_router, y_pred_router, zero_division=0)
        router_f1 = f1_score(y_test_router, y_pred_router, zero_division=0)

        print(f"\n  Router decision (P_H vs T77):")
        print(f"    Accuracy:  {router_acc*100:.1f}%")
        print(f"    Precision: {router_prec*100:.1f}%  (of predicted P_H, how many really hybrid)")
        print(f"    Recall:    {router_rec*100:.1f}%  (of real hybrid, how many caught)")
        print(f"    F1:        {router_f1*100:.1f}%")

        # Per-function breakdown
        df_test = df[test_mask].copy()
        df_test['y_pred'] = y_pred
        agg = df_test.groupby('fnum').agg(
            truth=('y_true', 'first'),
            pred_mode=('y_pred', lambda s: s.value_counts().index[0]),
            n_seeds=('y_pred', 'count'),
        )
        agg['gt_label'] = [GROUND_TRUTH[held_out].get(f, '?') for f in agg.index]
        agg['truth_name'] = [CLASS_NAMES[t] for t in agg['truth']]
        agg['pred_name'] = [CLASS_NAMES[p] for p in agg['pred_mode']]
        agg['routes_to'] = [ROUTER_CONFIG[p] for p in agg['pred_mode']]

        print(f"\n  Per-function (test on {held_out}):")
        print(f"  {'fnum':<5}{'gt_label':<14}{'truth':<14}{'pred':<14}{'routes':<8}{'correct':<3}{'route':<6}")
        for fnum, row in agg.iterrows():
            correct = '✓' if row['truth'] == row['pred_mode'] else '✗'
            router_correct_truth = ROUTER_CONFIG[int(row['truth'])]
            router_match = '✓' if router_correct_truth == row['routes_to'] else '✗'
            print(f"  f{fnum:<4}{row['gt_label']:<14}{row['truth_name']:<14}"
                  f"{row['pred_name']:<14}{row['routes_to']:<8}{correct:<3}{router_match:<6}")

        # Feature importances
        imp = pd.Series(rf.feature_importances_, index=feat_cols).sort_values(ascending=False)
        print(f"\n  Top-5 features for {held_out} fold:")
        for feat, importance in imp.head(5).items():
            print(f"    {importance:.3f}  {feat}")

        all_results.append({
            'test_suite': held_out,
            'accuracy': acc,
            'f1_macro': f1_macro,
            'f1_weighted': f1_weighted,
        })
        binary_router_results.append({
            'test_suite': held_out,
            'router_accuracy': router_acc,
            'router_precision': router_prec,
            'router_recall': router_rec,
            'router_f1': router_f1,
        })

    print("\n" + "=" * 72)
    print("OVERALL 3-WAY (averaged across leave-one-suite-out folds):")
    for metric in ['accuracy', 'f1_macro', 'f1_weighted']:
        mean = np.mean([r[metric] for r in all_results])
        print(f"  {metric:<14s} {mean*100:.1f}%")

    print("\n" + "=" * 72)
    print("ROUTER DECISION (P_H vs T77) — averaged across folds:")
    for metric in ['router_accuracy', 'router_precision', 'router_recall', 'router_f1']:
        mean = np.mean([r[metric] for r in binary_router_results])
        print(f"  {metric:<20s} {mean*100:.1f}%")
    print("=" * 72)

    return all_results, binary_router_results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dim', type=int, default=10)
    ap.add_argument('--sample-size', type=int, default=None,
                    help="sample size; default = 50*dim")
    ap.add_argument('--seeds', type=int, default=3)
    ap.add_argument('--jobs', type=int, default=15)
    ap.add_argument('--suites', nargs='+',
                    default=['cec2017', 'cec2020', 'cec2022'])
    ap.add_argument('--sampler', choices=['lhs', 'sobol', 'halton'],
                    default='lhs',
                    help="Sampling method; MUST match MSC Phase-0 for "
                         "deployment-time Phase-0 reuse. Default: lhs.")
    ap.add_argument('--save-features', default=None,
                    help="CSV path to save computed features")
    ap.add_argument('--load-features', default=None,
                    help="CSV path to load cached features (skip computation)")
    ap.add_argument('--save-model', default=None,
                    help="Pickle path to save final RF (3-way) trained on ALL data")
    args = ap.parse_args()

    M = args.sample_size or 50 * args.dim
    print(f"=== ELA + RandomForest 3-way classifier ===")
    print(f"D={args.dim}  M={M}  seeds={args.seeds}  "
          f"sampler={args.sampler}  suites={args.suites}")
    print(f"Classes: 0=smooth(unimodal+basic) → T77")
    print(f"         1=hybrid                  → P_H")
    print(f"         2=composition             → T77")

    if args.load_features:
        print(f"\nLoading cached features from {args.load_features}")
        df = pd.read_csv(args.load_features)
        if 'sampler' in df.columns:
            cached_samplers = df['sampler'].unique()
            if len(cached_samplers) > 1:
                print(f"  WARNING: cached file contains multiple samplers: "
                      f"{cached_samplers}")
            elif cached_samplers[0] != args.sampler:
                print(f"  WARNING: cached sampler={cached_samplers[0]!r} "
                      f"differs from requested {args.sampler!r}.")
        else:
            print(f"  WARNING: cached file lacks 'sampler' column.")
    else:
        df = collect_all_features(args.suites, args.dim, M, args.seeds,
                                  args.jobs, args.sampler)
        if args.save_features:
            df.to_csv(args.save_features, index=False)
            print(f"Saved features to {args.save_features}")

    classify_leave_suite_out(df)

    if args.save_model:
        import pickle
        from sklearn.ensemble import RandomForestClassifier

        def to_class(row):
            gt = GROUND_TRUTH[row['suite']].get(row['fnum'], '?')
            return CLASS_MAP.get(gt, -1)

        df2 = df.copy()
        df2['y_true'] = df2.apply(to_class, axis=1)
        non_feat_cols = ['suite', 'fnum', 'seed', 'sampler', 'y_true']
        feat_cols = [c for c in df2.columns if c not in non_feat_cols
                     and not c.endswith('_error')
                     and df2[c].dtype in [np.float64, np.int64,
                                          np.float32, np.int32]]

        X_all = df2[feat_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        y_all = df2['y_true'].values

        rf_final = RandomForestClassifier(n_estimators=200, max_depth=8,
                                          random_state=42, n_jobs=-1)
        rf_final.fit(X_all.values, y_all)

        payload = {
            'rf': rf_final,
            'feature_columns': feat_cols,
            'class_map': CLASS_MAP,
            'class_names': CLASS_NAMES,
            'router_config': ROUTER_CONFIG,
            'sampler': args.sampler,
            'dim': args.dim,
            'sample_size': M,
            'suites_trained_on': args.suites,
            'classifier_type': '3way',
        }
        with open(args.save_model, 'wb') as f:
            pickle.dump(payload, f)
        print(f"\nSaved final 3-way RF model to {args.save_model}")
        print(f"  feature_columns: {len(feat_cols)}")
        print(f"  classes: {CLASS_NAMES}")
        print(f"  router_config: {ROUTER_CONFIG}")


if __name__ == "__main__":
    main()
