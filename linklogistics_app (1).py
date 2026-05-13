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

    # Mini-game state
    "supp_chosen": None,
    "supp_confirmed": False,
    "forecast_value": 47000,
    "forecast_confirmed": False,
    "crisis_chosen": None,
    "crisis_confirmed": False,
    "route_chosen": None,
    "route_confirmed": False,

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
    """Resets all mini-game confirmations for a new quarter."""
    st.session_state.supp_chosen = None
    st.session_state.supp_confirmed = False
    st.session_state.forecast_value = 47000
    st.session_state.forecast_confirmed = False
    st.session_state.crisis_chosen = None
    st.session_state.crisis_confirmed = False
    st.session_state.route_chosen = None
    st.session_state.route_confirmed = False
    st.session_state.completed_games = []


def current_quarter_decisions():
    return [
        row for row in st.session_state.decision_log
        if row["Quarter"] == f"Q{st.session_state.quarter}"
    ]


def make_decision_table(rows):
    """Formats decision log for display."""
    formatted = []

    for row in rows:
        formatted.append(
            {
                "Quarter": row["Quarter"],
                "Area": row["Area"],
                "Choice": row["Choice"],
                "Concept": row["Concept"],
                "Score": row["Score Impact"],
                "Profit": money(row["Profit Impact"]),
                "Revenue": money(row["Revenue Impact"]),
                "Inventory": money(row["Inventory Impact"]),
                "Service": row["Service Impact"],
                "ESG": row["ESG Impact"],
                "Lead Time": row["Lead Time Impact"],
                "Risk": row["Risk Impact"],
            }
        )

    return formatted


def get_current_event_note():
    code = st.session_state.active_event_code

    if code == "rotterdam_strike":
        return "Sea freight through Rotterdam is disrupted. Rail and local suppliers become more attractive."
    elif code == "suez_blockage":
        return "Global sea freight is disrupted. Transport decisions should avoid sea routes."
    elif code == "tariff":
        return "Foreign sourcing is more expensive. Domestic or pre-buying strategies become more attractive."
    elif code == "taiwan_fire":
        return "Component availability is low. Inventory and supplier reliability are extra important."
    elif code == "currency_shock":
        return "Currency movement hurts margins. Cost control and pricing decisions matter more."
    elif code == "pandemic":
        return "Demand is unstable. Forecasting accuracy is more difficult."
    elif code == "labour_strike":
        return "Road logistics are delayed. Lead time and service level are under pressure."
    return "No special event active."


# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

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
section[data-testid="stSidebar"] .stRadio label { 
    color: rgba(232,230,224,0.7) !important; 
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
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚚 **Supply Chain Game HAN**")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "🏠 Start",
            "📊 Dashboard",
            "🎮 Mini-games",
            "📋 Quarter Summary",
            "💰 Financials",
            "🏁 Final Report",
            "👨‍🏫 Instructor view",
        ],
        label_visibility="collapsed",
    )

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
You are the supply chain management team of **{st.session_state.team_name}**.

Each quarter, your team makes decisions about:

- Supplier selection
- Demand forecasting
- Crisis response
- Logistics routes

Every decision changes your KPIs. The goal is not only to make profit, but also to keep customers satisfied, manage risk and improve sustainability.
        """)

        if st.button("▶️ Start game"):
            st.session_state.game_started = True
            st.success("Game started. Go to the Dashboard or Mini-games page.")

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
    st.caption(f"{completed}/4 mini-games completed this quarter.")


# ═══════════════════════════════════════════════════════
# PAGE: MINI-GAMES
# ═══════════════════════════════════════════════════════
elif page == "🎮 Mini-games":
    st.title("Learning Activities")
    st.caption(f"Complete all four challenges this quarter · Q{st.session_state.quarter}")

    if st.session_state.game_paused:
        st.warning("The instructor has paused the game. You can view the page, but decisions cannot be submitted.")

    st.markdown(f"""
