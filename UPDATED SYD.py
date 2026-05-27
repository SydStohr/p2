
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Supply Chain Game HAN",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

defaults = {
    "team_name": "GreenRoute Co.",
    "group_name": "Group 4",
    "score": 62,
    "quarter": 1,
    "difficulty": "Medium",
    "current_page": "🏠 Start",
    "selected_department": "Purchasing",
    "role_mode_enabled": False,
    "student_department_role": "Team view",

    # Instructor locking system
    "lock_dashboard": False,
    "lock_decision_log": False,
    "lock_financials": False,
    "lock_final_report": False,
    "lock_quarter_summary": False,
    "lock_finish_quarter": False,
    "lock_peer_comparison": False,
    "lock_kpi_impacts": False,
    "lock_message": "This section is currently locked by the instructor. Please wait for the next instruction.",
    "class_phase": "Decision round",
    "department_locks": {
        "Purchasing": False,
        "Operations": False,
        "Sales": False,
        "Supply Chain": False,
    },
    "revenue": 3200000,
    "net_profit": 900000,
    "inventory_value": 720000,
    "service_level": 78,
    "sustainability_score": 68,
    "lead_time_days": 18,
    "risk_level": 52,
    "event": "The new management team analyses the current supply chain.",
    "event_label": "Quarter 1 - Current State Analysis",
    "active_event_code": "current_state",
    "manual_event_override": False,
    "applied_event_quarters": [],

    "purchasing_chosen": None,
    "purchasing_confirmed": False,

    "operations_chosen": None,
    "operations_confirmed": False,
    "operations_stock_settings": None,
    "operations_pending_impact": None,

    "sales_chosen": None,
    "sales_confirmed": False,
    "supply_chain_chosen": None,
    "supply_chain_confirmed": False,

    "game_started": False,
    "game_paused": False,
    "completed_games": [],
    "decision_log": [],

    "history": [],
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


EVENTS = {
    1: {
        "code": "current_state",
        "title": "Quarter 1 - Current State Analysis",
        "description": "The new management team analyses the current supply chain.",
        "learning_objective": "Supply Chain Mapping and KPI Diagnosis",
        "kpi_modifier": {"risk": 0, "lead_time": 0, "service_level": 0, "esg": 0, "profit": 0},
    },
    2: {
        "code": "supplier_strategy",
        "title": "Quarter 2 - Supplier Strategy",
        "description": "Suppliers differ in cost, quality and reliability.",
        "learning_objective": "Supplier Selection and Sourcing Strategy",
        "kpi_modifier": {"risk": 5, "lead_time": 3, "service_level": -2, "profit": 20000},
    },
    3: {
        "code": "rotterdam_strike",
        "title": "Quarter 3 - Rotterdam Port Strike",
        "description": "Port strike in Rotterdam increases lead times by 14 days.",
        "learning_objective": "Risk Management and Resilience",
        "kpi_modifier": {"lead_time": 14, "risk": 12, "service_level": -4, "profit": -80000},
    },
    4: {
        "code": "demand_surge",
        "title": "Quarter 4 - Demand Surge",
        "description": "Customer demand increases unexpectedly.",
        "learning_objective": "Forecasting and Capacity Planning",
        "kpi_modifier": {"service_level": -5, "inventory": -100000, "profit": 50000},
    },
    5: {
        "code": "sustainability_pressure",
        "title": "Quarter 5 - Sustainability Pressure",
        "description": "Customers demand greener sourcing.",
        "learning_objective": "ESG and Sustainable Supply Chains",
        "kpi_modifier": {"esg": 8, "profit": -30000, "risk": -2},
    },
    6: {
        "code": "tariff",
        "title": "Quarter 6 - Tariff Shock",
        "description": "Import tariffs increase sourcing costs.",
        "learning_objective": "Global Sourcing and Total Landed Cost",
        "kpi_modifier": {"profit": -120000, "risk": 4},
    },
    7: {
        "code": "market_volatility",
        "title": "Quarter 7 - Market Volatility",
        "description": "Demand becomes highly uncertain.",
        "learning_objective": "Agility and Flexibility",
        "kpi_modifier": {"risk": 8, "service_level": -3},
    },
    8: {
        "code": "ceo_challenge",
        "title": "Quarter 8 - CEO Challenge",
        "description": "The CEO expects maximum ROI and strategic alignment.",
        "learning_objective": "Integrated Decision-Making",
        "kpi_modifier": {"profit": 100000, "risk": -5, "service_level": 3, "esg": 3},
    },
}


def get_event_for_quarter(quarter):
    return EVENTS.get(quarter, EVENTS[1])


def clamp_kpis():
    st.session_state.score = max(0, min(100, st.session_state.score))
    st.session_state.service_level = max(0, min(100, st.session_state.service_level))
    st.session_state.sustainability_score = max(0, min(100, st.session_state.sustainability_score))
    st.session_state.risk_level = max(0, min(100, st.session_state.risk_level))
    st.session_state.lead_time_days = max(1, st.session_state.lead_time_days)
    st.session_state.inventory_value = max(0, st.session_state.inventory_value)


def apply_event_modifiers_to_session_state(quarter):
    if quarter in st.session_state.applied_event_quarters:
        return

    event = get_event_for_quarter(quarter)
    key_map = {
        "risk": "risk_level",
        "lead_time": "lead_time_days",
        "service_level": "service_level",
        "esg": "sustainability_score",
        "profit": "net_profit",
        "inventory": "inventory_value",
        "revenue": "revenue",
        "score": "score",
    }

    for key, change in event["kpi_modifier"].items():
        session_key = key_map.get(key)
        if session_key in st.session_state:
            st.session_state[session_key] += change

    clamp_kpis()
    st.session_state.applied_event_quarters.append(quarter)


def sync_quarter_event():
    if st.session_state.manual_event_override:
        return

    event = get_event_for_quarter(st.session_state.quarter)
    st.session_state.active_event_code = event["code"]
    st.session_state.event_label = event["title"]
    st.session_state.event = event["description"]

    apply_event_modifiers_to_session_state(st.session_state.quarter)


sync_quarter_event()


def money(value):
    sign = "−" if value < 0 else ""
    value = abs(int(value))
    if value >= 1000000:
        return f"{sign}${value / 1000000:.2f}M"
    if value >= 1000:
        return f"{sign}${value / 1000:.0f}k"
    return f"{sign}${value}"


def sustainability_rating(score):
    if score >= 90:
        return "A"
    if score >= 80:
        return "B+"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C+"
    return "C"


def risk_label(score):
    if score <= 30:
        return "Low"
    if score <= 60:
        return "Medium"
    return "High"


def strategy_type():
    profit = st.session_state.net_profit
    service = st.session_state.service_level
    esg = st.session_state.sustainability_score
    risk = st.session_state.risk_level
    inventory = st.session_state.inventory_value

    if service >= 90 and risk <= 35:
        return "Resilient Strategist", "You protected delivery reliability and reduced supply chain risk."
    if esg >= 85:
        return "Green Leader", "You made sustainable choices and improved ESG performance."
    if profit >= 1350000 and risk >= 55:
        return "Risk Taker", "You protected short-term profit but accepted higher supply chain risk."
    if inventory >= 1050000:
        return "Inventory Hoarder", "You reduced stockout risk, but inventory and holding costs are becoming high."
    if profit >= 1350000:
        return "Cost Controller", "You controlled costs well and protected financial performance."
    return "Balanced Operator", "You made balanced decisions across profit, service, ESG and risk."


def get_forecast_tolerance():
    if st.session_state.difficulty == "Easy":
        return 20
    if st.session_state.difficulty == "Hard":
        return 10
    return 15


def apply_kpi_change(score=0, profit=0, revenue=0, inventory=0, service=0, sustainability=0, lead_time=0, risk=0):
    st.session_state.score += score
    st.session_state.net_profit += profit
    st.session_state.revenue += revenue
    st.session_state.inventory_value += inventory
    st.session_state.service_level += service
    st.session_state.sustainability_score += sustainability
    st.session_state.lead_time_days += lead_time
    st.session_state.risk_level += risk
    clamp_kpis()

    return {
        "Score": score,
        "Profit": profit,
        "Revenue": revenue,
        "Inventory": inventory,
        "Service": service,
        "ESG": sustainability,
        "Lead Time": lead_time,
        "Risk": risk,
    }


def record_decision(area, choice, concept, impact):
    st.session_state.decision_log.append(
        {
            "Quarter": f"Q{st.session_state.quarter}",
            "Area": area,
            "Choice": choice,
            "Concept": concept,
            "Score Impact": impact.get("Score", 0),
            "Profit Impact": impact.get("Profit", 0),
            "Revenue Impact": impact.get("Revenue", 0),
            "Inventory Impact": impact.get("Inventory", 0),
            "Service Impact": impact.get("Service", 0),
            "ESG Impact": impact.get("ESG", 0),
            "Lead Time Impact": impact.get("Lead Time", 0),
            "Risk Impact": impact.get("Risk", 0),
        }
    )


def add_current_quarter_to_history():
    current_q = f"Q{st.session_state.quarter}"
    current_data = {
        "Quarter": current_q,
        "Revenue": st.session_state.revenue,
        "Net Profit": st.session_state.net_profit,
        "Efficiency Score": st.session_state.score,
        "Service Level": st.session_state.service_level,
        "ESG Score": st.session_state.sustainability_score,
        "Inventory Value": st.session_state.inventory_value,
        "Risk Level": st.session_state.risk_level,
        "Lead Time": st.session_state.lead_time_days,
    }

    existing_quarters = [row["Quarter"] for row in st.session_state.history]
    if current_q in existing_quarters:
        index = existing_quarters.index(current_q)
        st.session_state.history[index] = current_data
    else:
        st.session_state.history.append(current_data)


def reset_quarter_games():
    st.session_state.purchasing_chosen = None
    st.session_state.purchasing_confirmed = False
    st.session_state.operations_chosen = None
    st.session_state.operations_confirmed = False
    st.session_state.operations_stock_settings = None
    st.session_state.operations_pending_impact = None
    st.session_state.sales_chosen = None
    st.session_state.sales_confirmed = False
    st.session_state.supply_chain_chosen = None
    st.session_state.supply_chain_confirmed = False
    st.session_state.completed_games = []


def get_peer_teams():
    """
    Returns simulated peer-team KPI data for the current quarter.
    Data is deterministic per quarter so it stays stable during a session.
    The current team is always included with live KPI values.
    """
    q = st.session_state.quarter

    # Base peer stats — scaled gently per quarter to feel realistic
    growth = 1 + (q - 1) * 0.035
    peers = [
        {
            "Team": "Team Apex",
            "Score": min(100, int(91 + q * 0.4)),
            "Net Profit": int(1_820_000 * growth),
            "Service Level": min(100, 94 + (q % 3)),
            "ESG Score": min(100, 82 + q),
            "Risk Level": max(15, 28 - q),
            "Lead Time": max(6, 16 - q),
        },
        {
            "Team": "NovaTrade",
            "Score": min(100, int(88 - q * 0.2)),
            "Net Profit": int(1_710_000 * growth),
            "Service Level": min(100, 91 - (q % 2)),
            "ESG Score": min(100, 79 + q),
            "Risk Level": max(18, 33 - q),
            "Lead Time": max(7, 15 - q),
        },
        {
            "Team": "LogiX Group",
            "Score": min(100, int(83 + q * 0.1)),
            "Net Profit": int(1_580_000 * growth),
            "Service Level": min(100, 89),
            "ESG Score": min(100, 74 + q),
            "Risk Level": max(20, 38 - q),
            "Lead Time": max(8, 17 - q),
        },
        {
            "Team": "FastLink",
            "Score": max(30, int(69 - q * 0.5)),
            "Net Profit": int(1_100_000 * growth),
            "Service Level": max(55, 78 - (q % 4)),
            "ESG Score": max(40, 66 - q),
            "Risk Level": min(95, 52 + q),
            "Lead Time": min(30, 18 + q),
        },
        {
            "Team": "ChainMasters",
            "Score": max(20, int(61 - q * 1.2)),
            "Net Profit": int(-220_000 * growth),
            "Service Level": max(45, 67 - q),
            "ESG Score": max(35, 58 - q),
            "Risk Level": min(95, 60 + q),
            "Lead Time": min(35, 22 + q),
        },
    ]

    # Insert the current team
    current = {
        "Team": f"⭐ {st.session_state.team_name}",
        "Score": st.session_state.score,
        "Net Profit": st.session_state.net_profit,
        "Service Level": st.session_state.service_level,
        "ESG Score": st.session_state.sustainability_score,
        "Risk Level": st.session_state.risk_level,
        "Lead Time": st.session_state.lead_time_days,
    }

    all_teams = peers + [current]
    # Sort by Score descending
    all_teams.sort(key=lambda t: t["Score"], reverse=True)
    return all_teams


def show_peer_comparison():
    """Renders the peer-comparison leaderboard and bar charts for the Quarter Summary."""
    st.markdown("---")
    st.markdown("### 🏆 Class comparison — how does your team rank this quarter?")

    teams = get_peer_teams()
    team_names = [t["Team"] for t in teams]
    my_team_label = f"⭐ {st.session_state.team_name}"

    # Rank
    rank = next((i + 1 for i, t in enumerate(teams) if t["Team"] == my_team_label), None)
    total = len(teams)

    if rank == 1:
        rank_msg = f"🥇 Your team is **ranked #1** out of {total} teams this quarter!"
    elif rank == 2:
        rank_msg = f"🥈 Your team is **ranked #2** out of {total} teams — almost at the top!"
    elif rank == 3:
        rank_msg = f"🥉 Your team is **ranked #3** out of {total} teams — a strong position."
    elif rank and rank >= total:
        rank_msg = f"⚠️ Your team is **ranked last** ({rank}/{total}). There is room to improve."
    else:
        rank_msg = f"📊 Your team is **ranked #{rank}** out of {total} teams."

    st.markdown(rank_msg)

    # Leaderboard table
    df_rows = []
    for i, t in enumerate(teams):
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
        df_rows.append({
            "Rank": medal,
            "Team": t["Team"],
            "Score": f"{t['Score']}/100",
            "Net Profit": money(t["Net Profit"]),
            "Service Level": f"{t['Service Level']}%",
            "ESG Score": t["ESG Score"],
            "Risk Level": t["Risk Level"],
            "Lead Time (days)": t["Lead Time"],
        })

    st.dataframe(pd.DataFrame(df_rows), use_container_width=True, hide_index=True)

    # Visual bar charts for key KPIs
    st.markdown("#### KPI breakdown across teams")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Efficiency Score**")
        score_data = pd.DataFrame({
            "Team": team_names,
            "Score": [t["Score"] for t in teams],
        }).set_index("Team")
        st.bar_chart(score_data)

        st.markdown("**Service Level (%)**")
        sl_data = pd.DataFrame({
            "Team": team_names,
            "Service Level": [t["Service Level"] for t in teams],
        }).set_index("Team")
        st.bar_chart(sl_data)

    with col_b:
        st.markdown("**Net Profit**")
        profit_data = pd.DataFrame({
            "Team": team_names,
            "Net Profit": [t["Net Profit"] for t in teams],
        }).set_index("Team")
        st.bar_chart(profit_data)

        st.markdown("**Risk Level (lower is better)**")
        risk_data = pd.DataFrame({
            "Team": team_names,
            "Risk Level": [t["Risk Level"] for t in teams],
        }).set_index("Team")
        st.bar_chart(risk_data)

    # Contextual tips based on rank
    st.markdown("#### 💡 What this means for you")
    my = next(t for t in teams if t["Team"] == my_team_label)

    tips = []
    avg_service = sum(t["Service Level"] for t in teams) / len(teams)
    avg_esg = sum(t["ESG Score"] for t in teams) / len(teams)
    avg_risk = sum(t["Risk Level"] for t in teams) / len(teams)

    if my["Service Level"] < avg_service - 5:
        tips.append("Your service level is below the class average — consider reviewing your inventory and supplier decisions.")
    if my["ESG Score"] < avg_esg - 5:
        tips.append("Your ESG score is below average. Sustainable sourcing and operations choices can improve this.")
    if my["Risk Level"] > avg_risk + 5:
        tips.append("Your supply chain risk is higher than most teams. Diversifying suppliers or increasing safety stock may help.")
    if my["Net Profit"] < 0:
        tips.append("Your team is currently operating at a loss. Review cost-heavy decisions in Purchasing and Operations.")
    if rank == 1:
        tips.append("You are leading the class — but stay sharp, other teams can close the gap quickly.")

    if tips:
        for tip in tips:
            st.info(tip)
    else:
        st.success("Your team is performing well compared to the class. Keep making balanced decisions.")


def apply_operations_pending_stock_impact():
    """
    Operations stock slider results are applied only when the quarter is finished.
    This prevents students from seeing the result immediately after confirming.
    """
    impact = st.session_state.operations_pending_impact

    if impact is None:
        return

    choice_text = st.session_state.operations_chosen or "Stock level determination"
    applied = apply_kpi_change(
        score=impact["Score"],
        profit=impact["Profit"],
        revenue=impact["Revenue"],
        inventory=impact["Inventory"],
        service=impact["Service"],
        sustainability=impact["ESG"],
        lead_time=impact["Lead Time"],
        risk=impact["Risk"],
    )
    record_decision("Operations", choice_text, "Stock determination", applied)
    st.session_state.operations_pending_impact = None


def show_quarter_summary():
    apply_operations_pending_stock_impact()
    add_current_quarter_to_history()
    st.session_state.current_page = "📋 Quarter Summary"
    st.rerun()


def continue_to_next_quarter():
    if st.session_state.quarter < 8:
        st.session_state.quarter += 1
        st.session_state.revenue = int(st.session_state.revenue * 1.04)
        st.session_state.net_profit = int(st.session_state.net_profit * 1.02)
        st.session_state.lead_time_days = max(8, int(st.session_state.lead_time_days * 0.95))
        st.session_state.risk_level = max(20, int(st.session_state.risk_level * 0.95))
        reset_quarter_games()
        st.session_state.manual_event_override = False
        sync_quarter_event()
        st.session_state.current_page = "📝 Decision Log"
    else:
        st.session_state.current_page = "🏁 Final Report"

    st.rerun()


def current_quarter_decisions():
    return [row for row in st.session_state.decision_log if row["Quarter"] == f"Q{st.session_state.quarter}"]


def make_decision_table(rows):
    formatted = []

    for row in rows:
        formatted.append(
            {
                "Quarter": row["Quarter"],
                "Department": row["Area"],
                "Decision": row["Choice"],
                "Concept": row["Concept"],
                "Score": row["Score Impact"],
                "Profit": money(row["Profit Impact"]),
                "Revenue": money(row["Revenue Impact"]),
                "Inventory": money(row["Inventory Impact"]),
                "Service": f"{row['Service Impact']:+}",
                "ESG": f"{row['ESG Impact']:+}",
                "Lead Time": f"{row['Lead Time Impact']:+}",
                "Risk": f"{row['Risk Impact']:+}",
            }
        )

    return formatted


def show_clean_decision_table(rows):
    df = pd.DataFrame(make_decision_table(rows))

    if st.session_state.get("lock_kpi_impacts", False) and not is_instructor_unlocked():
        safe_columns = ["Quarter", "Department", "Decision", "Concept"]
        df = df[[col for col in safe_columns if col in df.columns]]
        st.info("KPI impact details are locked by the instructor. The decision overview is visible, but the exact effects are hidden for now.")

    st.dataframe(df, use_container_width=True, hide_index=True)


def quarter_kpi_comment():
    score = st.session_state.score
    service = st.session_state.service_level
    risk = st.session_state.risk_level
    profit = st.session_state.net_profit
    inventory = st.session_state.inventory_value

    comments = []

    if score >= 80:
        comments.append("The team is performing strongly overall.")
    elif score >= 65:
        comments.append("The team is performing reasonably well, but there is room for improvement.")
    else:
        comments.append("The team needs to improve its supply chain decisions in the next quarter.")

    if service >= 90:
        comments.append("Service level is strong, meaning customers are likely receiving orders on time.")
    elif service >= 80:
        comments.append("Service level is acceptable, but delivery reliability can still improve.")
    else:
        comments.append("Service level is under pressure, which may lead to stockouts or unhappy customers.")

    if risk <= 35:
        comments.append("Risk is well controlled.")
    elif risk <= 60:
        comments.append("Risk is manageable, but the supply chain is still exposed to disruption.")
    else:
        comments.append("Risk is high, so the company should focus on resilience next quarter.")

    if inventory >= 1050000:
        comments.append("Inventory value is becoming high, which increases holding costs.")
    elif inventory <= 650000:
        comments.append("Inventory is relatively low, which can help costs but may increase stockout risk.")

    if profit < 1000000:
        comments.append("Profit is lower than desired, so cost control should be reviewed.")

    return " ".join(comments)


def get_current_event_note():
    code = st.session_state.active_event_code
    event = get_event_for_quarter(st.session_state.quarter)

    if code == "current_state":
        return "The company is analysing its current supply chain. The focus is on understanding KPIs and identifying bottlenecks."
    if code == "supplier_strategy":
        return "Suppliers differ in cost, quality and reliability. Purchasing decisions should balance cost savings and supply risk."
    if code == "rotterdam_strike":
        return "Sea freight through Rotterdam is disrupted. Alternative routes and reliable suppliers become more attractive."
    if code == "demand_surge":
        return "Customer demand increases unexpectedly. Production capacity, inventory and sales promises are under pressure."
    if code == "sustainability_pressure":
        return "Customers demand greener sourcing. ESG performance becomes more important, but sustainable choices may affect costs."
    if code == "tariff":
        return "Foreign sourcing is more expensive. Purchasing decisions should consider local alternatives, split sourcing or total landed cost."
    if code == "market_volatility":
        return "Demand is highly uncertain. The company needs flexibility in production, inventory and sales decisions."
    if code == "ceo_challenge":
        return "The CEO expects strong ROI and alignment between departments. Integrated decision-making is essential."
    if code == "suez_blockage":
        return "Global sea freight is disrupted. Transport and supply chain decisions should avoid heavy dependence on sea routes."
    if code == "taiwan_fire":
        return "Component availability is low. Inventory and supplier reliability are extra important."
    if code == "currency_shock":
        return "Currency movement hurts margins. Cost control and pricing decisions matter more."
    if code == "pandemic":
        return "Demand is unstable. Sales promises and inventory levels should be managed carefully."
    if code == "labour_strike":
        return "Road logistics are delayed. Lead time and service level are under pressure."

    return event["learning_objective"]


def calculate_stock_slider_impact(slider_values):
    """
    Scores slider-based stock targets.
    Target is based on demand + safety stock.
    Too low = stockout / service risk.
    Too high = obsolete inventory and holding cost.
    """
    products = get_operations_products()
    total_score = 0
    total_profit = 0
    total_inventory = 0
    total_service = 0
    total_risk = 0
    total_lead_time = 0

    comments = []

    for product in products:
        name = product["Product"]
        current = product["Current stock"]
        demand = product["Expected demand"]
        safety = product["Safety stock"]
        target = demand + safety
        chosen = slider_values[name]
        deviation = chosen - target
        deviation_pct = deviation / target

        inventory_change_units = chosen - current
        total_inventory += inventory_change_units * product["Unit value"]

        if abs(deviation_pct) <= 0.10:
            total_score += 3
            total_profit += 20000
            total_service += 2
            total_risk -= 2
            comments.append(f"{name}: stock target is close to the required level.")
        elif deviation_pct < -0.10:
            shortage_units = target - chosen
            total_score -= 3
            total_profit -= int(shortage_units * product["Stockout cost"])
            total_service -= 4
            total_risk += 5
            total_lead_time += 1
            comments.append(f"{name}: stock is too low, creating stockout risk.")
        else:
            excess_units = chosen - target
            total_score -= 2
            total_profit -= int(excess_units * product["Holding/obsolete cost"])
            total_service += 1
            total_risk += 1
            comments.append(f"{name}: stock is too high, increasing holding and obsolete inventory risk.")

    impact = {
        "Score": total_score,
        "Profit": total_profit,
        "Revenue": 0,
        "Inventory": total_inventory,
        "Service": total_service,
        "ESG": 0,
        "Lead Time": total_lead_time,
        "Risk": total_risk,
        "Comments": comments,
    }

    return impact


def get_operations_products():
    """
    Creates product data for the Operations stock slider.
    The stock situation is recalculated every quarter, so warnings and tips change during the game.
    """
    base = [
        {
            "Product": "FreshMix 250ml",
            "Base stock": 12000,
            "Base demand": 18000,
            "Base safety stock": 3000,
            "Unit value": 8,
            "Stockout cost": 12,
            "Holding/obsolete cost": 4,
        },
        {
            "Product": "FreshMix 500ml",
            "Base stock": 26000,
            "Base demand": 24000,
            "Base safety stock": 4000,
            "Unit value": 10,
            "Stockout cost": 14,
            "Holding/obsolete cost": 5,
        },
        {
            "Product": "FreshMix 1L",
            "Base stock": 8000,
            "Base demand": 13500,
            "Base safety stock": 2500,
            "Unit value": 14,
            "Stockout cost": 18,
            "Holding/obsolete cost": 7,
        },
    ]

    quarter = st.session_state.quarter
    event = st.session_state.active_event_code

    # Demand changes slightly over time, so each quarter feels different.
    quarter_demand_factor = 1 + max(0, quarter - 3) * 0.04

    # Current stock is influenced by the company's total inventory value.
    inventory_factor = st.session_state.inventory_value / 860000
    inventory_factor = max(0.65, min(1.45, inventory_factor))

    products = []

    for index, product in enumerate(base):
        demand = int(product["Base demand"] * quarter_demand_factor)
        safety_stock = int(product["Base safety stock"])
        current_stock = int(product["Base stock"] * inventory_factor)

        # Small product-specific quarter pattern to avoid all products moving in the same direction.
        if quarter % 3 == 1 and index == 0:
            demand = int(demand * 1.12)
        elif quarter % 3 == 2 and index == 1:
            demand = int(demand * 1.10)
        elif quarter % 3 == 0 and index == 2:
            demand = int(demand * 1.13)

        if event == "demand_surge":
            demand = int(demand * 1.18)
        if event in ["market_volatility", "pandemic"]:
            safety_stock = int(safety_stock * 1.25)
        if event in ["rotterdam_strike", "suez_blockage", "labour_strike"]:
            safety_stock = int(safety_stock * 1.15)
        if event == "tariff":
            current_stock = int(current_stock * 0.92)
        if event == "sustainability_pressure":
            safety_stock = int(safety_stock * 0.95)

        products.append(
            {
                "Product": product["Product"],
                "Current stock": current_stock,
                "Expected demand": demand,
                "Safety stock": safety_stock,
                "Unit value": product["Unit value"],
                "Stockout cost": product["Stockout cost"],
                "Holding/obsolete cost": product["Holding/obsolete cost"],
            }
        )

    return products


def get_stock_status(product):
    """Returns a status and tip based on the current stock position for one product."""
    current = product["Current stock"]
    demand = product["Expected demand"]
    safety = product["Safety stock"]
    target = demand + safety

    if current < demand:
        return (
            "Low stock",
            "Current stock is below expected demand. There is a clear stockout risk if no action is taken.",
        )
    if current < target:
        return (
            "Below target",
            "Current stock covers expected demand, but not the recommended safety stock. A slightly higher target may protect service level.",
        )
    if current > target * 1.25:
        return (
            "Too high",
            "Current stock is far above the recommended level. This can increase holding costs and obsolete inventory risk.",
        )
    return (
        "Healthy",
        "Current stock is close to the recommended level. Keep the target near demand plus safety stock.",
    )


def render_operations_tips(products):
    """Shows fresh stock tips every quarter before the sliders are used."""
    low_or_high = []

    for product in products:
        status, tip = get_stock_status(product)
        if status != "Healthy":
            low_or_high.append((product["Product"], status, tip))

    if not low_or_high:
        st.success("Operations tip: stock levels look fairly balanced this quarter. Try to stay close to demand plus safety stock.")
        return

    st.markdown("### Operations tips for this quarter")
    for product_name, status, tip in low_or_high:
        if status in ["Low stock", "Below target"]:
            st.warning(f"{product_name}: {status}. {tip}")
        else:
            st.info(f"{product_name}: {status}. {tip}")



# ── Instructor Locking System ────────────────────────────────────────────────
def is_instructor_unlocked():
    """Returns True when the instructor has unlocked the instructor background."""
    return st.session_state.get("instructor_authenticated", False)


def is_page_locked(page_name):
    """
    Checks whether a page is locked for students.
    Instructor view remains reachable because it contains the password screen.
    """
    if page_name == "👨‍🏫 Instructor view":
        return False

    if is_instructor_unlocked():
        return False

    page_lock_map = {
        "📊 Dashboard": "lock_dashboard",
        "📝 Decision Log": "lock_decision_log",
        "📋 Quarter Summary": "lock_quarter_summary",
        "💰 Financials": "lock_financials",
        "🏁 Final Report": "lock_final_report",
    }

    lock_key = page_lock_map.get(page_name)
    return bool(st.session_state.get(lock_key, False)) if lock_key else False


def is_department_locked(department_name):
    """
    Checks whether a department is locked in the Decision Log.
    The instructor can still see locked departments after logging in.
    """
    if is_instructor_unlocked():
        return False

    locks = st.session_state.get("department_locks", {})
    return bool(locks.get(department_name, False))


def get_department_role():
    """
    Role selection is no longer controlled by students.
    The instructor now controls playable departments by locking or unlocking departments.
    """
    return "Team view"


def is_role_limited():
    """Student-side role limiting is disabled. Department access is controlled by instructor locks."""
    return False


def get_playable_departments():
    """
    Returns the departments students are allowed to play this round.

    If the instructor locks Operations, Sales and Supply Chain, only Purchasing remains playable.
    The game then only requires the Purchasing decision before students can finish the round.
    """
    departments = ["Purchasing", "Operations", "Sales", "Supply Chain"]
    locks = st.session_state.get("department_locks", {})

    playable = [department for department in departments if not bool(locks.get(department, False))]

    return playable


def get_round_scope_label():
    """Creates a readable label for the departments that are playable this round."""
    playable = get_playable_departments()

    if len(playable) == 4:
        return "Full team round: all departments are playable."
    if len(playable) == 0:
        return "No departments are currently playable. The instructor needs to unlock at least one department."
    if len(playable) == 1:
        return f"Single-department round: only {playable[0]} is playable."

    return "Multi-department round: " + ", ".join(playable) + " are playable."


def get_required_departments_for_round():
    """Departments that must be completed before the round can be finished."""
    playable = get_playable_departments()

    if not playable:
        return ["Purchasing", "Operations", "Sales", "Supply Chain"]

    return playable


def get_completed_required_departments():
    """Required departments that have already been completed."""
    required = get_required_departments_for_round()
    return [department for department in required if department in st.session_state.completed_games]


def is_round_complete():
    """
    Checks whether the current round can be finished.

    This fixes the situation where the instructor only unlocks one department,
    for example Purchasing. In that case, students only need to complete Purchasing.
    """
    required = get_required_departments_for_round()

    if not required:
        return False

    return all(department in st.session_state.completed_games for department in required)


def is_department_access_locked(department_name):
    """
    A department is locked when the instructor locks it.
    Instructor mode bypasses the lock, so the teacher can still inspect everything.
    """
    return is_department_locked(department_name)


def get_department_lock_reason(department_name):
    """Explains why a department is locked for the current student."""
    if is_department_locked(department_name):
        return f"{department_name} Department is locked by the instructor"

    return f"{department_name} Department is locked"


def get_active_locks():
    """Returns a readable list of active locks for the sidebar and instructor panel."""
    active = []

    page_labels = {
        "lock_dashboard": "Dashboard",
        "lock_decision_log": "Decision Log",
        "lock_financials": "Financials",
        "lock_final_report": "Final Report",
        "lock_quarter_summary": "Quarter Summary",
        "lock_finish_quarter": "Finish Quarter",
        "lock_peer_comparison": "Class Comparison",
        "lock_kpi_impacts": "KPI Impact Details",
    }

    for key, label in page_labels.items():
        if st.session_state.get(key, False):
            active.append(label)

    for department, locked in st.session_state.get("department_locks", {}).items():
        if locked:
            active.append(f"{department} Department")

    return active


def render_locked_message(title="Locked by instructor"):
    """Shows a consistent locked screen."""
    st.markdown("## 🔒 " + title)
    st.markdown(
        f"""
<div class="locked-card">
    <strong>{st.session_state.get("class_phase", "Class phase")}</strong><br><br>
    {st.session_state.get("lock_message", "This section is locked by the instructor.")}
</div>
""",
        unsafe_allow_html=True,
    )
    st.info("Ask the instructor to unlock this section when the class is ready to continue.")


def set_lock_values(
    dashboard=None,
    decision_log=None,
    financials=None,
    final_report=None,
    quarter_summary=None,
    finish_quarter=None,
    peer_comparison=None,
    kpi_impacts=None,
    class_phase=None,
):
    """
    Updates lock values safely from button callbacks.

    Important Streamlit detail:
    each checkbox also has its own widget key, for example cb_lock_dashboard.
    If only lock_dashboard is changed, the visible checkbox can stay checked
    because Streamlit keeps the widget key value. Therefore this function updates
    both the real lock value and the matching checkbox widget key.
    """
    updates = {
        "lock_dashboard": dashboard,
        "lock_decision_log": decision_log,
        "lock_financials": financials,
        "lock_final_report": final_report,
        "lock_quarter_summary": quarter_summary,
        "lock_finish_quarter": finish_quarter,
        "lock_peer_comparison": peer_comparison,
        "lock_kpi_impacts": kpi_impacts,
    }

    widget_key_map = {
        "lock_dashboard": "cb_lock_dashboard",
        "lock_decision_log": "cb_lock_decision_log",
        "lock_financials": "cb_lock_financials",
        "lock_final_report": "cb_lock_final_report",
        "lock_quarter_summary": "cb_lock_quarter_summary",
        "lock_finish_quarter": "cb_lock_finish_quarter",
        "lock_peer_comparison": "cb_lock_peer_comparison",
        "lock_kpi_impacts": "cb_lock_kpi_impacts",
    }

    for key, value in updates.items():
        if value is not None:
            st.session_state[key] = value
            st.session_state[widget_key_map[key]] = value

    if class_phase is not None:
        st.session_state.class_phase = class_phase
        st.session_state.class_phase_select = class_phase


def set_department_lock_values(purchasing=None, operations=None, sales=None, supply_chain=None):
    """
    Updates department lock values and the matching checkbox widget keys.
    This makes quick-mode buttons visually update the department checkboxes too.
    """
    updates = {
        "Purchasing": purchasing,
        "Operations": operations,
        "Sales": sales,
        "Supply Chain": supply_chain,
    }

    if "department_locks" not in st.session_state:
        st.session_state.department_locks = {
            "Purchasing": False,
            "Operations": False,
            "Sales": False,
            "Supply Chain": False,
        }

    for department, value in updates.items():
        if value is not None:
            st.session_state.department_locks[department] = value
            st.session_state[f"cb_lock_department_{department}"] = value


def unlock_all_locks():
    """Unlocks all pages, departments and feedback settings safely."""
    set_lock_values(
        dashboard=False,
        decision_log=False,
        financials=False,
        final_report=False,
        quarter_summary=False,
        finish_quarter=False,
        peer_comparison=False,
        kpi_impacts=False,
        class_phase="Decision round",
    )

    set_department_lock_values(
        purchasing=False,
        operations=False,
        sales=False,
        supply_chain=False,
    )


def set_decision_round_mode():
    """Typical mode while students are making decisions."""
    set_lock_values(
        dashboard=False,
        decision_log=False,
        financials=True,
        final_report=True,
        quarter_summary=True,
        finish_quarter=False,
        peer_comparison=True,
        kpi_impacts=True,
        class_phase="Decision round",
    )

    set_department_lock_values(
        purchasing=False,
        operations=False,
        sales=False,
        supply_chain=False,
    )


def set_review_mode():
    """Typical mode while the instructor reviews results with the class."""
    set_lock_values(
        dashboard=False,
        decision_log=True,
        financials=False,
        final_report=True,
        quarter_summary=False,
        finish_quarter=True,
        peer_comparison=False,
        kpi_impacts=False,
        class_phase="Review round",
    )

    set_department_lock_values(
        purchasing=True,
        operations=True,
        sales=True,
        supply_chain=True,
    )


def render_lock_panel():
    """Instructor controls for locking and unlocking pages, departments and feedback."""
    st.markdown("### 🔐 Instructor Lock Panel")
    st.caption(
        "Use these controls to guide the class. Locks are dynamic and can be changed during the simulation. "
        "While you are logged in as instructor, locks are bypassed for you. Use 'Preview as student' in the sidebar to test them."
    )

    st.markdown("#### Quick modes")
    c1, c2, c3 = st.columns(3)

    c1.button(
        "🔓 Unlock everything",
        use_container_width=True,
        on_click=unlock_all_locks,
    )

    c2.button(
        "🎓 Decision-round mode",
        use_container_width=True,
        on_click=set_decision_round_mode,
    )

    c3.button(
        "🔍 Review mode",
        use_container_width=True,
        on_click=set_review_mode,
    )

    st.session_state.class_phase = st.selectbox(
        "Class phase",
        ["Briefing", "Decision round", "Review round", "Final presentation"],
        index=["Briefing", "Decision round", "Review round", "Final presentation"].index(
            st.session_state.get("class_phase", "Decision round")
        ),
        key="class_phase_select",
    )

    st.session_state.lock_message = st.text_area(
        "Message shown to students when something is locked",
        value=st.session_state.get(
            "lock_message",
            "This section is currently locked by the instructor. Please wait for the next instruction.",
        ),
        height=80,
        key="lock_message_input",
    )

    st.markdown("#### Page locks")
    p1, p2 = st.columns(2)

    with p1:
        st.session_state.lock_dashboard = st.checkbox(
            "Lock Dashboard",
            value=st.session_state.lock_dashboard,
            key="cb_lock_dashboard",
        )
        st.session_state.lock_decision_log = st.checkbox(
            "Lock Decision Log",
            value=st.session_state.lock_decision_log,
            key="cb_lock_decision_log",
        )
        st.session_state.lock_financials = st.checkbox(
            "Lock Financials",
            value=st.session_state.lock_financials,
            key="cb_lock_financials",
        )

    with p2:
        st.session_state.lock_final_report = st.checkbox(
            "Lock Final Report",
            value=st.session_state.lock_final_report,
            key="cb_lock_final_report",
        )
        st.session_state.lock_quarter_summary = st.checkbox(
            "Lock Quarter Summary",
            value=st.session_state.lock_quarter_summary,
            key="cb_lock_quarter_summary",
        )
        st.session_state.lock_finish_quarter = st.checkbox(
            "Lock Finish Quarter button",
            value=st.session_state.lock_finish_quarter,
            key="cb_lock_finish_quarter",
        )

    st.markdown("#### Department locks")
    dcols = st.columns(4)
    departments = ["Purchasing", "Operations", "Sales", "Supply Chain"]

    for col, department in zip(dcols, departments):
        with col:
            widget_key = f"cb_lock_department_{department}"
            current_value = st.session_state.department_locks.get(department, False)
            st.session_state.department_locks[department] = st.checkbox(
                department,
                value=current_value,
                key=widget_key,
            )

    st.markdown("#### Playable department setup")
    playable_departments = get_playable_departments()
    required_departments = get_required_departments_for_round()

    if len(playable_departments) == 0:
        st.error("No departments are currently playable for students. Unlock at least one department to start a playable round.")
    else:
        st.markdown(
            f"""
<div class="instructor-info-card">
<strong>{get_round_scope_label()}</strong><br><br>
Students only need to complete the unlocked department(s) before they can finish the round.
This makes it possible to run a one-role session, for example an <strong>Operations-only</strong> round.
</div>
""",
            unsafe_allow_html=True,
        )

    st.caption(
        "Tip: for a group-of-four setup, open the game on four devices and lock three departments on each device. "
        "For example, one device has only Purchasing unlocked, another only Operations, another only Sales and another only Supply Chain."
    )

    st.markdown("#### Feedback locks")
    f1, f2 = st.columns(2)

    with f1:
        st.session_state.lock_kpi_impacts = st.checkbox(
            "Hide KPI impact details from students",
            value=st.session_state.lock_kpi_impacts,
            key="cb_lock_kpi_impacts",
        )

    with f2:
        st.session_state.lock_peer_comparison = st.checkbox(
            "Hide class comparison from students",
            value=st.session_state.lock_peer_comparison,
            key="cb_lock_peer_comparison",
        )

    active_locks = get_active_locks()

    if active_locks:
        st.warning("Active locks: " + ", ".join(active_locks))
    else:
        st.success("No active locks. Students can access all main sections.")


# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid rgba(28,27,25,0.12);
    border-radius: 12px;
    padding: 16px 18px;
}
section[data-testid="stSidebar"] { background: #1C1B19 !important; }
section[data-testid="stSidebar"] * { color: #E8E6E0 !important; }
.stButton > button {
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 14px;
    padding: 8px 18px;
    border: 1px solid rgba(28,27,25,0.2);
    transition: all 0.15s;
}
.stButton > button:hover { border-color: rgba(28,27,25,0.5); }
.stProgress > div > div { background-color: #185FA5 !important; }
.event-banner {
    background: #FAEEDA;
    border: 1px solid #EF9F27;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 16px;
    font-size: 14px;
    color: #412402;
}
.event-label {
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #633806;
}
.result-correct {
    background: #EAF3DE;
    border: 1px solid #97C459;
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 13px;
    color: #173404;
    margin-top: 12px;
    line-height: 1.6;
}
.result-wrong {
    background: #FAECE7;
    border: 1px solid #F09595;
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 13px;
    color: #501313;
    margin-top: 12px;
    line-height: 1.6;
}
.result-neutral {
    background: #E6F1FB;
    border: 1px solid #8BBBE8;
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 13px;
    color: #0C447C;
    margin-top: 12px;
    line-height: 1.6;
}
.white-card {
    background: #FFFFFF;
    border: 1px solid rgba(28,27,25,0.12);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 16px;
}
.white-card h1,
.white-card h2,
.white-card h3,
.white-card h4 {
    color: #1C1B19 !important;
    font-weight: 700;
}
.white-card p,
.white-card div,
.white-card span {
    color: #5F5E5A;
}
.card-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #888780;
    margin-bottom: 12px;
}
.kpi-note { color: #5F5E5A; font-size: 13px; line-height: 1.5; }
.badge-blue { background:#E6F1FB; color:#0C447C; border-radius:6px; padding:3px 9px; font-size:12px; font-weight:500; }
.badge-orange { background:#FAEEDA; color:#633806; border-radius:6px; padding:3px 9px; font-size:12px; font-weight:500; }
.badge-red { background:#FAECE7; color:#993C1D; border-radius:6px; padding:3px 9px; font-size:12px; font-weight:500; }
.badge-green { background:#EAF3DE; color:#0F6E56; border-radius:6px; padding:3px 9px; font-size:12px; font-weight:500; }
.big-title { font-size: 44px; font-weight: 700; margin-bottom: 4px; }
.subtitle { font-size: 17px; color: #5F5E5A; line-height: 1.6; }
.department-card {
    background: #FFFFFF;
    border: 1px solid rgba(28,27,25,0.12);
    border-radius: 12px;
    padding: 18px 20px;
    margin-top: 12px;
    margin-bottom: 16px;
}
.locked-card {
    background: #FAECE7;
    border: 1px solid #F09595;
    border-radius: 12px;
    padding: 18px 20px;
    color: #501313;
    line-height: 1.6;
    margin-top: 12px;
    margin-bottom: 16px;
}
.locked-card strong {
    color: #993C1D;
}
.lock-status-card {
    background: #E6F1FB;
    border: 1px solid #8BBBE8;
    border-radius: 10px;
    padding: 10px 12px;
    color: #0C447C;
    font-size: 13px;
    line-height: 1.4;
}

/* Make lock/status messages readable inside the dark sidebar. */
section[data-testid="stSidebar"] .lock-status-card {
    background: #F3F8FF !important;
    border: 1px solid #8BBBE8 !important;
    color: #0C447C !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    line-height: 1.45 !important;
}
section[data-testid="stSidebar"] .lock-status-card * {
    color: #0C447C !important;
}
section[data-testid="stSidebar"] .role-card {
    background: #171F2D !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 10px;
    padding: 10px 12px;
    color: #E8E6E0 !important;
    font-size: 13px;
    line-height: 1.45;
}
section[data-testid="stSidebar"] .role-card strong {
    color: #FFFFFF !important;
}

.instructor-info-card {
    background: #F3F8FF;
    border: 1px solid #8BBBE8;
    border-radius: 10px;
    padding: 12px 14px;
    color: #0C447C;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 8px;
}
.instructor-info-card strong {
    color: #0C447C;
}
.round-scope-card {
    background: #F3F8FF;
    border: 1px solid #8BBBE8;
    border-radius: 10px;
    padding: 12px 14px;
    color: #0C447C;
    font-size: 14px;
    line-height: 1.5;
    margin-bottom: 16px;
}

</style>
""", unsafe_allow_html=True)


# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚚 **Supply Chain Game HAN**")
    st.markdown("---")

    nav_pages = [
        "🏠 Start",
        "📊 Dashboard",
        "📝 Decision Log",
        "💰 Financials",
        "🏁 Final Report",
        "👨‍🏫 Instructor view",
    ]

    for nav_page in nav_pages:
        button_type = "primary" if st.session_state.current_page == nav_page else "secondary"
        locked = is_page_locked(nav_page)
        nav_label = f"🔒 {nav_page}" if locked else nav_page

        if st.button(nav_label, use_container_width=True, type=button_type, disabled=locked):
            st.session_state.current_page = nav_page
            st.rerun()

    page = st.session_state.current_page

    active_locks = get_active_locks()
    if active_locks and not is_instructor_unlocked():
        st.markdown("---")
        st.markdown('<div class="lock-status-card">🔒 Instructor locks active<br>' + ", ".join(active_locks[:4]) + ("..." if len(active_locks) > 4 else "") + '</div>', unsafe_allow_html=True)

    # Instructor mode intentionally bypasses all locks. This button lets the instructor
    # quickly test the student view in the same browser session.
    if is_instructor_unlocked():
        st.markdown("---")
        st.markdown('<div class="lock-status-card">🧑‍🏫 Instructor mode active<br>Locks are bypassed for you.</div>', unsafe_allow_html=True)
        if st.button("👤 Preview as student", use_container_width=True):
            st.session_state.instructor_authenticated = False
            # Stay on the current page so a locked page immediately shows the lock screen.
            st.rerun()

    st.markdown("---")

    st.session_state.team_name = st.text_input("Team name", value=st.session_state.team_name)
    st.session_state.group_name = st.text_input("Group", value=st.session_state.group_name)

    st.markdown(f"**{st.session_state.team_name}** · {st.session_state.group_name}")
    st.markdown(f"Quarter {st.session_state.quarter} of 8")
    st.progress(st.session_state.quarter / 8)
    st.markdown(f"**Score: {st.session_state.score}/100**")
    st.caption("Global Efficiency Score")

    st.markdown("---")
    st.markdown("**Current KPI status**")
    st.caption(f"Profit: {money(st.session_state.net_profit)}")
    st.caption(f"Service level: {st.session_state.service_level}%")
    st.caption(f"ESG: {st.session_state.sustainability_score}/100")
    st.caption(f"Risk: {risk_label(st.session_state.risk_level)}")

    if st.session_state.game_paused:
        st.warning("⏸ Game is paused")


# If a page becomes locked while a student is already on it, show a lock screen.
if is_page_locked(page):
    render_locked_message(f"{page} is locked")
    st.stop()



if page == "🏠 Start":
    st.markdown('<div class="big-title">🚚 Supply Chain Game HAN</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">A supply chain management simulation game about profit, service level, sustainability, inventory and risk.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("### Your role")
        st.markdown(f"""
You are the management team of **{st.session_state.team_name}**.

Each quarter, your team makes decisions for four departments:

- **Purchasing**
- **Operations**
- **Sales**
- **Supply Chain**

Every department decision changes your KPIs. Some decisions are multiple choice, while others require an estimation, such as determining the right stock level with sliders.
        """)

        if st.button("▶️ Start game"):
            st.session_state.game_started = True
            st.session_state.current_page = "📝 Decision Log"
            st.rerun()

    with col2:
        st.markdown('<div class="white-card"><div class="card-label">Game Objectives</div>', unsafe_allow_html=True)
        st.markdown("""
**Main goal:**  
Build the strongest supply chain by Quarter 8.

**Important KPIs:**

- Efficiency Score
- Net Profit
- Service Level
- ESG Score
- Inventory Value
- Lead Time
- Supply Chain Risk
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### Current scenario")
    st.markdown(f"""
<div class="event-banner">
    <div class="event-label">🔴 {st.session_state.event_label}</div>
    <div style="margin-top:4px;">{st.session_state.event}</div>
    <div style="margin-top:6px;"><strong>Meaning:</strong> {get_current_event_note()}</div>
    <div style="margin-top:6px;"><strong>Learning objective:</strong> {get_event_for_quarter(st.session_state.quarter)["learning_objective"]}</div>
</div>
""", unsafe_allow_html=True)


elif page == "📊 Dashboard":
    st.title(f"Quarter {st.session_state.quarter} Overview")

    st.markdown(f"""
    <div class="event-banner">
        <div class="event-label">🔴 {st.session_state.event_label}</div>
        <div style="margin-top:4px;">{st.session_state.event}</div>
        <div style="margin-top:6px;"><strong>Decision context:</strong> {get_current_event_note()}</div>
        <div style="margin-top:6px;"><strong>Learning objective:</strong> {get_event_for_quarter(st.session_state.quarter)["learning_objective"]}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Global Efficiency Score", f"{st.session_state.score}/100", "Dynamic")
    c2.metric("Net Profit", money(st.session_state.net_profit), "Affected by decisions")
    c3.metric("Inventory Value", money(st.session_state.inventory_value), "Holding cost impact", delta_color="inverse")
    c4.metric("Sustainability Rating", sustainability_rating(st.session_state.sustainability_score), f"{st.session_state.sustainability_score}/100 ESG")

    k1, k2, k3 = st.columns(3)
    k1.metric("Service Level", f"{st.session_state.service_level}%", "Delivery reliability")
    k2.metric("Average Lead Time", f"{st.session_state.lead_time_days} days", "Lower is better")
    k3.metric("Supply Chain Risk", f"{st.session_state.risk_level}/100", risk_label(st.session_state.risk_level), delta_color="inverse")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="white-card"><div class="card-label">Inventory Levels</div>', unsafe_allow_html=True)

        inventory = {
            "Raw materials": min(100, max(0, int(st.session_state.inventory_value / 12000))),
            "Work in progress": min(100, max(0, int(st.session_state.service_level * 0.65))),
            "Finished goods": min(100, max(0, int(100 - st.session_state.risk_level * 0.8))),
            "Safety stock": min(100, max(0, int(st.session_state.inventory_value / 15000))),
        }

        for name, pct in inventory.items():
            cols = st.columns([3, 1])
            cols[0].markdown(f"**{name}**")
            cols[1].markdown(f"`{pct}%`")
            st.progress(pct / 100)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="white-card"><div class="card-label">Leaderboard — Current Quarter</div>', unsafe_allow_html=True)

        leaderboard = [
            ("Team Apex", 91, False),
            ("NovaTrade", 88, False),
            ("LogiX Group", 83, False),
            (st.session_state.team_name, st.session_state.score, True),
            ("FastLink", 69, False),
            ("ChainMasters", 61, False),
        ]
        leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)

        for i, (name, score, is_you) in enumerate(leaderboard, start=1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            if is_you:
                st.markdown(f"**{medal} 🔵 {name}** ← you &nbsp;&nbsp; **{score}**")
            else:
                st.markdown(f"{medal} {name} &nbsp;&nbsp; {score}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    col_l2, col_r2 = st.columns(2)

    with col_l2:
        st.markdown('<div class="white-card"><div class="card-label">P&L — Current Quarter Snapshot</div>', unsafe_allow_html=True)

        estimated_cogs = int(st.session_state.revenue * 0.55)
        logistics_costs = int(280000 + st.session_state.lead_time_days * 4000)
        holding_costs = int(st.session_state.inventory_value * 0.08)

        pnl = [
            ("Revenue", money(st.session_state.revenue), True),
            ("Cost of goods sold", money(-estimated_cogs), False),
            ("Logistics costs", money(-logistics_costs), False),
            ("Holding costs", money(-holding_costs), False),
            ("Net profit", money(st.session_state.net_profit), True),
        ]

        for label, val, pos in pnl:
            col_a, col_b = st.columns([3, 2])
            bold = label == "Net profit"
            col_a.markdown(f"{'**' if bold else ''}{label}{'**' if bold else ''}")
            col_b.markdown(
                f"<span style='color:{'#0F6E56' if pos else '#993C1D'};font-family:monospace;'>{'**' if bold else ''}{val}{'**' if bold else ''}</span>",
                unsafe_allow_html=True,
            )

        st.markdown('</div>', unsafe_allow_html=True)

    with col_r2:
        st.markdown('<div class="white-card"><div class="card-label">Sustainability Breakdown</div>', unsafe_allow_html=True)

        sustain = {
            "Carbon emissions": max(0, min(100, st.session_state.sustainability_score - 4)),
            "Supplier ESG rating": max(0, min(100, st.session_state.sustainability_score + 6)),
            "Packaging waste": max(0, min(100, st.session_state.sustainability_score - 12)),
            "Labour practices": max(0, min(100, st.session_state.sustainability_score - 6)),
        }

        for name, val in sustain.items():
            cols = st.columns([3, 1])
            cols[0].markdown(f"**{name}**")
            cols[1].markdown(f"`{val}/100`")
            st.progress(val / 100)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Decision Progress")
    completed = len(st.session_state.completed_games)
    st.progress(completed / 4)
    st.caption(f"{completed}/4 department decisions completed this quarter.")


elif page == "📝 Decision Log":
    st.title("Decision Log")
    st.caption(f"Make one management decision for each department · Q{st.session_state.quarter}")

    if st.session_state.game_paused:
        st.warning("The instructor has paused the game. You can view the departments, but decisions cannot be submitted.")

    st.markdown(f"""
<div class="event-banner">
    <div class="event-label">🔴 Current event</div>
    <div style="margin-top:4px;">{st.session_state.event}</div>
    <div style="margin-top:6px;"><strong>Meaning:</strong> {get_current_event_note()}</div>
    <div style="margin-top:6px;"><strong>Learning objective:</strong> {get_event_for_quarter(st.session_state.quarter)["learning_objective"]}</div>
</div>
""", unsafe_allow_html=True)

    done = st.session_state.completed_games
    departments = ["Purchasing", "Operations", "Sales", "Supply Chain"]

    # If the selected department is locked by instructor settings or by the chosen role,
    # automatically move to the first department that this student is allowed to open.
    if is_department_access_locked(st.session_state.selected_department):
        unlocked_departments = [department for department in departments if not is_department_access_locked(department)]
        if unlocked_departments:
            st.session_state.selected_department = unlocked_departments[0]

    playable_departments = get_playable_departments()
    required_departments = get_required_departments_for_round()

    if not is_instructor_unlocked():
        if len(playable_departments) == 0:
            render_locked_message("No department is currently unlocked for this round")
            st.stop()
        elif len(playable_departments) < 4:
            st.markdown(
                f"""
<div class="round-scope-card">
<strong>{get_round_scope_label()}</strong><br>
Required before finishing: {", ".join(required_departments)}.
</div>
""",
                unsafe_allow_html=True,
            )

    cols = st.columns(4)
    for i, (col, department) in enumerate(zip(cols, departments)):
        locked = is_department_access_locked(department)
        status = "🔒" if locked else ("✅" if department in done else ("🔵" if i == len(done) else "⚪"))
        is_selected = st.session_state.selected_department == department
        button_type = "primary" if is_selected and not locked else "secondary"

        if col.button(
            f"{status} {department}",
            key=f"department_button_{department}",
            use_container_width=True,
            type=button_type,
            disabled=locked,
        ):
            st.session_state.selected_department = department
            st.rerun()

    st.markdown("---")

    department_tab = st.session_state.selected_department

    if is_department_access_locked(department_tab):
        render_locked_message(get_department_lock_reason(department_tab))
        st.stop()

    if department_tab == "Purchasing":
        st.subheader("🏭 Purchasing Department")
        st.markdown('<span class="badge-orange">Supplier strategy</span>', unsafe_allow_html=True)

        tariff_active = st.session_state.active_event_code == "tariff"
        port_disruption = st.session_state.active_event_code in ["rotterdam_strike", "suez_blockage"]

        st.markdown("""
### Current situation
The purchasing department is reviewing the supplier strategy for the next quarter.

The company currently buys many components from a low-cost overseas supplier. This keeps purchase prices low, but recent disruptions have made deliveries less reliable. A European supplier is more expensive, but offers shorter lead times and better reliability. Purchasing can also split the order between both suppliers to reduce dependency.
        """)

        if tariff_active:
            st.warning("Import tariffs are active. Overseas purchasing is more expensive this quarter.")
        if port_disruption:
            st.warning("Sea freight disruption is active. Overseas suppliers have a higher delivery risk.")

        options = {
            "Stay with the low-cost overseas supplier": "Lowest purchase price, but higher exposure to delays, tariffs and supply disruption.",
            "Switch to the reliable European supplier": "Higher purchase cost, but better delivery reliability and lower supply risk.",
            "Split purchasing between both suppliers": "Balanced option: less dependency on one supplier, but slightly higher coordination cost.",
        }

        choice = st.radio(
            "Purchasing decision:",
            list(options.keys()),
            key="purchasing_decision_radio",
            disabled=st.session_state.purchasing_confirmed,
        )

        st.caption(options[choice])

        if st.button(
            "✅ Confirm purchasing decision",
            key="confirm_purchasing",
            disabled=st.session_state.purchasing_confirmed or st.session_state.game_paused,
        ):
            st.session_state.purchasing_confirmed = True
            st.session_state.purchasing_chosen = choice

            if "Purchasing" not in st.session_state.completed_games:
                if choice == "Split purchasing between both suppliers":
                    impact = apply_kpi_change(score=8, profit=-60000, service=5, sustainability=2, lead_time=-2, risk=-8)
                elif choice == "Switch to the reliable European supplier":
                    impact = apply_kpi_change(score=6, profit=-90000, service=7, sustainability=4, lead_time=-4, risk=-9)
                else:
                    impact = apply_kpi_change(
                        score=-5 if port_disruption or tariff_active else -2,
                        profit=50000 if not tariff_active else -90000,
                        inventory=-70000,
                        service=-8 if port_disruption else -4,
                        sustainability=-2,
                        lead_time=6 if port_disruption else 3,
                        risk=10 if port_disruption else 6,
                    )

                record_decision("Purchasing", choice, "Supplier strategy", impact)
                st.session_state.completed_games.append("Purchasing")

        if st.session_state.purchasing_confirmed:
            st.markdown("""
            <div class="result-neutral">
            Decision saved. The purchasing impact is included in the quarter results. Review the complete KPI effect after finishing the quarter.
            </div>
            """, unsafe_allow_html=True)

    elif department_tab == "Operations":
        st.subheader("⚙️ Operations Department")
        st.markdown('<span class="badge-green">Stock determination</span>', unsafe_allow_html=True)

        demand_pressure = st.session_state.active_event_code in ["demand_surge", "pandemic", "market_volatility"]

        st.markdown("""
### Current situation
Operations is reviewing the stock levels for three products. Some products are running low, while others may already have more stock than needed.

For each product, determine the **target stock level for next period**.  
A stock level that is too low can create stockouts and lower service level.  
A stock level that is too high increases holding costs and obsolete inventory risk.

The exact KPI result is **not shown immediately**. It will be applied and shown after finishing the quarter.
        """)

        if demand_pressure:
            st.warning("Demand uncertainty is high this quarter. The required safety stock is higher than normal.")

        products = get_operations_products()
        render_operations_tips(products)

        product_table = []
        for product in products:
            status, tip = get_stock_status(product)
            product_table.append(
                {
                    "Product": product["Product"],
                    "Current stock": f"{product['Current stock']:,}",
                    "Expected demand": f"{product['Expected demand']:,}",
                    "Recommended safety stock": f"{product['Safety stock']:,}",
                    "Theoretical target": f"{product['Expected demand'] + product['Safety stock']:,}",
                    "Status": status,
                    "Tip": tip,
                }
            )

        st.markdown("### Product information")
        st.dataframe(pd.DataFrame(product_table), use_container_width=True, hide_index=True)

        st.markdown("### Set target stock level")

        slider_values = {}

        for product in products:
            name = product["Product"]
            target = product["Expected demand"] + product["Safety stock"]
            min_value = 0
            max_value = int(target * 1.8)
            default_value = int(product["Current stock"])

            slider_values[name] = st.slider(
                f"{name} target stock",
                min_value=min_value,
                max_value=max_value,
                value=min(default_value, max_value),
                step=500,
                disabled=st.session_state.operations_confirmed or st.session_state.game_paused,
                key=f"stock_slider_{name}_{st.session_state.quarter}",
            )

        if st.button(
            "✅ Confirm operations stock plan",
            key="confirm_operations_stock",
            disabled=st.session_state.operations_confirmed or st.session_state.game_paused,
        ):
            impact = calculate_stock_slider_impact(slider_values)

            st.session_state.operations_confirmed = True
            st.session_state.operations_stock_settings = slider_values
            st.session_state.operations_pending_impact = impact
            st.session_state.operations_chosen = "Stock targets: " + ", ".join(
                [f"{product} {amount:,}" for product, amount in slider_values.items()]
            )

            if "Operations" not in st.session_state.completed_games:
                st.session_state.completed_games.append("Operations")

            st.success("Operations stock plan saved. The KPI consequences will be shown after finishing the quarter.")

        if st.session_state.operations_confirmed:
            st.markdown("""
            <div class="result-neutral">
            ✅ <strong>Stock plan saved.</strong><br><br>
            The result is hidden for now. After finishing the quarter, the game will compare your target stock levels with demand and safety stock. 
            If stock is too low, service level and risk will be affected. If stock is too high, profit and inventory value will be affected.
            </div>
            """, unsafe_allow_html=True)

    elif department_tab == "Sales":
        st.subheader("📈 Sales Department")
        st.markdown('<span class="badge-blue">Customer demand</span>', unsafe_allow_html=True)

        demand_shock = st.session_state.active_event_code in ["pandemic", "demand_surge", "market_volatility"]

        st.markdown("""
### Current situation
Sales is negotiating with a large customer. The customer wants faster delivery and higher volumes next quarter.

Accepting the request could increase revenue, but it also creates pressure on purchasing, operations and the supply chain. The sales team must decide how ambitious the commercial promise should be.
        """)

        if demand_shock:
            st.warning("Demand uncertainty is high. Promising too much may create operational pressure later.")

        options = {
            "Accept all extra customer demand": "Highest revenue potential, but high pressure on production and delivery reliability.",
            "Accept part of the extra demand": "Balanced commercial growth with lower operational risk.",
            "Reject the extra demand": "Low operational risk, but missed revenue opportunity.",
        }

        choice = st.radio(
            "Sales decision:",
            list(options.keys()),
            key="sales_decision_radio",
            disabled=st.session_state.sales_confirmed,
        )

        st.caption(options[choice])

        if st.button(
            "✅ Confirm sales decision",
            key="confirm_sales",
            disabled=st.session_state.sales_confirmed or st.session_state.game_paused,
        ):
            st.session_state.sales_confirmed = True
            st.session_state.sales_chosen = choice

            if "Sales" not in st.session_state.completed_games:
                if choice == "Accept part of the extra demand":
                    impact = apply_kpi_change(score=8 if demand_shock else 7, profit=90000, revenue=160000, service=3, risk=-2)
                elif choice == "Accept all extra customer demand":
                    impact = apply_kpi_change(
                        score=-4 if demand_shock else -2,
                        profit=130000,
                        revenue=260000,
                        service=-9 if demand_shock else -7,
                        lead_time=5 if demand_shock else 4,
                        risk=9 if demand_shock else 7,
                    )
                else:
                    impact = apply_kpi_change(score=-3, profit=-60000, revenue=-140000, service=2, risk=-3)

                record_decision("Sales", choice, "Customer demand", impact)
                st.session_state.completed_games.append("Sales")

        if st.session_state.sales_confirmed:
            st.markdown("""
            <div class="result-neutral">
            Decision saved. Review the full KPI effect after finishing the quarter.
            </div>
            """, unsafe_allow_html=True)

    elif department_tab == "Supply Chain":
        st.subheader("🚚 Supply Chain Department")
        st.markdown('<span class="badge-red">Network resilience</span>', unsafe_allow_html=True)

        sea_disrupted = st.session_state.active_event_code in ["rotterdam_strike", "suez_blockage"]
        labour_disrupted = st.session_state.active_event_code == "labour_strike"

        st.markdown("""
### Current situation
The supply chain department is reviewing the logistics plan for the next quarter.

The current network is cost-efficient, but disruptions are increasing. The team can keep using the cheapest route, switch to a faster route, or redesign the logistics plan with a more balanced route and higher resilience.
        """)

        if sea_disrupted:
            st.warning("Sea freight disruption is active. Sea routes have a higher delay risk.")
        if labour_disrupted:
            st.warning("Labour strikes are active. Road logistics are less reliable this quarter.")

        options = {
            "Keep the cheapest transport route": "Lowest transport cost, but higher risk of delays and stockouts.",
            "Use the fastest transport route": "Best for delivery speed, but expensive and less sustainable.",
            "Use a balanced multimodal route": "Moderate cost with better balance between speed, risk and sustainability.",
        }

        choice = st.radio(
            "Supply Chain decision:",
            list(options.keys()),
            key="supply_chain_decision_radio",
            disabled=st.session_state.supply_chain_confirmed,
        )

        st.caption(options[choice])

        if st.button(
            "✅ Confirm supply chain decision",
            key="confirm_supply_chain",
            disabled=st.session_state.supply_chain_confirmed or st.session_state.game_paused,
        ):
            st.session_state.supply_chain_confirmed = True
            st.session_state.supply_chain_chosen = choice

            if "Supply Chain" not in st.session_state.completed_games:
                if choice == "Use a balanced multimodal route":
                    impact = apply_kpi_change(score=8, profit=-50000, service=5, sustainability=4, lead_time=-2, risk=-7)
                elif choice == "Use the fastest transport route":
                    impact = apply_kpi_change(score=-1, profit=-120000, service=8, sustainability=-8, lead_time=-6, risk=-3)
                else:
                    impact = apply_kpi_change(
                        score=-5 if sea_disrupted or labour_disrupted else 2,
                        profit=-90000 if sea_disrupted else 30000,
                        inventory=-80000 if sea_disrupted else 0,
                        service=-9 if sea_disrupted or labour_disrupted else 1,
                        sustainability=3,
                        lead_time=10 if sea_disrupted or labour_disrupted else 2,
                        risk=9 if sea_disrupted or labour_disrupted else 2,
                    )

                record_decision("Supply Chain", choice, "Network resilience", impact)
                st.session_state.completed_games.append("Supply Chain")

        if st.session_state.supply_chain_confirmed:
            st.markdown("""
            <div class="result-neutral">
            Decision saved. Review the full KPI effect after finishing the quarter.
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    completed = len(st.session_state.completed_games)
    required_departments = get_required_departments_for_round()
    completed_required = get_completed_required_departments()
    missing_required = [department for department in required_departments if department not in st.session_state.completed_games]

    if len(get_playable_departments()) == 0 and not is_instructor_unlocked():
        st.warning("No departments are currently unlocked. Ask the instructor to unlock at least one department.")
    elif not is_round_complete():
        st.info(
            f"Complete the required department(s) before finishing the round. "
            f"Progress: {len(completed_required)}/{len(required_departments)} completed. "
            f"Still needed: {', '.join(missing_required)}."
        )
    else:
        if st.session_state.get("lock_finish_quarter", False) and not is_instructor_unlocked():
            st.warning("The instructor has locked the finish button. Wait until the class is ready to review the results.")
            st.button("🔒 Finish round locked", type="primary", disabled=True)
        else:
            if len(required_departments) == 1:
                st.success(f"{required_departments[0]} has been completed. You can now finish this department round.")
                button_label = "➡️ Finish department round and view summary"
            elif len(required_departments) < 4:
                st.success("All unlocked departments have been completed. You can now finish this partial round.")
                button_label = "➡️ Finish partial round and view summary"
            else:
                st.success("All four department decisions have been completed. You can now finish this quarter.")
                button_label = "➡️ Finish quarter and view summary"

            if st.button(button_label, type="primary"):
                show_quarter_summary()


elif page == "📋 Quarter Summary":
    st.title(f"Quarter {st.session_state.quarter} Summary")
    st.caption("Review this quarter first. Then continue to the next quarter.")

    decisions = current_quarter_decisions()
    completed = len(st.session_state.completed_games)

    st.markdown(f"""
<div class="event-banner">
    <div class="event-label">Quarter context</div>
    <div style="margin-top:4px;">{st.session_state.event}</div>
    <div style="margin-top:6px;"><strong>Meaning:</strong> {get_current_event_note()}</div>
    <div style="margin-top:6px;"><strong>Learning objective:</strong> {get_event_for_quarter(st.session_state.quarter)["learning_objective"]}</div>
</div>
""", unsafe_allow_html=True)

    col_progress, col_status = st.columns([2, 1])

    with col_progress:
        st.markdown("### Department progress")
        required_departments = get_required_departments_for_round()
        completed_required = get_completed_required_departments()
        progress_value = len(completed_required) / len(required_departments) if required_departments else 0
        st.progress(progress_value)
        st.caption(
            f"{len(completed_required)}/{len(required_departments)} required department(s) completed: "
            f"{', '.join(required_departments)}"
        )

    with col_status:
        if is_round_complete():
            if len(get_required_departments_for_round()) < 4:
                st.success("Partial department round completed.")
            else:
                st.success("Quarter completed.")
        else:
            st.warning("Round not fully completed.")

    st.markdown("---")

    st.markdown("### KPI result")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Efficiency Score", f"{st.session_state.score}/100")
    c2.metric("Net Profit", money(st.session_state.net_profit))
    c3.metric("Service Level", f"{st.session_state.service_level}%")
    c4.metric("ESG Rating", sustainability_rating(st.session_state.sustainability_score))

    c5, c6, c7 = st.columns(3)
    c5.metric("Inventory Value", money(st.session_state.inventory_value))
    c6.metric("Lead Time", f"{st.session_state.lead_time_days} days")
    c7.metric("Supply Chain Risk", f"{st.session_state.risk_level}/100", risk_label(st.session_state.risk_level))

    st.markdown("---")

    st.markdown("### Quarter interpretation")

    title, explanation = strategy_type()

    col_profile, col_comment = st.columns([1, 1.4])

    with col_profile:
        st.markdown(f"""
<div class="white-card">
<div class="card-label">Strategic profile</div>
<h3>{title}</h3>
<p class="kpi-note">{explanation}</p>
</div>
""", unsafe_allow_html=True)

    with col_comment:
        st.markdown(f"""
<div class="white-card">
<div class="card-label">Management summary</div>
<p class="kpi-note">{quarter_kpi_comment()}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### Department decisions this quarter")

    if decisions:
        show_clean_decision_table(decisions)
    else:
        st.info("No decisions have been made in this quarter yet.")

    if st.session_state.get("lock_peer_comparison", False) and not is_instructor_unlocked():
        st.markdown("---")
        render_locked_message("Class comparison is locked")
    else:
        show_peer_comparison()

    st.markdown("---")

    st.markdown("### Group reflection")
    st.markdown("""
Use these questions to discuss the quarter with your group:

1. Which department decision had the strongest positive or negative KPI impact?
2. Did your team focus more on profit, service level, sustainability or risk?
3. Did the departments support each other, or did one department create pressure for another?
4. What would you change in the next quarter?
    """)

    st.markdown("---")

    if st.session_state.quarter < 8:
        if st.button("➡️ Continue to next quarter", type="primary"):
            continue_to_next_quarter()
    else:
        if st.button("🏁 Go to final report", type="primary"):
            continue_to_next_quarter()


elif page == "💰 Financials":
    st.title("Financial Statements")
    st.caption("Auto-generated based on current KPI performance and player decisions.")

    col_fl, col_fr = st.columns(2)

    with col_fl:
        st.markdown("**Income Statement — Year to Date**")

        total_previous_revenue = sum(row["Revenue"] for row in st.session_state.history)
        total_previous_profit = sum(row["Net Profit"] for row in st.session_state.history)

        current_quarter_in_history = f"Q{st.session_state.quarter}" in [row["Quarter"] for row in st.session_state.history]

        if current_quarter_in_history:
            total_revenue_ytd = total_previous_revenue
            total_profit_ytd = total_previous_profit
        else:
            total_revenue_ytd = total_previous_revenue + st.session_state.revenue
            total_profit_ytd = total_previous_profit + st.session_state.net_profit

        estimated_cogs = int(total_revenue_ytd * 0.56)
        estimated_logistics = int(900000 + st.session_state.lead_time_days * 8000)
        estimated_holding = int(st.session_state.inventory_value * 0.08)

        income = [
            ("Current Quarter Revenue", money(st.session_state.revenue), True),
            ("Total Revenue YTD", money(total_revenue_ytd), True),
            ("Estimated COGS", money(-estimated_cogs), False),
            ("Estimated Logistics Costs", money(-estimated_logistics), False),
            ("Estimated Holding Costs", money(-estimated_holding), False),
            ("Net Profit YTD", money(total_profit_ytd), True),
        ]

        for label, val, pos in income:
            c1, c2 = st.columns([3, 2])
            bold = label in ("Total Revenue YTD", "Net Profit YTD")
            c1.markdown(f"{'**' if bold else ''}{label}{'**' if bold else ''}")
            c2.markdown(
                f"<span style='color:{'#0F6E56' if pos else '#993C1D'};font-family:monospace;'>{'**' if bold else ''}{val}{'**' if bold else ''}</span>",
                unsafe_allow_html=True,
            )

    with col_fr:
        st.markdown("**Balance Sheet — Current Situation**")

        cash = max(0, 2100000 + st.session_state.net_profit - 1240000)
        accounts_receivable = int(st.session_state.revenue * 0.14)
        accounts_payable = int(st.session_state.revenue * 0.09)
        short_debt = 150000
        net_equity = cash + st.session_state.inventory_value + accounts_receivable - accounts_payable - short_debt

        balance = [
            ("— ASSETS —", "", None),
            ("Cash", money(cash), True),
            ("Inventory", money(st.session_state.inventory_value), True),
            ("Accounts Receivable", money(accounts_receivable), True),
            ("— LIABILITIES —", "", None),
            ("Accounts Payable", money(-accounts_payable), False),
            ("Short-term Debt", money(-short_debt), False),
            ("Net Equity", money(net_equity), True),
        ]

        for label, val, pos in balance:
            c1, c2 = st.columns([3, 2])
            if pos is None:
                c1.markdown(f"**{label}**")
            else:
                bold = label == "Net Equity"
                c1.markdown(f"{'**' if bold else ''}{label}{'**' if bold else ''}")
                c2.markdown(
                    f"<span style='color:{'#0F6E56' if pos else '#993C1D'};font-family:monospace;'>{'**' if bold else ''}{val}{'**' if bold else ''}</span>",
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.markdown("### Quarter-by-Quarter Performance")

    performance_rows = []

    for row in st.session_state.history:
        performance_rows.append(row.copy())

    current_q = f"Q{st.session_state.quarter}"

    if current_q not in [row["Quarter"] for row in st.session_state.history]:
        performance_rows.append(
            {
                "Quarter": f"{current_q} current",
                "Revenue": st.session_state.revenue,
                "Net Profit": st.session_state.net_profit,
                "Efficiency Score": st.session_state.score,
                "Service Level": st.session_state.service_level,
                "ESG Score": st.session_state.sustainability_score,
                "Inventory Value": st.session_state.inventory_value,
                "Risk Level": st.session_state.risk_level,
                "Lead Time": st.session_state.lead_time_days,
            }
        )

    formatted_rows = []
    for row in performance_rows:
        formatted_rows.append(
            {
                "Quarter": row["Quarter"],
                "Revenue": money(row["Revenue"]),
                "Net Profit": money(row["Net Profit"]),
                "Efficiency Score": row["Efficiency Score"],
                "Service Level": f"{row['Service Level']}%",
                "ESG Score": row["ESG Score"],
                "Inventory Value": money(row["Inventory Value"]),
                "Risk Level": row["Risk Level"],
                "Lead Time": row["Lead Time"],
            }
        )

    st.dataframe(pd.DataFrame(formatted_rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### KPI Charts")

    chart_df = pd.DataFrame(performance_rows).set_index("Quarter")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("**Net Profit per Quarter**")
        st.line_chart(chart_df["Net Profit"])

        st.markdown("**Service Level per Quarter**")
        st.line_chart(chart_df["Service Level"])

    with col_chart2:
        st.markdown("**ESG Score per Quarter**")
        st.line_chart(chart_df["ESG Score"])

        st.markdown("**Risk Level per Quarter**")
        st.line_chart(chart_df["Risk Level"])

    st.markdown("---")
    st.markdown("### Decision History")

    if st.session_state.decision_log:
        show_clean_decision_table(st.session_state.decision_log)
    else:
        st.info("No decisions have been logged yet.")


elif page == "🏁 Final Report":
    st.title("Final Company Report")

    title, explanation = strategy_type()

    st.markdown(f"""
<div class="white-card">
<div class="card-label">Final performance profile</div>
<h2>{title}</h2>
<p class="kpi-note">{explanation}</p>
</div>
""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Final Score", f"{st.session_state.score}/100")
    c2.metric("Net Profit", money(st.session_state.net_profit))
    c3.metric("Service Level", f"{st.session_state.service_level}%")
    c4.metric("ESG Rating", sustainability_rating(st.session_state.sustainability_score))

    c5, c6, c7 = st.columns(3)
    c5.metric("Inventory Value", money(st.session_state.inventory_value))
    c6.metric("Lead Time", f"{st.session_state.lead_time_days} days")
    c7.metric("Risk Level", f"{st.session_state.risk_level}/100", risk_label(st.session_state.risk_level))

    st.markdown("---")

    if st.session_state.quarter < 8:
        st.info("This is a preview. The official final report is completed after Quarter 8.")
    else:
        st.success("The simulation has reached Quarter 8. This is the final performance report.")

    st.markdown("### Final interpretation")

    if st.session_state.score >= 85:
        st.markdown("🏆 **Excellent performance.** Your team created a strong and resilient supply chain.")
    elif st.session_state.score >= 70:
        st.markdown("✅ **Good performance.** Your team managed most trade-offs well, but there is still room for improvement.")
    elif st.session_state.score >= 55:
        st.markdown("⚠️ **Average performance.** Your team survived, but several decisions hurt profit, service or risk.")
    else:
        st.markdown("❌ **Weak performance.** Your supply chain strategy needs major improvement.")

    show_peer_comparison()

    st.markdown("---")
    st.markdown("### Complete decision history")

    if st.session_state.decision_log:
        show_clean_decision_table(st.session_state.decision_log)
    else:
        st.info("No decisions have been logged yet.")


elif page == "👨‍🏫 Instructor view":
    st.title("Instructor — God Mode")
    st.markdown('<span class="badge-red">Instructor only</span>', unsafe_allow_html=True)

    if "instructor_authenticated" not in st.session_state:
        st.session_state.instructor_authenticated = False

    if not st.session_state.instructor_authenticated:
        st.markdown("### 🔒 Instructor Access")
        st.markdown("This area is restricted to instructors. Please enter the password to continue.")

        pwd_input = st.text_input("Password", type="password", placeholder="Enter instructor password")

        if st.button("Unlock", type="primary"):
            if pwd_input == "Oliver123":
                st.session_state.instructor_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

        st.stop()

    logout_col, preview_col, _ = st.columns([1, 1, 2])
    if logout_col.button("🔒 Lock instructor view again"):
        st.session_state.instructor_authenticated = False
        st.rerun()
    if preview_col.button("👤 Preview as student"):
        st.session_state.instructor_authenticated = False
        st.session_state.current_page = "🏠 Start"
        st.rerun()

    col_ev, col_ctrl = st.columns([1, 1])

    with col_ev:
        st.markdown("### 🌍 Trigger a Global Event")

        events = {
            "Rotterdam port strike": {
                "code": "rotterdam_strike",
                "label": "Active Black Swan",
                "desc": "Port strike in Rotterdam — sea freight lead times +14 days.",
                "kpi": {"lead_time": 7, "risk": 8, "service": -3},
            },
            "Suez Canal blockage": {
                "code": "suez_blockage",
                "label": "Supply disruption",
                "desc": "All sea freight routes are delayed by a global canal blockage.",
                "kpi": {"lead_time": 10, "risk": 12, "service": -5},
            },
            "Factory fire — Taiwan": {
                "code": "taiwan_fire",
                "label": "Production crisis",
                "desc": "Semiconductor supply reduced by 40%.",
                "kpi": {"inventory": -120000, "risk": 15, "service": -8},
            },
            "Currency shock": {
                "code": "currency_shock",
                "label": "Financial shock",
                "desc": "EUR/USD moves 15% against all teams.",
                "kpi": {"profit": -150000, "risk": 8},
            },
            "Pandemic scenario": {
                "code": "pandemic",
                "label": "Demand shock",
                "desc": "Medical demand +200%, consumer goods −30%.",
                "kpi": {"revenue": -180000, "inventory": 90000, "risk": 10},
            },
            "Import tariff hike 20%": {
                "code": "tariff",
                "label": "Policy change",
                "desc": "All foreign sourcing costs increase by 20%.",
                "kpi": {"profit": -120000, "risk": 9},
            },
            "Labour strike — logistics hubs": {
                "code": "labour_strike",
                "label": "Ops disruption",
                "desc": "All road freight delayed by 1 week globally.",
                "kpi": {"lead_time": 7, "service": -6, "risk": 10},
            },
        }

        for name, info in events.items():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{name}**  \n{info['desc']}")

            if c2.button("Trigger", key=f"ev_{name}"):
                st.session_state.manual_event_override = True
                st.session_state.active_event_code = info["code"]
                st.session_state.event_label = f"⚡ {info['label']}"
                st.session_state.event = info["desc"]

                impact = apply_kpi_change(
                    profit=info["kpi"].get("profit", 0),
                    revenue=info["kpi"].get("revenue", 0),
                    inventory=info["kpi"].get("inventory", 0),
                    service=info["kpi"].get("service", 0),
                    sustainability=info["kpi"].get("sustainability", 0),
                    lead_time=info["kpi"].get("lead_time", 0),
                    risk=info["kpi"].get("risk", 0),
                )

                record_decision("Instructor event", name, "Black swan event", impact)
                st.success(f"✅ Event triggered: {name}. KPI impact applied.")

    with col_ctrl:
        render_lock_panel()

        st.markdown("---")
        st.markdown("### ⚙️ Game Controls")

        st.session_state.difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
            index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty),
        )

        st.caption(f"Forecast tolerance: ±{get_forecast_tolerance()}%")

        col_p1, col_p2 = st.columns(2)

        if col_p1.button("⏸ Pause game" if not st.session_state.game_paused else "▶️ Resume game"):
            st.session_state.game_paused = not st.session_state.game_paused
            status = "paused" if st.session_state.game_paused else "resumed"
            st.info(f"Game {status}.")

        if col_p2.button("⏭ Advance quarter"):
            show_quarter_summary()

        st.markdown("---")

        if st.button("🔄 Reset entire game"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")
        st.markdown("### 📊 Current Team Performance")

        teams = [
            {"Team": "Team Apex", "Score": 91, "Profit": "$1.82M", "ESG": "A", "Service": "94%"},
            {"Team": "NovaTrade", "Score": 88, "Profit": "$1.71M", "ESG": "B+", "Service": "91%"},
            {"Team": "LogiX Group", "Score": 83, "Profit": "$1.58M", "ESG": "B", "Service": "89%"},
            {
                "Team": f"⭐ {st.session_state.team_name}",
                "Score": st.session_state.score,
                "Profit": money(st.session_state.net_profit),
                "ESG": sustainability_rating(st.session_state.sustainability_score),
                "Service": f"{st.session_state.service_level}%",
            },
            {"Team": "FastLink", "Score": 69, "Profit": "$1.10M", "ESG": "C+", "Service": "78%"},
            {"Team": "ChainMasters", "Score": 61, "Profit": "−$220k", "ESG": "C", "Service": "67%"},
        ]

        st.dataframe(pd.DataFrame(teams), use_container_width=True, hide_index=True)

        st.markdown("### Current KPI Values")

        current_kpis = {
            "KPI": [
                "Revenue",
                "Net Profit",
                "Inventory Value",
                "Service Level",
                "Sustainability Score",
                "Lead Time",
                "Supply Chain Risk",
                "Active Event",
                "Difficulty",
                "Round scope",
                "Playable departments",
                "Learning Objective",
            ],
            "Value": [
                money(st.session_state.revenue),
                money(st.session_state.net_profit),
                money(st.session_state.inventory_value),
                f"{st.session_state.service_level}%",
                f"{st.session_state.sustainability_score}/100",
                f"{st.session_state.lead_time_days} days",
                f"{st.session_state.risk_level}/100",
                st.session_state.event_label,
                st.session_state.difficulty,
                get_round_scope_label(),
                ", ".join(get_playable_departments()) if get_playable_departments() else "None",
                get_event_for_quarter(st.session_state.quarter)["learning_objective"],
            ],
        }

        st.dataframe(pd.DataFrame(current_kpis), use_container_width=True, hide_index=True)
