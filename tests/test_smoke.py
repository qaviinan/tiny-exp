from src.simulator import simulate_users
from src.srm_power import srm_pvalue, mde_for_two_proportions, power_for_two_proportions
from src.analyzer import analyze

def test_smoke():
    df, meta = simulate_users(n_users=5000, p0=0.12, split=(0.5,0.5), effect_type="relative", delta=0.03, pre_corr=0.5, seed=1)
    p, _ = srm_pvalue(df, planned=(0.5,0.5))
    assert 0.0 <= p <= 1.0
    res = analyze(df, use_cuped=True)
    assert "primary" in res and "guardrails" in res
    mde = mde_for_two_proportions(0.12, n_total=5000, alpha=0.05, power=0.8, alloc=(0.5,0.5))
    powr = power_for_two_proportions(0.12, d_abs=0.12*0.03, n_total=5000, alpha=0.05, alloc=(0.5,0.5))
    assert mde > 0 and 0 <= powr <= 1