<div class="event-banner">
    <div class="event-label">🔴 Current event</div>
    <div style="margin-top:4px;">{st.session_state.event}</div>
    <div style="margin-top:6px;"><strong>Meaning:</strong> {get_current_event_note()}</div>
</div>
""", unsafe_allow_html=True)

    done = st.session_state.completed_games
    cols = st.columns(4)
    games = ["Supplier selection", "Demand forecast", "Crisis response", "Logistics route"]

    for i, (col, g) in enumerate(zip(cols, games)):
        status = "✅" if g in done else ("🔵" if i == len(done) else "⚪")
        col.markdown(f"{status} **{g}**")

    st.markdown("---")

    game_tab = st.selectbox(
        "Choose a challenge:",
        games,
        label_visibility="collapsed",
    )

    # ── GAME 1: SUPPLIER SELECTION ─────────────────────────────────────────────
    if game_tab == "Supplier selection":
        st.subheader("🏭 Supplier Selection Challenge")
        st.markdown("> Choose the best supplier considering cost, lead time, reliability, risk and sustainability.")
        st.markdown('<span class="badge-orange">Supplier resilience</span>', unsafe_allow_html=True)

        tariff_active = st.session_state.active_event_code == "tariff"
        port_disruption = st.session_state.active_event_code in ["rotterdam_strike", "suez_blockage"]

        if tariff_active:
            st.warning("Tariff event active: foreign suppliers are more expensive this quarter.")
        if port_disruption:
            st.warning("Sea freight disruption active: suppliers that rely on sea freight have higher lead time risk.")

        suppliers = {
            "Shenzhen FastMfg": {
                "Cost": "$15/unit" if tariff_active else "$12/unit",
                "Lead time": "42 days sea" if port_disruption else "28 days sea",
                "ESG": "★★☆☆☆",
                "Reliability": "91%",
                "desc": "Cheapest base option, but exposed to foreign sourcing and sea freight risk.",
            },
            "EuroManuf GmbH": {
                "Cost": "$19/unit",
                "Lead time": "6 days rail",
                "ESG": "★★★★☆",
                "Reliability": "97%",
                "desc": "More expensive, but reliable and less exposed to global shipping disruption.",
            },
            "SwiftAir Logistics": {
                "Cost": "$31/unit",
                "Lead time": "2 days air",
                "ESG": "★★☆☆☆",
                "Reliability": "99%",
                "desc": "Fastest option, but very costly and high emissions.",
            },
        }

        cols = st.columns(3)
        for col, (name, info) in zip(cols, suppliers.items()):
            with col:
                st.markdown(f"**{name}**")
                st.markdown(f"💰 Cost: `{info['Cost']}`")
                st.markdown(f"⏱ Lead time: `{info['Lead time']}`")
                st.markdown(f"🌿 ESG: {info['ESG']}")
                st.markdown(f"✅ Reliability: `{info['Reliability']}`")
                st.caption(info["desc"])

        chosen = st.radio(
            "Select your supplier:",
            list(suppliers.keys()),
            key="supp_radio",
            horizontal=True,
            disabled=st.session_state.supp_confirmed,
        )

        col_btn1, col_btn2, _ = st.columns([1, 1, 4])
        confirm = col_btn1.button(
            "✅ Confirm selection",
            key="supp_confirm_btn",
            disabled=st.session_state.supp_confirmed or st.session_state.game_paused,
        )
        hint = col_btn2.button("💡 Show hint", key="supp_hint_btn")

        if hint:
            if st.session_state.difficulty == "Hard":
                st.info("Hints are limited in Hard mode. Think about total risk, not only unit cost.")
            else:
                st.info("Hint: the cheapest supplier is not always the best supplier. Consider disruption exposure, lead time and ESG.")

        if confirm:
            st.session_state.supp_confirmed = True
            st.session_state.supp_chosen = chosen

            if "Supplier selection" not in done:
                if chosen == "EuroManuf GmbH":
                    impact = apply_kpi_change(
                        score=8,
                        profit=-40000,
                        inventory=0,
                        service=6,
                        sustainability=5,
                        lead_time=-4,
                        risk=-8,
                    )
                elif chosen == "Shenzhen FastMfg":
                    impact = apply_kpi_change(
                        score=-6 if port_disruption else -3,
                        profit=-140000 if tariff_active else -120000,
                        inventory=-90000,
                        service=-12 if port_disruption else -8,
                        sustainability=-3,
                        lead_time=14 if port_disruption else 6,
                        risk=14 if port_disruption else 8,
                    )
                else:
                    impact = apply_kpi_change(
                        score=-3,
                        profit=-190000,
                        inventory=0,
                        service=4,
                        sustainability=-8,
                        lead_time=-8,
                        risk=-3,
                    )

                record_decision("Supplier selection", chosen, "Supplier resilience", impact)
                st.session_state.completed_games.append("Supplier selection")

        if st.session_state.supp_confirmed:
            ch = st.session_state.supp_chosen

            if ch == "EuroManuf GmbH":
                st.markdown("""
                <div class="result-correct">
                ✅ <strong>Strong choice.</strong> EuroManuf GmbH is not the cheapest, but it protects reliability and avoids major disruption exposure.
                <br><br>
                <strong>Concept:</strong> Supplier resilience. A resilient supplier can be worth more than a cheap supplier during disruption.
                </div>
                """, unsafe_allow_html=True)
            elif ch == "Shenzhen FastMfg":
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Risky choice.</strong> Shenzhen FastMfg has low unit cost, but the current event creates high disruption exposure.
                <br><br>
                <strong>Concept:</strong> Total cost of ownership. A low purchase price can still lead to high hidden costs through delay, stockouts and risk.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Too costly.</strong> SwiftAir is very reliable and fast, but it damages profit and sustainability.
                <br><br>
                <strong>Concept:</strong> Trade-off management. Speed improves service level, but can reduce margin and ESG performance.
                </div>
                """, unsafe_allow_html=True)

    # ── GAME 2: DEMAND FORECASTING ─────────────────────────────────────────────
    elif game_tab == "Demand forecast":
        st.subheader("📈 Demand Forecasting Quiz")
        tolerance = get_forecast_tolerance()
        st.markdown(f"> Read the market report below, then set your Q4 demand forecast. Accuracy within **{tolerance}%** earns full points.")
        st.markdown('<span class="badge-blue">Bullwhip effect</span>', unsafe_allow_html=True)

        demand_shock = st.session_state.active_event_code == "pandemic"

        col_report, col_slider = st.columns([1, 1])

        with col_report:
            st.markdown("**📋 Market Intelligence — Q4 Outlook**")

            if demand_shock:
                st.markdown("""
| Signal | Detail |
|--------|--------|
| ↑ Medical demand | +200% in healthcare-related products |
| ↓ Consumer goods | −30% demand pressure |
| ↑ Market uncertainty | Forecast error risk is high |
| → Q3 actual demand | **42,000 units** |
| → Expected stable demand | **44,000–50,000 units** |
                """)
            else:
                st.markdown("""
| Signal | Detail |
|--------|--------|
| ↑ Consumer confidence | Index up 8 points vs Q3 |
| ↑ Competitor stockout | Demand may shift to us |
| → Seasonal trend | Q4 historically +12% over Q3 |
| ↓ New tariff | 5% import tariff may soften demand |
| → Q3 actual demand | **42,000 units** |
                """)

        with col_slider:
            st.markdown("**Your Q4 Forecast**")
            forecast = st.slider(
                "Drag to set your forecast, in units",
                min_value=30000,
                max_value=70000,
                value=st.session_state.forecast_value,
                step=500,
                key="forecast_slider",
                disabled=st.session_state.forecast_confirmed,
            )

            st.session_state.forecast_value = forecast
            st.markdown(f"### `{forecast:,} units`")
            st.caption("The Bullwhip Effect means small demand changes can become amplified upstream.")

        col_b1, col_b2, _ = st.columns([1, 1, 4])
        confirm_fc = col_b1.button(
            "✅ Submit forecast",
            key="fc_confirm",
            disabled=st.session_state.forecast_confirmed or st.session_state.game_paused,
        )
        hint_fc = col_b2.button("💡 Bullwhip effect?", key="fc_hint")

        if hint_fc:
            if st.session_state.difficulty == "Hard":
                st.info("Hints are limited in Hard mode. Avoid panic-ordering.")
            else:
                st.info("Bullwhip Effect: small changes in customer demand can create larger order changes upstream. Anchor forecasts to real demand.")

        if confirm_fc:
            st.session_state.forecast_confirmed = True
            correct = 46000 if demand_shock else 48000
            pct_off = abs(forecast - correct) / correct * 100

            if "Demand forecast" not in done:
                if pct_off <= tolerance:
                    impact = apply_kpi_change(
                        score=6,
                        profit=90000,
                        revenue=60000,
                        inventory=-20000,
                        service=5,
                        sustainability=2,
                        risk=-4,
                    )
                elif forecast > correct:
                    impact = apply_kpi_change(
                        score=-4,
                        profit=-85000,
                        inventory=120000,
                        service=-2,
                        sustainability=-5,
                        risk=6,
                    )
                else:
                    impact = apply_kpi_change(
                        score=-5,
                        profit=-110000,
                        revenue=-70000,
                        inventory=-100000,
                        service=-8,
                        sustainability=0,
                        risk=8,
                    )

                record_decision("Demand forecast", f"{forecast:,} units", "Bullwhip effect", impact)
                st.session_state.completed_games.append("Demand forecast")

        if st.session_state.forecast_confirmed:
            correct = 46000 if demand_shock else 48000
            forecast = st.session_state.forecast_value
            pct_off = abs(forecast - correct) / correct * 100

            if pct_off <= tolerance:
                st.markdown(f"""
                <div class="result-correct">
                ✅ <strong>Good forecast!</strong> The expected demand was approximately {correct:,} units. Your estimate was {pct_off:.1f}% off.
                <br><br>
                <strong>Concept:</strong> Forecast accuracy. A realistic forecast improves service level and prevents unnecessary inventory costs.
                </div>
                """, unsafe_allow_html=True)
            elif forecast > correct:
                st.markdown(f"""
                <div class="result-wrong">
                ❌ <strong>Overforecast.</strong> You predicted {forecast:,} units versus expected demand of approximately {correct:,}.
                <br><br>
                <strong>Concept:</strong> Bullwhip effect. Overreacting to demand signals creates excess inventory and holding costs.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-wrong">
                ❌ <strong>Underforecast.</strong> You predicted {forecast:,} units versus expected demand of approximately {correct:,}.
                <br><br>
                <strong>Concept:</strong> Service level. Too little stock creates stockouts, lost sales and lower delivery reliability.
                </div>
                """, unsafe_allow_html=True)

    # ── GAME 3: CRISIS RESPONSE ───────────────────────────────────────────────
    elif game_tab == "Crisis response":
        st.subheader("🚨 Crisis Response")
        st.markdown('<span class="badge-red">Risk mitigation</span>', unsafe_allow_html=True)

        if st.session_state.active_event_code == "tariff":
            crisis_title = "20% Tariff Hike"
            crisis_text = """
The government announced a **20% import tariff** on electronics components, effective next quarter.

Your primary supplier is abroad. Estimated profit impact: **−$380,000** unless you act now.
            """
        elif st.session_state.active_event_code == "taiwan_fire":
            crisis_title = "Factory Fire in Taiwan"
            crisis_text = """
A key component factory in Taiwan has been hit by a fire.

Component availability is expected to fall by **40%** next quarter. Service level and inventory are at risk.
            """
        else:
            crisis_title = "Unexpected Supply Chain Shock"
            crisis_text = """
A major disruption is expected next quarter.

Your team must choose a mitigation strategy to protect service level, profit and risk exposure.
            """

        st.error(f"**🚨 Breaking — {crisis_title}**\n\n{crisis_text}")

        options = {
            "A — Absorb the impact": "Keep the current plan. Low effort, but high financial and operational risk.",
            "B — Emergency domestic switch": "Urgently onboard a local supplier. Less disruption exposure, but quality and onboarding risks.",
            "C — Pass cost to customer": "Raise prices to protect margin. May reduce demand and customer satisfaction.",
            "D — Pre-buy safety stock now": "Buy extra stock before the disruption fully hits. Higher inventory cost, but lower risk.",
        }

        crisis_choice = st.radio(
            "Choose your response strategy:",
            list(options.keys()),
            key="crisis_radio",
            disabled=st.session_state.crisis_confirmed,
        )

        for opt, desc in options.items():
            if opt == crisis_choice:
                st.caption(f"→ {desc}")

        col_c1, col_c2, _ = st.columns([1, 1, 4])
        confirm_cr = col_c1.button(
            "✅ Confirm response",
            key="crisis_confirm",
            disabled=st.session_state.crisis_confirmed or st.session_state.game_paused,
        )
        hint_cr = col_c2.button("💡 Show hint", key="crisis_hint")

        if hint_cr:
            if st.session_state.difficulty == "Hard":
                st.info("Hints are limited in Hard mode. Think about risk versus cost.")
            else:
                st.info("Hint: A good crisis response reduces risk before the disruption fully damages the supply chain.")

        if confirm_cr:
            st.session_state.crisis_confirmed = True
            st.session_state.crisis_chosen = crisis_choice

            if "Crisis response" not in done:
                if crisis_choice.startswith("D"):
                    impact = apply_kpi_change(
                        score=10,
                        profit=-90000,
                        inventory=180000,
                        service=7,
                        sustainability=-2,
                        risk=-10,
                    )
                elif crisis_choice.startswith("A"):
                    impact = apply_kpi_change(
                        score=-6,
                        profit=-380000,
                        service=-3,
                        risk=12,
                    )
                elif crisis_choice.startswith("B"):
                    impact = apply_kpi_change(
                        score=-3,
                        profit=-160000,
                        inventory=-40000,
                        service=-6,
                        sustainability=4,
                        lead_time=-3,
                        risk=8,
                    )
                else:
                    impact = apply_kpi_change(
                        score=-4,
                        profit=-130000,
                        revenue=-150000,
                        inventory=30000,
                        service=-5,
                        risk=5,
                    )

                record_decision("Crisis response", crisis_choice, "Risk mitigation", impact)
                st.session_state.completed_games.append("Crisis response")

        if st.session_state.crisis_confirmed:
            ch = st.session_state.crisis_chosen

            if ch.startswith("D"):
                st.markdown("""
                <div class="result-correct">
                ✅ <strong>Strong mitigation.</strong> Pre-buying safety stock increases inventory costs, but it protects service level and reduces risk.
                <br><br>
                <strong>Concept:</strong> Buying forward. Companies sometimes buy earlier to avoid future disruption or price increases.
                </div>
                """, unsafe_allow_html=True)
            elif ch.startswith("A"):
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Too passive.</strong> Absorbing the impact keeps the plan simple, but profit and risk performance suffer.
                <br><br>
                <strong>Concept:</strong> Supply chain resilience requires preparation, not only reaction.
                </div>
                """, unsafe_allow_html=True)
            elif ch.startswith("B"):
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Risky pivot.</strong> Domestic switching can help, but emergency onboarding often causes quality and delivery issues.
                <br><br>
                <strong>Concept:</strong> Supplier onboarding risk. New suppliers need validation before they can be fully trusted.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Demand risk.</strong> Passing costs to customers may protect margins, but it can reduce demand and customer satisfaction.
                <br><br>
                <strong>Concept:</strong> Price elasticity. Customers may buy less when prices increase.
                </div>
                """, unsafe_allow_html=True)

    # ── GAME 4: LOGISTICS ROUTE ───────────────────────────────────────────────
    elif game_tab == "Logistics route":
        st.subheader("🗺️ Logistics Route Picker")
        st.markdown("> Ship **10,000 units** from **Shanghai → Amsterdam**. Balance speed, cost and carbon emissions.")
        st.markdown('<span class="badge-green">Total landed cost</span>', unsafe_allow_html=True)

        sea_disrupted = st.session_state.active_event_code in ["rotterdam_strike", "suez_blockage"]

        if sea_disrupted:
            st.warning("Sea freight disruption active: sea route has a major delay risk.")

        routes = {
            "🚢 Sea freight": {
                "cost": "$2.10/unit",
                "total": "$21,000",
                "transit": "42 days" if sea_disrupted else "28 days",
                "co2": "0.01 kg/unit",
                "note": "⚠️ Disruption delay active." if sea_disrupted else "Cheap and low emissions.",
                "note_color": "red" if sea_disrupted else "green",
            },
            "✈️ Air freight": {
                "cost": "$8.40/unit",
                "total": "$84,000",
                "transit": "3 days",
                "co2": "0.89 kg/unit",
                "note": "Fast but expensive and high emissions.",
                "note_color": "orange",
            },
            "🚂 Rail freight": {
                "cost": "$3.80/unit",
                "total": "$38,000",
                "transit": "14 days",
                "co2": "0.04 kg/unit",
                "note": "Good balance of cost, speed and ESG.",
                "note_color": "green",
            },
        }

        cols = st.columns(3)
        for col, (name, info) in zip(cols, routes.items()):
            with col:
                st.markdown(f"**{name}**")
                st.markdown(f"💰 `{info['cost']}` per unit")
                st.markdown(f"📦 Total: `{info['total']}`")
                st.markdown(f"⏱ Transit: `{info['transit']}`")
                st.markdown(f"🌿 CO₂: `{info['co2']}`")
                color_map = {"red": "🔴", "orange": "🟡", "green": "🟢"}
                st.caption(f"{color_map[info['note_color']]} {info['note']}")

        route_choice = st.radio(
            "Choose your transport mode:",
            list(routes.keys()),
            key="route_radio",
            horizontal=True,
            disabled=st.session_state.route_confirmed,
        )

        col_r1, col_r2, _ = st.columns([1, 1, 4])
        confirm_rt = col_r1.button(
            "✅ Confirm route",
            key="route_confirm",
            disabled=st.session_state.route_confirmed or st.session_state.game_paused,
        )
        hint_rt = col_r2.button("💡 Show hint", key="route_hint")

        if hint_rt:
            if st.session_state.difficulty == "Hard":
                st.info("Hints are limited in Hard mode. Look beyond transport cost.")
            else:
                st.info("Hint: Total landed cost includes transport cost, delay risk, lost sales and emissions.")

        if confirm_rt:
            st.session_state.route_confirmed = True
            st.session_state.route_chosen = route_choice

            if "Logistics route" not in done:
                if "Rail" in route_choice:
                    impact = apply_kpi_change(
                        score=7,
                        profit=-38000,
                        service=5,
                        sustainability=4,
                        lead_time=0,
                        risk=-6,
                    )
                elif "Sea" in route_choice:
                    impact = apply_kpi_change(
                        score=-6 if sea_disrupted else 4,
                        profit=-90000 if sea_disrupted else -21000,
                        inventory=-80000 if sea_disrupted else 0,
                        service=-10 if sea_disrupted else 1,
                        sustainability=3,
                        lead_time=14 if sea_disrupted else 4,
                        risk=10 if sea_disrupted else 1,
                    )
                else:
                    impact = apply_kpi_change(
                        score=-3,
                        profit=-84000,
                        service=7,
                        sustainability=-8,
                        lead_time=-8,
                        risk=-2,
                    )

                record_decision("Logistics route", route_choice, "Total landed cost", impact)
                st.session_state.completed_games.append("Logistics route")

        if st.session_state.route_confirmed:
            ch = st.session_state.route_chosen

            if "Rail" in ch:
                st.markdown("""
                <div class="result-correct">
                ✅ <strong>Strong choice.</strong> Rail gives the best balance between cost, speed, risk and ESG in this scenario.
                <br><br>
                <strong>Concept:</strong> Total landed cost. The cheapest route is not always cheapest after delay risk and lost sales are included.
                </div>
                """, unsafe_allow_html=True)
            elif "Sea" in ch and sea_disrupted:
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Disrupted route.</strong> Sea freight is normally attractive, but the active event creates too much delay risk.
                <br><br>
                <strong>Concept:</strong> Bottleneck risk. A disruption at one node can damage the entire supply chain.
                </div>
                """, unsafe_allow_html=True)
            elif "Sea" in ch:
                st.markdown("""
                <div class="result-correct">
                ✅ <strong>Acceptable choice.</strong> Sea freight is slow, but cost-efficient and sustainable when no disruption is active.
                <br><br>
                <strong>Concept:</strong> Mode selection. The best transport mode depends on urgency, cost and disruption risk.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Too expensive.</strong> Air freight is fast, but the shipment is too large for this to be cost-efficient.
                <br><br>
                <strong>Concept:</strong> Transport trade-off. Speed improves service level, but can damage margin and ESG.
                </div>
                """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# PAGE: QUARTER SUMMARY
# ═══════════════════════════════════════════════════════
elif page == "📋 Quarter Summary":
    st.title(f"Quarter {st.session_state.quarter} Summary")

    decisions = current_quarter_decisions()
    completed = len(st.session_state.completed_games)

    st.markdown(f"""
