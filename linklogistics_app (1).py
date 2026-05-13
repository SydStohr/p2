import streamlit as st
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Game HAN",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ───────────────────────────────────────────────────
defaults = {
    # General
    "team_name": "GreenRoute Co.",
    "group_name": "Group 4",
    "score": 74,
    "quarter": 3,
    "difficulty": "Medium",
    "current_page": "🏠 Start",

    # Dynamic KPIs
    "revenue": 3800000,
    "net_profit": 1240000,
    "inventory_value": 860000,
    "service_level": 87,
    "sustainability_score": 76,
    "lead_time_days": 14,
    "risk_level": 42,

    # Event system
    "event": "Port strike in Rotterdam — sea freight lead times +14 days.",
    "event_label": "Active Black Swan",
    "active_event_code": "rotterdam_strike",

    # Department decision state
    "purchasing_chosen": None,
    "purchasing_confirmed": False,
    "operations_chosen": None,
    "operations_confirmed": False,
    "sales_chosen": None,
    "sales_confirmed": False,
    "supply_chain_chosen": None,
    "supply_chain_confirmed": False,

    # Game control
    "game_started": False,
    "game_paused": False,
    "completed_games": [],

    # Decision log
    "decision_log": [],

    # History
    "history": [
        {
            "Quarter": "Q1",
            "Revenue": 3200000,
            "Net Profit": 900000,
            "Efficiency Score": 62,
            "Service Level": 78,
            "ESG Score": 68,
            "Inventory Value": 720000,
            "Risk Level": 52,
            "Lead Time": 18,
        },
        {
            "Quarter": "Q2",
            "Revenue": 3550000,
            "Net Profit": 1030000,
            "Efficiency Score": 68,
            "Service Level": 82,
            "ESG Score": 72,
            "Inventory Value": 790000,
            "Risk Level": 47,
            "Lead Time": 16,
        },
    ],
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helper functions ─────────────────────────────────────────────────────────
def money(value):
    """Formats money values neatly."""
    sign = "−" if value < 0 else ""
    value = abs(int(value))

    if value >= 1000000:
        return f"{sign}${value / 1000000:.2f}M"
    elif value >= 1000:
        return f"{sign}${value / 1000:.0f}k"
    else:
        return f"{sign}${value}"


def sustainability_rating(score):
    """Converts ESG score to a rating."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C+"
    else:
        return "C"


def risk_label(score):
    """Converts risk score to a text label."""
    if score <= 30:
        return "Low"
    elif score <= 60:
        return "Medium"
    else:
        return "High"


def strategy_type():
    """Gives the team a strategy type based on KPI values."""
    profit = st.session_state.net_profit
    service = st.session_state.service_level
    esg = st.session_state.sustainability_score
    risk = st.session_state.risk_level
    inventory = st.session_state.inventory_value

    if service >= 90 and risk <= 35:
        return "Resilient Strategist", "You protected delivery reliability and reduced supply chain risk."
    elif esg >= 85:
        return "Green Leader", "You made sustainable choices and improved ESG performance."
    elif profit >= 1350000 and risk >= 55:
        return "Risk Taker", "You protected short-term profit but accepted higher supply chain risk."
    elif inventory >= 1050000:
        return "Inventory Hoarder", "You reduced stockout risk, but inventory and holding costs are becoming high."
    elif profit >= 1350000:
        return "Cost Controller", "You controlled costs well and protected financial performance."
    else:
        return "Balanced Operator", "You made balanced decisions across profit, service, ESG and risk."


def get_forecast_tolerance():
    if st.session_state.difficulty == "Easy":
        return 20
    elif st.session_state.difficulty == "Hard":
        return 10
    return 15


def apply_kpi_change(
    score=0,
    profit=0,
    revenue=0,
    inventory=0,
    service=0,
    sustainability=0,
    lead_time=0,
    risk=0,
):
    """Applies KPI changes after a player decision."""
    st.session_state.score = max(0, min(100, st.session_state.score + score))
    st.session_state.net_profit += profit
    st.session_state.revenue += revenue
    st.session_state.inventory_value = max(0, st.session_state.inventory_value + inventory)
    st.session_state.service_level = max(0, min(100, st.session_state.service_level + service))
    st.session_state.sustainability_score = max(0, min(100, st.session_state.sustainability_score + sustainability))
    st.session_state.lead_time_days = max(1, st.session_state.lead_time_days + lead_time)
    st.session_state.risk_level = max(0, min(100, st.session_state.risk_level + risk))

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
    """Stores decision history for the summary page."""
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
    """Saves the current quarter results to history before advancing."""
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
    """Resets all decision confirmations for a new quarter."""
    st.session_state.purchasing_chosen = None
    st.session_state.purchasing_confirmed = False
    st.session_state.operations_chosen = None
    st.session_state.operations_confirmed = False
    st.session_state.sales_chosen = None
    st.session_state.sales_confirmed = False
    st.session_state.supply_chain_chosen = None
    st.session_state.supply_chain_confirmed = False
    st.session_state.completed_games = []


def show_quarter_summary():
    """Saves the current quarter and opens the hidden Quarter Summary screen."""
    add_current_quarter_to_history()
    st.session_state.current_page = "📋 Quarter Summary"
    st.rerun()


def continue_to_next_quarter():
    """Moves from the Quarter Summary to the next playable quarter."""
    if st.session_state.quarter < 8:
        st.session_state.quarter += 1

        # Small automatic market change for the new quarter
        st.session_state.revenue = int(st.session_state.revenue * 1.04)
        st.session_state.net_profit = int(st.session_state.net_profit * 1.02)

        # Slightly normalize some KPIs
        st.session_state.lead_time_days = max(8, int(st.session_state.lead_time_days * 0.95))
        st.session_state.risk_level = max(20, int(st.session_state.risk_level * 0.95))

        reset_quarter_games()
        st.session_state.current_page = "📝 Decision Log"
    else:
        st.session_state.current_page = "🏁 Final Report"

    st.rerun()


def current_quarter_decisions():
    return [
        row for row in st.session_state.decision_log
        if row["Quarter"] == f"Q{st.session_state.quarter}"
    ]


def make_decision_table(rows):
    """Formats decision log for a cleaner display."""
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


def make_decision_dataframe(rows):
    """Creates a dataframe for a neater Streamlit table."""
    return pd.DataFrame(make_decision_table(rows))


def show_clean_decision_table(rows):
    """Displays the decision log in a wider and cleaner dataframe."""
    df = make_decision_dataframe(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Quarter": st.column_config.TextColumn("Quarter", width="small"),
            "Department": st.column_config.TextColumn("Department", width="medium"),
            "Decision": st.column_config.TextColumn("Decision", width="large"),
            "Concept": st.column_config.TextColumn("Concept", width="medium"),
            "Score": st.column_config.NumberColumn("Score", width="small"),
            "Profit": st.column_config.TextColumn("Profit", width="small"),
            "Revenue": st.column_config.TextColumn("Revenue", width="small"),
            "Inventory": st.column_config.TextColumn("Inventory", width="small"),
            "Service": st.column_config.TextColumn("Service", width="small"),
            "ESG": st.column_config.TextColumn("ESG", width="small"),
            "Lead Time": st.column_config.TextColumn("Lead Time", width="small"),
            "Risk": st.column_config.TextColumn("Risk", width="small"),
        },
    )


def quarter_kpi_comment():
    """Creates a short readable quarter summary."""
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

    if code == "rotterdam_strike":
        return "Sea freight through Rotterdam is disrupted. Alternative routes and reliable suppliers become more attractive."
    elif code == "suez_blockage":
        return "Global sea freight is disrupted. Transport and supply chain decisions should avoid heavy dependence on sea routes."
    elif code == "tariff":
        return "Foreign sourcing is more expensive. Purchasing decisions should consider local alternatives or split sourcing."
    elif code == "taiwan_fire":
        return "Component availability is low. Inventory and supplier reliability are extra important."
    elif code == "currency_shock":
        return "Currency movement hurts margins. Cost control and pricing decisions matter more."
    elif code == "pandemic":
        return "Demand is unstable. Sales promises and inventory levels should be managed carefully."
    elif code == "labour_strike":
        return "Road logistics are delayed. Lead time and service level are under pressure."
    return "No special event active."


# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { 
    font-family: 'DM Sans', sans-serif; 
}

[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid rgba(28,27,25,0.12);
    border-radius: 12px;
    padding: 16px 18px;
}

section[data-testid="stSidebar"] {
    background: #1C1B19 !important;
}
section[data-testid="stSidebar"] * { 
    color: #E8E6E0 !important; 
}

.stButton > button {
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 14px;
    padding: 8px 18px;
    border: 1px solid rgba(28,27,25,0.2);
    transition: all 0.15s;
}
.stButton > button:hover { 
    border-color: rgba(28,27,25,0.5); 
}

.stProgress > div > div { 
    background-color: #185FA5 !important; 
}

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
.card-label {
    font-size: 11px; 
    font-weight: 600; 
    text-transform: uppercase;
    letter-spacing: 0.6px; 
    color: #888780; 
    margin-bottom: 12px;
}
.kpi-note {
    color: #5F5E5A;
    font-size: 13px;
    line-height: 1.5;
}
.badge-blue {
    background:#E6F1FB;
    color:#0C447C;
    border-radius:6px;
    padding:3px 9px;
    font-size:12px;
    font-weight:500;
}
.badge-orange {
    background:#FAEEDA;
    color:#633806;
    border-radius:6px;
    padding:3px 9px;
    font-size:12px;
    font-weight:500;
}
.badge-red {
    background:#FAECE7;
    color:#993C1D;
    border-radius:6px;
    padding:3px 9px;
    font-size:12px;
    font-weight:500;
}
.badge-green {
    background:#EAF3DE;
    color:#0F6E56;
    border-radius:6px;
    padding:3px 9px;
    font-size:12px;
    font-weight:500;
}
.big-title {
    font-size: 44px;
    font-weight: 700;
    margin-bottom: 4px;
}
.subtitle {
    font-size: 17px;
    color: #5F5E5A;
    line-height: 1.6;
}
.department-card {
    background: #FFFFFF;
    border: 1px solid rgba(28,27,25,0.12);
    border-radius: 12px;
    padding: 18px 20px;
    margin-top: 12px;
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

        if st.button(nav_page, use_container_width=True, type=button_type):
            st.session_state.current_page = nav_page
            st.rerun()

    page = st.session_state.current_page

    st.markdown("---")

    st.session_state.team_name = st.text_input(
        "Team name",
        value=st.session_state.team_name,
    )

    st.session_state.group_name = st.text_input(
        "Group",
        value=st.session_state.group_name,
    )

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


# ═══════════════════════════════════════════════════════
# PAGE: START
# ═══════════════════════════════════════════════════════
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

Every department decision changes your KPIs. The goal is not only to make profit, but also to keep customers satisfied, manage risk, improve sustainability and maintain a reliable supply chain.
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
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.title(f"Quarter {st.session_state.quarter} Overview")

    st.markdown(f"""
    <div class="event-banner">
        <div class="event-label">🔴 {st.session_state.event_label}</div>
        <div style="margin-top:4px;">{st.session_state.event}</div>
        <div style="margin-top:6px;"><strong>Decision context:</strong> {get_current_event_note()}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Global Efficiency Score", f"{st.session_state.score}/100", "Dynamic")

    with c2:
        st.metric("Net Profit", money(st.session_state.net_profit), "Affected by decisions")

    with c3:
        st.metric(
            "Inventory Value",
            money(st.session_state.inventory_value),
            "Holding cost impact",
            delta_color="inverse",
        )

    with c4:
        st.metric(
            "Sustainability Rating",
            sustainability_rating(st.session_state.sustainability_score),
            f"{st.session_state.sustainability_score}/100 ESG",
        )

    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric("Service Level", f"{st.session_state.service_level}%", "Delivery reliability")

    with k2:
        st.metric("Average Lead Time", f"{st.session_state.lead_time_days} days", "Lower is better")

    with k3:
        st.metric(
            "Supply Chain Risk",
            f"{st.session_state.risk_level}/100",
            risk_label(st.session_state.risk_level),
            delta_color="inverse",
        )

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="white-card"><div class="card-label">Inventory Levels</div>', unsafe_allow_html=True)

        raw_materials = min(100, max(0, int(st.session_state.inventory_value / 12000)))
        work_in_progress = min(100, max(0, int(st.session_state.service_level * 0.65)))
        finished_goods = min(100, max(0, int(100 - st.session_state.risk_level * 0.8)))
        safety_stock = min(100, max(0, int(st.session_state.inventory_value / 15000)))

        inventory = {
            "Raw materials": raw_materials,
            "Work in progress": work_in_progress,
            "Finished goods": finished_goods,
            "Safety stock": safety_stock,
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


# ═══════════════════════════════════════════════════════
# PAGE: DECISION LOG
# ═══════════════════════════════════════════════════════
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
</div>
""", unsafe_allow_html=True)

    done = st.session_state.completed_games
    departments = ["Purchasing", "Operations", "Sales", "Supply Chain"]

    cols = st.columns(4)

    for i, (col, department) in enumerate(zip(cols, departments)):
        status = "✅" if department in done else ("🔵" if i == len(done) else "⚪")
        col.markdown(f"{status} **{department}**")

    st.markdown("---")

    department_tab = st.selectbox(
        "Choose a department:",
        departments,
        label_visibility="collapsed",
    )

    # ── DEPARTMENT 1: PURCHASING ─────────────────────────────────────────────
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
                    impact = apply_kpi_change(
                        score=8,
                        profit=-60000,
                        service=5,
                        sustainability=2,
                        lead_time=-2,
                        risk=-8,
                    )
                elif choice == "Switch to the reliable European supplier":
                    impact = apply_kpi_change(
                        score=6,
                        profit=-90000,
                        service=7,
                        sustainability=4,
                        lead_time=-4,
                        risk=-9,
                    )
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
            ch = st.session_state.purchasing_chosen

            if ch == "Split purchasing between both suppliers":
                st.markdown("""
                <div class="result-correct">
                ✅ <strong>Balanced purchasing decision.</strong> Splitting the order reduces dependency on one supplier and improves resilience.
                <br><br>
                <strong>Management insight:</strong> Purchasing is not only about lowest price. Supplier reliability, risk exposure and lead time also influence total supply chain performance.
                </div>
                """, unsafe_allow_html=True)
            elif ch == "Switch to the reliable European supplier":
                st.markdown("""
                <div class="result-neutral">
                ℹ️ <strong>Reliable but more expensive.</strong> This decision protects service level and lead time, but reduces short-term profit.
                <br><br>
                <strong>Management insight:</strong> A higher purchase price can be acceptable when it prevents delays, stockouts and emergency costs.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-wrong">
                ⚠️ <strong>Cost-focused but risky.</strong> The low-cost supplier protects the purchase price, but increases disruption exposure.
                <br><br>
                <strong>Management insight:</strong> A cheap supplier can become expensive when delays and stockouts are included.
                </div>
                """, unsafe_allow_html=True)

    # ── DEPARTMENT 2: OPERATIONS ─────────────────────────────────────────────
    elif department_tab == "Operations":
        st.subheader("⚙️ Operations Department")
        st.markdown('<span class="badge-green">Capacity planning</span>', unsafe_allow_html=True)

        st.markdown("""
### Current situation
Operations is under pressure. Sales expects more orders next quarter, while current production capacity is almost fully used.

The operations manager warns that if production capacity is not adjusted, delivery times may increase. However, adding capacity also increases costs. The team must decide how operations should prepare for the next quarter.
        """)

        options = {
            "Keep current production capacity": "No extra cost, but a higher risk of late deliveries if demand increases.",
            "Use overtime for the next quarter": "Temporary capacity increase with higher labour costs.",
            "Invest in extra production capacity": "High short-term cost, but improves future capacity and delivery reliability.",
        }

        choice = st.radio(
            "Operations decision:",
            list(options.keys()),
            key="operations_decision_radio",
            disabled=st.session_state.operations_confirmed,
        )

        st.caption(options[choice])

        if st.button(
            "✅ Confirm operations decision",
            key="confirm_operations",
            disabled=st.session_state.operations_confirmed or st.session_state.game_paused,
        ):
            st.session_state.operations_confirmed = True
            st.session_state.operations_chosen = choice

            if "Operations" not in st.session_state.completed_games:
                if choice == "Use overtime for the next quarter":
                    impact = apply_kpi_change(
                        score=6,
                        profit=-70000,
                        service=6,
                        lead_time=-3,
                        risk=-4,
                    )
                elif choice == "Invest in extra production capacity":
                    impact = apply_kpi_change(
                        score=8,
                        profit=-180000,
                        service=8,
                        sustainability=1,
                        lead_time=-5,
                        risk=-6,
                    )
                else:
                    impact = apply_kpi_change(
                        score=-4,
                        profit=30000,
                        service=-7,
                        lead_time=4,
                        risk=6,
                    )

                record_decision("Operations", choice, "Capacity planning", impact)
                st.session_state.completed_games.append("Operations")

        if st.session_state.operations_confirmed:
            ch = st.session_state.operations_chosen

            if ch == "Use overtime for the next quarter":
                st.markdown("""
                <div class="result-correct">
                ✅ <strong>Flexible operations decision.</strong> Overtime gives extra capacity without a major long-term investment.
                <br><br>
                <strong>Management insight:</strong> Overtime is useful when demand pressure is temporary, but it should not become a permanent solution.
                </div>
                """, unsafe_allow_html=True)
            elif ch == "Invest in extra production capacity":
                st.markdown("""
                <div class="result-neutral">
                ℹ️ <strong>Strong long-term decision.</strong> Extra capacity improves service and lead time, but it is expensive in the short term.
                <br><br>
                <strong>Management insight:</strong> Capacity investments are valuable when demand growth is expected to continue.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-wrong">
                ⚠️ <strong>Low-cost but risky.</strong> Keeping capacity unchanged saves money now, but can hurt lead time and service level.
                <br><br>
                <strong>Management insight:</strong> Operations must balance cost efficiency with delivery reliability.
                </div>
                """, unsafe_allow_html=True)

    # ── DEPARTMENT 3: SALES ──────────────────────────────────────────────────
    elif department_tab == "Sales":
        st.subheader("📈 Sales Department")
        st.markdown('<span class="badge-blue">Customer demand</span>', unsafe_allow_html=True)

        demand_shock = st.session_state.active_event_code == "pandemic"

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
                    impact = apply_kpi_change(
                        score=7,
                        profit=90000,
                        revenue=160000,
                        service=3,
                        risk=-2,
                    )
                elif choice == "Accept all extra customer demand":
                    impact = apply_kpi_change(
                        score=-2,
                        profit=130000,
                        revenue=260000,
                        service=-7,
                        lead_time=4,
                        risk=7,
                    )
                else:
                    impact = apply_kpi_change(
                        score=-3,
                        profit=-60000,
                        revenue=-140000,
                        service=2,
                        risk=-3,
                    )

                record_decision("Sales", choice, "Customer demand", impact)
                st.session_state.completed_games.append("Sales")

        if st.session_state.sales_confirmed:
            ch = st.session_state.sales_chosen

            if ch == "Accept part of the extra demand":
                st.markdown("""
                <div class="result-correct">
                ✅ <strong>Balanced sales decision.</strong> The company grows revenue without putting too much pressure on operations.
                <br><br>
                <strong>Management insight:</strong> Sales promises should match what the supply chain can actually deliver.
                </div>
                """, unsafe_allow_html=True)
            elif ch == "Accept all extra customer demand":
                st.markdown("""
                <div class="result-wrong">
                ⚠️ <strong>Ambitious but risky.</strong> Revenue increases, but the company may struggle to deliver everything on time.
                <br><br>
                <strong>Management insight:</strong> Commercial growth can damage service level if operations and supply chain are not prepared.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-neutral">
                ℹ️ <strong>Safe but conservative.</strong> Rejecting demand protects operations, but limits growth and profit.
                <br><br>
                <strong>Management insight:</strong> Avoiding risk can be useful, but it can also mean missing strategic opportunities.
                </div>
                """, unsafe_allow_html=True)

    # ── DEPARTMENT 4: SUPPLY CHAIN ───────────────────────────────────────────
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
                    impact = apply_kpi_change(
                        score=8,
                        profit=-50000,
                        service=5,
                        sustainability=4,
                        lead_time=-2,
                        risk=-7,
                    )
                elif choice == "Use the fastest transport route":
                    impact = apply_kpi_change(
                        score=-1,
                        profit=-120000,
                        service=8,
                        sustainability=-8,
                        lead_time=-6,
                        risk=-3,
                    )
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
            ch = st.session_state.supply_chain_chosen

            if ch == "Use a balanced multimodal route":
                st.markdown("""
                <div class="result-correct">
                ✅ <strong>Resilient supply chain decision.</strong> A balanced multimodal route protects service level while keeping costs and emissions under control.
                <br><br>
                <strong>Management insight:</strong> Supply chain decisions are about total performance, not only transport price.
                </div>
                """, unsafe_allow_html=True)
            elif ch == "Use the fastest transport route":
                st.markdown("""
                <div class="result-neutral">
                ℹ️ <strong>Fast but costly.</strong> The fastest route improves delivery performance, but reduces profit and sustainability.
                <br><br>
                <strong>Management insight:</strong> Speed can be valuable, but it should be used where customer value justifies the extra cost.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-wrong">
                ⚠️ <strong>Cheap but exposed.</strong> The cheapest route saves money, but disruption risk can damage lead time and service level.
                <br><br>
                <strong>Management insight:</strong> The cheapest logistics option is not always the best option after delay risk is included.
                </div>
                """, unsafe_allow_html=True)

    # ── FINISH QUARTER BUTTON ────────────────────────────────────────────────
    st.markdown("---")

    completed = len(st.session_state.completed_games)

    if completed < 4:
        st.info(
            f"Complete all four departments before finishing the quarter. "
            f"Progress: {completed}/4 department decisions completed."
        )
    else:
        st.success("All four department decisions have been completed. You can now finish this quarter.")

        if st.button("➡️ Finish quarter and view summary", type="primary"):
            show_quarter_summary()


# ═══════════════════════════════════════════════════════
# HIDDEN PAGE: QUARTER SUMMARY
# ═══════════════════════════════════════════════════════
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
</div>
""", unsafe_allow_html=True)

    col_progress, col_status = st.columns([2, 1])

    with col_progress:
        st.markdown("### Department progress")
        st.progress(completed / 4)
        st.caption(f"{completed}/4 department decisions completed this quarter.")

    with col_status:
        if completed < 4:
            st.warning("Quarter not fully completed.")
        else:
            st.success("Quarter completed.")

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


# ═══════════════════════════════════════════════════════
# PAGE: FINANCIALS
# ═══════════════════════════════════════════════════════
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
        performance_rows.append({
            "Quarter": f"{current_q} current",
            "Revenue": st.session_state.revenue,
            "Net Profit": st.session_state.net_profit,
            "Efficiency Score": st.session_state.score,
            "Service Level": st.session_state.service_level,
            "ESG Score": st.session_state.sustainability_score,
            "Inventory Value": st.session_state.inventory_value,
            "Risk Level": st.session_state.risk_level,
            "Lead Time": st.session_state.lead_time_days,
        })

    formatted_rows = []
    for row in performance_rows:
        formatted_rows.append({
            "Quarter": row["Quarter"],
            "Revenue": money(row["Revenue"]),
            "Net Profit": money(row["Net Profit"]),
            "Efficiency Score": row["Efficiency Score"],
            "Service Level": f"{row['Service Level']}%",
            "ESG Score": row["ESG Score"],
            "Inventory Value": money(row["Inventory Value"]),
            "Risk Level": row["Risk Level"],
            "Lead Time": row["Lead Time"],
        })

    st.dataframe(pd.DataFrame(formatted_rows), use_container_width=True, hide_index=True)

    st.markdown("---")

    st.markdown("### KPI Charts")

    chart_df = pd.DataFrame(performance_rows)
    chart_df = chart_df.set_index("Quarter")

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


# ═══════════════════════════════════════════════════════
# PAGE: FINAL REPORT
# ═══════════════════════════════════════════════════════
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

    st.markdown("---")

    st.markdown("### Complete decision history")

    if st.session_state.decision_log:
        show_clean_decision_table(st.session_state.decision_log)
    else:
        st.info("No decisions have been logged yet.")


# ═══════════════════════════════════════════════════════
# PAGE: INSTRUCTOR
# ═══════════════════════════════════════════════════════
elif page == "👨‍🏫 Instructor view":
    st.title("Instructor — God Mode")
    st.markdown('<span class="badge-red">Instructor only</span>', unsafe_allow_html=True)

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
            {
                "Team": "Team Apex",
                "Score": 91,
                "Profit": "$1.82M",
                "ESG": "A",
                "Service": "94%",
            },
            {
                "Team": "NovaTrade",
                "Score": 88,
                "Profit": "$1.71M",
                "ESG": "B+",
                "Service": "91%",
            },
            {
                "Team": "LogiX Group",
                "Score": 83,
                "Profit": "$1.58M",
                "ESG": "B",
                "Service": "89%",
            },
            {
                "Team": f"⭐ {st.session_state.team_name}",
                "Score": st.session_state.score,
                "Profit": money(st.session_state.net_profit),
                "ESG": sustainability_rating(st.session_state.sustainability_score),
                "Service": f"{st.session_state.service_level}%",
            },
            {
                "Team": "FastLink",
                "Score": 69,
                "Profit": "$1.10M",
                "ESG": "C+",
                "Service": "78%",
            },
            {
                "Team": "ChainMasters",
                "Score": 61,
                "Profit": "−$220k",
                "ESG": "C",
                "Service": "67%",
            },
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
            ],
        }

        st.dataframe(pd.DataFrame(current_kpis), use_container_width=True, hide_index=True)
