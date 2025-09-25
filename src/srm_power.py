import numpy as np
import pandas as pd
from scipy.stats import chi2
from math import sqrt
from scipy.stats import norm

def srm_pvalue(df, planned=(0.5,0.5)):
    counts = df["variant"].value_counts().reindex(["A","B"]).fillna(0).values
    n = counts.sum()
    expected = np.array(planned) * n
    # Chi-square statistic
    stat = ((counts - expected)**2 / expected).sum()
    p = 1 - chi2.cdf(stat, df=1)
    return float(p), dict(observed=counts.tolist(), expected=expected.tolist(), stat=float(stat))

def mde_for_two_proportions(p0, n_total, alpha=0.05, power=0.8, alloc=(0.5,0.5)):
    # Normal approx for two-sample test with pooled variance
    z_alpha = norm.ppf(1 - alpha/2)
    z_power = norm.ppf(power)
    n1, n2 = n_total*alloc[0], n_total*alloc[1]
    # Solve approximately for absolute difference d
    # variance ~ p0*(1-p0)*(1/n1 + 1/n2)
    se = sqrt(p0*(1-p0)*(1/n1 + 1/n2))
    d = (z_alpha + z_power)*se
    return float(d)

def power_for_two_proportions(p0, d_abs, n_total, alpha=0.05, alloc=(0.5,0.5)):
    from scipy.stats import norm
    z_alpha = norm.ppf(1 - alpha/2)
    n1, n2 = n_total*alloc[0], n_total*alloc[1]
    se = np.sqrt(p0*(1-p0)*(1/n1 + 1/n2))
    z = d_abs / se - z_alpha
    return float(norm.cdf(z))
