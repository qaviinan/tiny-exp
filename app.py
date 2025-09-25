import streamlit as st
import yaml, pandas as pd
from pathlib import Path
from src.simulator import simulate_users
from src.registry import MetricRegistry
from src.srm_power import srm_pvalue, mde_for_two_proportions, power_for_two_proportions
from src.analyzer import analyze
from src.decision import decide
from src.memo import render_markdown

st.set_page_config(page_title="Experimentation OS — Lite", layout="wide")

st.title("Experimentation OS — Lite")
st.write("A minimal, config-first A/B experimentation demo with CUPED and a decision memo.")

# Load configs
cfg = yaml.safe_load(open("config.yaml", "r"))
reg = MetricRegistry("metrics.yaml")

st.sidebar.header("Run Config")
n_users = st.sidebar.number_input("Users", min_value=1000, step=1000, value=cfg["n_users"])
alpha = st.sidebar.number_input("Alpha", min_value=0.001, max_value=0.2, step=0.001, value=float(cfg["alpha"]))
power_target = st.sidebar.number_input("Power target", min_value=0.5, max_value=0.99, step=0.01, value=float(cfg["power_target"]))
delta = st.sidebar.number_input("True effect (relative, e.g., 0.03=+3%)", min_value=-0.5, max_value=1.0, step=0.005, value=float(cfg["treatment"]["delta"]))
use_cuped = st.sidebar.checkbox("Use CUPED", value=bool(cfg["cuped"]["use_cuped"]))

run = st.sidebar.button("Run")

if run:
    df, meta = simulate_users(
        n_users=int(n_users),
        p0=float(cfg["baseline"]["conversion_p0"]),
        split=tuple(cfg["traffic_split"]),
        effect_type=cfg["treatment"]["effect_type"],
        delta=float(delta),
        pre_corr=float(cfg["cuped"]["pre_period_corr"]),
        seed=int(cfg["random_seed"])
    )
    st.success("Simulated data generated.")
    st.dataframe(df.head(10))

    # SRM
    p_srm, srm_info = srm_pvalue(df, planned=tuple(cfg["traffic_split"]))
    srm_ok = p_srm >= cfg["srm"]["alpha"]
    st.subheader("SRM Check")
    st.write(f"Observed counts: {srm_info[observed]} | Expected: {srm_info[expected]} | p={p_srm:.4g}")
    st.markdown("✅ **SRM PASS**" if srm_ok else "⚠️ **SRM FAIL**")

    # Power/MDE
    p0 = cfg["baseline"]["conversion_p0"]
    mde_abs = mde_for_two_proportions(p0, n_total=int(n_users), alpha=float(alpha), power=float(power_target), alloc=tuple(cfg["traffic_split"]))
    # Given *true* delta relative, compute absolute diff at p0 baseline (approx)
    d_abs_true = p0*float(delta)
    pow_now = power_for_two_proportions(p0, d_abs_true, n_total=int(n_users), alpha=float(alpha), alloc=tuple(cfg["traffic_split"]))
    powered = pow_now >= float(power_target)
    st.subheader("Power / MDE")
    st.write(f"MDE (abs): {mde_abs:.4f} | Power at true Δ: {pow_now:.3f}")

    # Analyze
    res = analyze(df, use_cuped=use_cuped)
    st.subheader("Primary Metric")
    prim = res["primary"]["cuped"] if use_cuped and "cuped" in res["primary"] else res["primary"]["plain"]
    st.write(prim)

    st.subheader("Guardrails")
    st.write(res["guardrails"])

    # Decision
    decision, risks = decide(res, mde_abs=mde_abs, srm_ok=srm_ok, powered=powered, guardrail_spec=reg.guardrails)
    st.header(f"Decision: {decision}")
    if risks:
        for r in risks:
            st.warning(r)

    # Memo
    meta_out = dict(n_users=int(n_users), planned_split=cfg["traffic_split"], **meta)
    memo_md = render_markdown(decision, risks, meta_out, res, mde_abs, powered, p_srm)
    st.subheader("Decision Memo (Markdown)")
    st.code(memo_md, language="markdown")

    # Export
    export_path = Path(cfg["export"]["memo_path"])
    export_path.write_text(memo_md, encoding="utf-8")
    st.success(f"Exported memo to {export_path}")
