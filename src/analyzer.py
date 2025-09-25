import numpy as np
import pandas as pd
from scipy.stats import norm

def diff_in_means(yA, yB):
    mA, mB = yA.mean(), yB.mean()
    nA, nB = len(yA), len(yB)
    diff = mB - mA
    se = np.sqrt(yA.var(ddof=1)/nA + yB.var(ddof=1)/nB)
    z = diff / se if se>0 else 0.0
    p = 2*(1 - norm.cdf(abs(z)))
    ci_low = diff - 1.96*se
    ci_high = diff + 1.96*se
    return {"diff": float(diff), "se": float(se), "z": float(z), "p": float(p), "ci": (float(ci_low), float(ci_high))}

def compute_theta_cuped(X_pre, Y):
    # theta = Cov(Y, X)/Var(X)
    x = X_pre - X_pre.mean()
    y = Y - Y.mean()
    varX = (x**2).mean()
    covYX = (x*y).mean()
    theta = covYX / varX if varX>0 else 0.0
    return float(theta)

def apply_cuped(Y, X_pre, theta):
    return Y - theta*(X_pre - X_pre.mean())

def analyze(df, use_cuped=True):
    A = df[df.variant=="A"]
    B = df[df.variant=="B"]
    res = {}
    # Primary
    yA, yB = A["outcome_Y"].values, B["outcome_Y"].values
    base = diff_in_means(yA, yB)
    res["primary"] = {"plain": base}
    if use_cuped:
        theta = compute_theta_cuped(df["pre_metric_X"].values, df["outcome_Y"].values)
        yA_c = apply_cuped(A["outcome_Y"].values, A["pre_metric_X"].values, theta)
        yB_c = apply_cuped(B["outcome_Y"].values, B["pre_metric_X"].values, theta)
        cup = diff_in_means(yA_c, yB_c)
        # variance reduction
        vr = 1.0 - (cup["se"]**2)/(base["se"]**2) if base["se"]>0 else 0.0
        res["primary"]["cuped"] = {**cup, "theta": theta, "var_reduction_pct": float(max(0.0, vr*100))}
    # Guardrails (simple deltas)
    guard = {}
    for m in ["error_flag","time_on_task"]:
        d = diff_in_means(A[m].values, B[m].values)
        guard[m] = d
    res["guardrails"] = guard
    return res
