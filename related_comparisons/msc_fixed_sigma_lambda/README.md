# MSC-CMA vs MSC-fixed_sigma_lambda

MSC-fixed_sigma_lambda is an ablation of MSC-CMA in which basin-dependent initialization of σ₀ and λ is replaced by the NEA2+ rules: a dimension-dependent random initial step size and λ = 4 + ⌊3 ln D⌋.

**CEC2017 · D = 10 · Budget = 100,000 evaluations · 51 runs per function · f2 excluded.**

## Median terminal error ↓

| Function | MSC-CMA | MSC-fixed_sigma_lambda |
|:--|--:|--:|
| f1 | 2.374e-08 | **0.000e+00** |
| f3 | 0.000e+00 | 0.000e+00 |
| f4 | 0.000e+00 | 0.000e+00 |
| f5 | **1.990e+00** | 4.975e+00 |
| f6 | **5.453e-03** | 8.791e-03 |
| f7 | 1.126e+01 | **9.586e+00** |
| f8 | **9.950e-01** | 3.980e+00 |
| f9 | 0.000e+00 | 0.000e+00 |
| f10 | **1.853e+01** | 1.468e+02 |
| f11 | **0.000e+00** | 2.985e+00 |
| f12 | **1.296e+02** | 1.298e+02 |
| f13 | **6.526e+00** | 6.765e+00 |
| f14 | **9.957e-01** | 2.287e+01 |
| f15 | **1.639e+00** | 3.383e+00 |
| f16 | 1.852e+00 | **1.850e+00** |
| f17 | **2.137e+01** | 2.364e+01 |
| f18 | **2.059e+01** | 2.217e+01 |
| f19 | **2.449e+00** | 4.726e+00 |
| f20 | **1.723e+01** | 2.261e+01 |
| f21 | 1.000e+02 | 1.000e+02 |
| f22 | **1.140e+01** | 1.686e+01 |
| f23 | 3.053e+02 | **3.040e+02** |
| f24 | 1.000e+02 | 1.000e+02 |
| f25 | 1.000e+02 | 1.000e+02 |
| f26 | 2.000e+02 | 2.000e+02 |
| f27 | **3.897e+02** | 3.924e+02 |
| f28 | 3.000e+02 | 3.000e+02 |
| f29 | **2.322e+02** | 2.422e+02 |
| f30 | **4.133e+02** | 4.209e+02 |
| **SUM — Composition (f21–f30)** | **2.152e+03** | 2.176e+03 |
| **SUM — All (29 functions)** | **2.387e+03** | 2.583e+03 |

## Fixed-Budget Target Coverage — FBTC(B) ↑

| Function | MSC-CMA | MSC-fixed_sigma_lambda |
|:--|--:|--:|
| f1 | 0.933 | **1.000** |
| f3 | 1.000 | 1.000 |
| f4 | 0.977 | **0.997** |
| f5 | **0.282** | 0.145 |
| f6 | **0.434** | 0.407 |
| f7 | 0.110 | **0.115** |
| f8 | **0.577** | 0.147 |
| f9 | 0.742 | **0.874** |
| f10 | **0.093** | 0.017 |
| f11 | **1.000** | 0.188 |
| f12 | **0.071** | 0.058 |
| f13 | 0.131 | **0.132** |
| f14 | **0.301** | 0.088 |
| f15 | **0.191** | 0.153 |
| f16 | 0.156 | **0.176** |
| f17 | **0.095** | 0.071 |
| f18 | **0.094** | 0.084 |
| f19 | **0.168** | 0.141 |
| f20 | **0.140** | 0.072 |
| f21 | **0.059** | 0.000 |
| f22 | **0.498** | 0.208 |
| f23 | **0.098** | 0.078 |
| f24 | 0.275 | **0.294** |
| f25 | **0.020** | 0.000 |
| f26 | 0.392 | **0.471** |
| f27 | 0.000 | 0.000 |
| f28 | **0.373** | 0.294 |
| f29 | 0.000 | 0.000 |
| f30 | 0.000 | 0.000 |
| **SUM — Composition (f21–f30)** | **1.714** | 1.345 |
| **SUM — All (29 functions)** | **9.209** | 7.211 |

*Bold marks the better displayed value: lower median error or higher FBTC(B). These are descriptive comparisons; bold does not indicate statistical significance. SUM values are taken from the supplied reports before rounding individual table entries.*