<div class="event-banner">
    <div class="event-label">Quarter context</div>
    <div style="margin-top:4px;">{st.session_state.event}</div>
</div>
""", unsafe_allow_html=True)

    if completed < 4:
        st.warning(f"You have completed {completed}/4 mini-games this quarter. Complete all challenges for a full summary.")
    else:
        st.success("All four mini-games have been completed this quarter.")

    st.markdown("### Current KPI result")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", f"{st.session_state.score}/100")
    c2.metric("Profit", money(st.session_state.net_profit))
    c3.metric("Service Level", f"{st.session_state.service_level}%")
    c4.metric("ESG Rating", sustainability_rating(st.session_state.sustainability_score))

    c5, c6, c7 = st.columns(3)
    c5.metric("Inventory", money(st.session_state.inventory_value))
    c6.metric("Lead Time", f"{st.session_state.lead_time_days} days")
    c7.metric("Risk", f"{st.session_state.risk_level}/100", risk_label(st.session_state.risk_level))

    st.markdown("---")

    st.markdown("### Decisions made this quarter")

    if decisions:
        st.table(make_decision_table(decisions))
    else:
        st.info("No decisions have been made in this quarter yet.")

    st.markdown("---")

    st.markdown("### Strategy type")
    title, explanation = strategy_type()
    st.markdown(f"""
