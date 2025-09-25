def decide(results, mde_abs, srm_ok=True, powered=True, guardrail_spec=None):
    """
    Ship if: SRM pass, power ok, primary CI entirely above MDE, guardrails within thresholds.
    """
    primary = results["primary"]["cuped"] if "cuped" in results["primary"] else results["primary"]["plain"]
    ci_low, ci_high = primary["ci"]
    ship = (srm_ok and powered and (ci_low > mde_abs))
    risk = []
    if not srm_ok:
        risk.append("SRM flagged (allocation off).")
    if not powered:
        risk.append("Under-powered for target MDE.")
    # Guardrails
    guard_ok = True
    breached = []
    if guardrail_spec:
        for g in guardrail_spec:
            name = g["name"]
            d = results["guardrails"][name]["diff"]*100.0  # convert to pp for flags intuition
            if g.get("direction","lower_is_better") == "lower_is_better":
                # If guardrail increased by more than allowed delta => breach
                if ("max_delta_pp" in g and d > g["max_delta_pp"]) or ("max_delta_pct" in g and d > g["max_delta_pct"]):
                    guard_ok = False
                    breached.append(f"{name} +{d:.2f}pp")
            else:
                # higher is better (not used in demo)
                pass
    if ship and guard_ok:
        decision = "SHIP"
    elif not guard_ok:
        decision = "ROLLBACK"
        risk.append("Guardrail breach: " + ", ".join(breached))
    else:
        decision = "HOLD"
    return decision, risk
