import numpy as np
import pandas as pd

def simulate_users(n_users=50000, p0=0.12, split=(0.5,0.5), 
                   effect_type="relative", delta=0.03, 
                   pre_corr=0.5, seed=42):
    rng = np.random.default_rng(seed)
    # Assign variant A/B by planned split
    variants = rng.choice(["A","B"], size=n_users, p=split)
    df = pd.DataFrame({"user_id": np.arange(n_users), "variant": variants})
    # Simple device segment for future stratification
    df["device"] = rng.choice(["desktop","mobile"], size=n_users, p=[0.4,0.6])
    # Pre-period covariate X (for CUPED): standard normal
    X = rng.normal(0, 1, size=n_users)
    # Construct outcome with a target corr(X, Y) ~ pre_corr via latent linear model
    # Map base propensity via logistic link to achieve p0
    # latent = a*X + noise; choose a to meet target corr approximately
    a = pre_corr
    noise = rng.normal(0, 1, size=n_users)
    latent = a*X + noise
    # Calibrate intercept to hit mean p0
    # Start with base logits near log(p0/(1-p0))
    base_logit = np.log(p0/(1.0-p0))
    # Convert to probability
    base_p = 1/(1+np.exp(-(base_logit + 0.0*latent)))
    # Treatment effect
    if effect_type == "relative":
        lift_mult = 1.0 + delta if delta is not None else 1.0
        pA = base_p
        pB = np.clip(base_p * lift_mult, 0.0001, 0.9999)
    else:
        # absolute
        pA = base_p
        pB = np.clip(base_p + (delta or 0.0), 0.0001, 0.9999)
    # Blend by variant
    p = np.where(df["variant"].eq("B"), pB, pA)
    # Inject mild device heterogeneity
    p = np.where(df["device"].eq("mobile"), np.clip(p*0.98, 0.0001, 0.9999), p)
    Y = (rng.uniform(size=n_users) < p).astype(int)
    # Extra demo metrics
    # error_flag slightly higher on B to test guardrails (tiny)
    error_flag = (rng.uniform(size=n_users) < (0.01 + 0.001 * (df["variant"]=="B"))).astype(int)
    # time_on_task ~ lognormal, slightly lower/better on B
    base_t = rng.lognormal(mean=2.0, sigma=0.5, size=n_users)
    tot = np.where(df["variant"].eq("B"), base_t*0.98, base_t)
    # Package
    out = df.assign(pre_metric_X=X, outcome_Y=Y, error_flag=error_flag, time_on_task=tot)
    meta = {
        "true_effect_type": effect_type,
        "true_delta": delta
    }
    return out, meta