<div class="white-card">
<div class="card-label">Your current strategic profile</div>
<h3>{title}</h3>
<p class="kpi-note">{explanation}</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("### Reflection")
    st.markdown("""
Use this page to discuss your decisions with your group. A good supply chain strategy is not about choosing the cheapest option every time.
It is about balancing profit, service level, sustainability, lead time, inventory and risk.
    """)


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

    st.table(formatted_rows)

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
        st.table(make_decision_table(st.session_state.decision_log))
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
        st.table(make_decision_table(st.session_state.decision_log))
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
            if st.session_state.quarter < 8:
                add_current_quarter_to_history()
                st.session_state.quarter += 1

                # Small automatic market change for the new quarter
                st.session_state.revenue = int(st.session_state.revenue * 1.04)
                st.session_state.net_profit = int(st.session_state.net_profit * 1.02)

                # Slightly normalize some KPIs
                st.session_state.lead_time_days = max(8, int(st.session_state.lead_time_days * 0.95))
                st.session_state.risk_level = max(20, int(st.session_state.risk_level * 0.95))

                reset_quarter_games()

                st.success(f"Advanced to Q{st.session_state.quarter}. Mini-games have been reset.")
            else:
                add_current_quarter_to_history()
                st.warning("Already at final quarter, Q8. Go to the Final Report page.")

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

        st.table(teams)

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

        st.table(current_kpis)
