from datetime import datetime

def render_markdown(decision, risk_notes, meta, stats, mde_abs, powered, srm_p):
    p = stats["primary"]["cuped"] if "cuped" in stats["primary"] else stats["primary"]["plain"]
    ci = p["ci"]
    vr = stats["primary"].get("cuped",{}).get("var_reduction_pct", 0.0)
    lines = []
    lines.append(f"# Experiment Decision Memo — {datetime.utcnow().strftime(%Y-%m-%d %H:%M UTC)}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"**Decision:** **{decision}**")
    lines.append(f"Primary lift (B−A): {p[diff]:.4f} (CI {ci[0]:.4f} … {ci[1]:.4f}); p={p[p]:.3g}")
    lines.append(f"MDE target (abs): {mde_abs:.4f} | Powered: {powered} | SRM p={srm_p:.3g}")
    lines.append(f"CUPED variance reduction: {vr:.1f}%")
    lines.append("")
    lines.append("## Design & Ground Truth")
    lines.append(f"- Planned split: {meta.get(planned_split)} | Users: {meta.get(n_users)}")
    lines.append(f"- True effect: {meta.get(true_effect_type)} {meta.get(true_delta)}")
    lines.append("")
    lines.append("## Guardrails")
    for k,v in stats["guardrails"].items():
        lines.append(f"- {k}: diff {v[diff]:.4f} (p={v[p]:.3g})")
    if risk_notes:
        lines.append("")
        lines.append("## Risks & Follow-ups")
        for r in risk_notes:
            lines.append(f"- {r}")
    return "
".join(lines)
