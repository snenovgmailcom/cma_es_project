/**
 * nb_tree.cpp — C++ nearest-better tree for MSC-CMA-ES Phase-0.
 *
 * Build:
 *   cd algorithms/cpp
 *   pip install pybind11 --break-system-packages  (if not installed)
 *   c++ -O3 -march=native -shared -std=c++17 -fPIC \
 *       $(python3 -m pybind11 --includes) \
 *       nb_tree.cpp -o nb_tree$(python3-config --extension-suffix)
 *
 * Usage from Python:
 *   from cpp.nb_tree import nearest_better_tree
 *   parent, edge_len = nearest_better_tree(points_norm, fvals, k=1)
 *
 * Algorithm:
 *   For each point i (except global best), find the nearest point j
 *   with f(j) < f(i). Uses a KD-tree with incremental k expansion.
 *   Identical semantics to the Python version in basin_detector.py.
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <limits>

namespace py = pybind11;

// =========================================================================
// Minimal KD-tree (leaf-only, L2 squared, rebuild-free)
// =========================================================================

struct KDTree {
    const double* data;     // (M, D) row-major
    int M, D;
    std::vector<int> idx;   // permuted indices
    std::vector<double> split_val;
    std::vector<int> split_dim;
    std::vector<int> left, right;  // child node indices (-1 = leaf)
    std::vector<int> leaf_start, leaf_end;  // range in idx[]
    int n_nodes = 0;
    static constexpr int LEAF_SIZE = 32;

    KDTree(const double* data, int M, int D) : data(data), M(M), D(D) {
        idx.resize(M);
        std::iota(idx.begin(), idx.end(), 0);
        // Pre-allocate (tree has at most 2*M/LEAF_SIZE nodes)
        int max_nodes = std::max(4 * M / LEAF_SIZE + 4, 64);
        split_val.resize(max_nodes);
        split_dim.resize(max_nodes);
        left.resize(max_nodes, -1);
        right.resize(max_nodes, -1);
        leaf_start.resize(max_nodes, -1);
        leaf_end.resize(max_nodes, -1);
        build(0, M);
    }

    int build(int lo, int hi) {
        int node = n_nodes++;
        if (hi - lo <= LEAF_SIZE) {
            leaf_start[node] = lo;
            leaf_end[node] = hi;
            return node;
        }
        // Find dimension with max spread
        int best_d = 0;
        double best_spread = -1;
        for (int d = 0; d < D; d++) {
            double lo_val = std::numeric_limits<double>::max();
            double hi_val = -std::numeric_limits<double>::max();
            for (int i = lo; i < hi; i++) {
                double v = data[idx[i] * D + d];
                lo_val = std::min(lo_val, v);
                hi_val = std::max(hi_val, v);
            }
            if (hi_val - lo_val > best_spread) {
                best_spread = hi_val - lo_val;
                best_d = d;
            }
        }
        split_dim[node] = best_d;
        int mid = (lo + hi) / 2;
        std::nth_element(idx.begin() + lo, idx.begin() + mid,
                         idx.begin() + hi,
                         [&](int a, int b) {
                             return data[a * D + best_d] < data[b * D + best_d];
                         });
        split_val[node] = data[idx[mid] * D + best_d];
        left[node] = build(lo, mid);
        right[node] = build(mid, hi);
        return node;
    }

    // Find k nearest neighbors of query point q.
    // Returns squared distances and indices.
    void knn(const double* q, int k,
             std::vector<double>& out_dist2,
             std::vector<int>& out_idx) const {
        // Max-heap of (dist2, point_index)
        std::vector<std::pair<double, int>> heap;
        heap.reserve(k + 1);
        double worst = std::numeric_limits<double>::max();
        knn_recurse(0, q, k, heap, worst);
        // Sort by distance
        std::sort(heap.begin(), heap.end());
        out_dist2.resize(heap.size());
        out_idx.resize(heap.size());
        for (size_t i = 0; i < heap.size(); i++) {
            out_dist2[i] = heap[i].first;
            out_idx[i] = heap[i].second;
        }
    }

private:
    void knn_recurse(int node, const double* q, int k,
                     std::vector<std::pair<double, int>>& heap,
                     double& worst) const {
        if (leaf_start[node] >= 0) {
            // Leaf node: check all points
            for (int i = leaf_start[node]; i < leaf_end[node]; i++) {
                int pi = idx[i];
                double d2 = 0;
                for (int d = 0; d < D; d++) {
                    double diff = q[d] - data[pi * D + d];
                    d2 += diff * diff;
                }
                if (d2 < worst || (int)heap.size() < k) {
                    heap.push_back({d2, pi});
                    std::push_heap(heap.begin(), heap.end());
                    if ((int)heap.size() > k) {
                        std::pop_heap(heap.begin(), heap.end());
                        heap.pop_back();
                    }
                    worst = heap.front().first;
                }
            }
            return;
        }
        int sd = split_dim[node];
        double sv = split_val[node];
        double diff = q[sd] - sv;
        int near = diff <= 0 ? left[node] : right[node];
        int far  = diff <= 0 ? right[node] : left[node];
        knn_recurse(near, q, k, heap, worst);
        if (diff * diff < worst || (int)heap.size() < k) {
            knn_recurse(far, q, k, heap, worst);
        }
    }
};

// =========================================================================
// nearest_better_tree — C++ implementation
// =========================================================================

std::pair<py::array_t<int>, py::array_t<double>>
nearest_better_tree(py::array_t<double, py::array::c_style> points_norm,
                    py::array_t<double, py::array::c_style> fvals,
                    int k) {
    auto pts = points_norm.unchecked<2>();
    auto fv  = fvals.unchecked<1>();
    int M = pts.shape(0);
    int D = pts.shape(1);

    // Find global best
    int best = 0;
    for (int i = 1; i < M; i++) {
        if (fv(i) < fv(best)) best = i;
    }

    // Build KD-tree
    KDTree tree(pts.data(0, 0), M, D);

    // Allocate output
    auto parent   = py::array_t<int>(M);
    auto edge_len = py::array_t<double>(M);
    auto par = parent.mutable_unchecked<1>();
    auto elen = edge_len.mutable_unchecked<1>();

    for (int i = 0; i < M; i++) {
        par(i) = -1;
        elen(i) = 0.0;
    }

    int k0 = std::max(2, std::min(k, M - 1));
    int k_cap = std::min(M - 1, std::max({k0, 8 * k0, 256}));

    // For each point, find nearest better neighbor
    std::vector<double> dists2;
    std::vector<int> nbrs;

    for (int i = 0; i < M; i++) {
        if (i == best) continue;
        double fi = fv(i);
        int k_try = k0;

        while (true) {
            int kk = std::min(M, k_try + 1);
            tree.knn(pts.data(i, 0), kk, dists2, nbrs);

            // Find nearest better (excluding self)
            double best_dist = std::numeric_limits<double>::max();
            int best_nbr = -1;

            for (size_t j = 0; j < nbrs.size(); j++) {
                if (nbrs[j] == i) continue;
                if (fv(nbrs[j]) < fi && dists2[j] < best_dist) {
                    best_dist = dists2[j];
                    best_nbr = nbrs[j];
                }
            }

            if (best_nbr >= 0) {
                par(i) = best_nbr;
                elen(i) = std::sqrt(best_dist);
                break;
            }

            if (k_try >= k_cap) {
                // Fallback: connect to global best
                par(i) = best;
                double d2 = 0;
                for (int d = 0; d < D; d++) {
                    double diff = pts(i, d) - pts(best, d);
                    d2 += diff * diff;
                }
                elen(i) = std::sqrt(d2);
                break;
            }
            k_try = std::min(k_cap, 2 * k_try);
        }
    }

    return {parent, edge_len};
}

// =========================================================================
// nbc_clustering — full Phase-0 NB tree + Rule1 + Rule2 + pointer jumping
// =========================================================================

std::tuple<py::array_t<int>,    // labels
           py::array_t<int>,    // parent_raw
           py::array_t<double>, // edge_len_raw
           double>              // mu
nbc_clustering(py::array_t<double, py::array::c_style> points_norm,
               py::array_t<double, py::array::c_style> fvals,
               int k, double phi, double nbc_b, int nbc_min_incoming) {
    auto pts = points_norm.unchecked<2>();
    auto fv  = fvals.unchecked<1>();
    int M = pts.shape(0);

    if (M == 0) {
        return {py::array_t<int>(0), py::array_t<int>(0),
                py::array_t<double>(0), 0.0};
    }

    // 1. Build NB tree
    auto [parent_arr, edge_len_arr] = nearest_better_tree(points_norm, fvals, k);
    auto par_raw = parent_arr.mutable_unchecked<1>();
    auto elen_raw = edge_len_arr.unchecked<1>();

    // Copy raw tree
    auto parent_raw_out = py::array_t<int>(M);
    auto edge_len_raw_out = py::array_t<double>(M);
    auto pr = parent_raw_out.mutable_unchecked<1>();
    auto er = edge_len_raw_out.mutable_unchecked<1>();
    for (int i = 0; i < M; i++) {
        pr(i) = par_raw(i);
        er(i) = elen_raw(i);
    }

    // 2. Compute mu
    double sum_el = 0;
    int count_valid = 0;
    for (int i = 0; i < M; i++) {
        if (par_raw(i) >= 0) {
            sum_el += elen_raw(i);
            count_valid++;
        }
    }
    double mu = count_valid > 0 ? sum_el / count_valid : 0.0;

    // Working copy of parent for cuts
    std::vector<int> parent(M);
    for (int i = 0; i < M; i++) parent[i] = par_raw(i);

    // 3. Rule 1: cut long edges
    if (mu > 0) {
        double threshold = phi * mu;
        for (int i = 0; i < M; i++) {
            if (parent[i] >= 0 && elen_raw(i) > threshold) {
                parent[i] = -1;
            }
        }
    }

    // 4. Rule 2: hub detection
    if (nbc_min_incoming > 0) {
        std::vector<int> indeg(M, 0);
        std::vector<double> sum_incoming(M, 0.0);
        for (int i = 0; i < M; i++) {
            int p = parent[i];
            if (p >= 0) {
                indeg[p]++;
                sum_incoming[p] += elen_raw(i);
            }
        }
        for (int j = 0; j < M; j++) {
            if (indeg[j] >= nbc_min_incoming && parent[j] >= 0) {
                double mean_in = sum_incoming[j] / indeg[j];
                if (mean_in > 0 && elen_raw(j) / mean_in > nbc_b) {
                    parent[j] = -1;
                }
            }
        }
    }

    // 5. Pointer jumping → labels
    std::vector<int> roots(M);
    for (int i = 0; i < M; i++) {
        roots[i] = parent[i] >= 0 ? parent[i] : i;
    }
    int max_iter = (int)std::ceil(std::log2(std::max(M, 2))) + 5;
    for (int iter = 0; iter < max_iter; iter++) {
        bool changed = false;
        for (int i = 0; i < M; i++) {
            int r2 = roots[roots[i]];
            if (r2 != roots[i]) {
                roots[i] = r2;
                changed = true;
            }
        }
        if (!changed) break;
    }

    auto labels = py::array_t<int>(M);
    auto lab = labels.mutable_unchecked<1>();
    for (int i = 0; i < M; i++) lab(i) = roots[i];

    return {labels, parent_raw_out, edge_len_raw_out, mu};
}

// =========================================================================
// Python bindings
// =========================================================================

PYBIND11_MODULE(nb_tree, m) {
    m.doc() = "C++ nearest-better tree for MSC-CMA-ES Phase-0";

    m.def("nearest_better_tree", &nearest_better_tree,
          py::arg("points_norm"), py::arg("fvals"), py::arg("k") = 1,
          "Build NB tree. Returns (parent, edge_len) arrays.");

    m.def("nbc_clustering", &nbc_clustering,
          py::arg("points_norm"), py::arg("fvals"),
          py::arg("k"), py::arg("phi"), py::arg("nbc_b"),
          py::arg("nbc_min_incoming"),
          "Full NBC: NB tree + Rule1 + Rule2 + pointer jumping.\n"
          "Returns (labels, parent_raw, edge_len_raw, mu).");
}
