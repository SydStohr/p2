pip install streamlit
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LinkLogistics",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ───────────────────────────────────────────────────
defaults = {
    "score": 74,
    "quarter": 3,

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
    "game_paused": False,
    "completed_games": [],

    # History for financial page
    "history": [
        {
            "Quarter": "Q1",
            "Revenue": 3200000,
            "Net Profit": 900000,
            "Efficiency Score": 62,
            "Service Level": 78,
            "ESG Score": 68,
            "Inventory Value": 720000,
        },
        {
            "Quarter": "Q2",
            "Revenue": 3550000,
            "Net Profit": 1030000,
            "Efficiency Score": 68,
            "Service Level": 82,
            "ESG Score": 72,
            "Inventory Value": 790000,
        },
    ],
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helper functions ─────────────────────────────────────────────────────────
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


def money(value):
    """Formats money values neatly."""
    sign = "−" if value < 0 else ""
    value = abs(value)

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


def add_current_quarter_to_history():
    """Saves the current quarter results to history before advancing."""
    current_q = f"Q{st.session_state.quarter}"

    existing_quarters = [row["Quarter"] for row in st.session_state.history]

    current_data = {
        "Quarter": current_q,
        "Revenue": st.session_state.revenue,
        "Net Profit": st.session_state.net_profit,
        "Efficiency Score": st.session_state.score,
        "Service Level": st.session_state.service_level,
        "ESG Score": st.session_state.sustainability_score,
        "Inventory Value": st.session_state.inventory_value,
    }

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


# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { 
    font-family: 'DM Sans', sans-serif; 
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid rgba(28,27,25,0.12);
    border-radius: 12px;
    padding: 16px 18px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1C1B19 !important;
}
section[data-testid="stSidebar"] * { 
    color: #E8E6E0 !important; 
}
section[data-testid="stSidebar"] .stRadio label { 
    color: rgba(232,230,224,0.7) !important; 
}

/* Buttons */
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

/* Progress bar */
.stProgress > div > div { 
    background-color: #185FA5 !important; 
}

/* Event banner */
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

/* Result boxes */
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
.result-hint {
    background: #EDECE8; 
    border: 1px solid rgba(28,27,25,0.15); 
    border-radius: 10px;
    padding: 14px 16px; 
    font-size: 13px; 
    color: #5F5E5A; 
    margin-top: 12px; 
    line-height: 1.6;
}

/* Cards */
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

/* Small KPI explanation */
.kpi-note {
    color: #5F5E5A;
    font-size: 13px;
    line-height: 1.5;
}

/* Status badges */
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
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔗 **Link**Logistics")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "🎮 Mini-games", "💰 Financials", "👨‍🏫 Instructor view"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**GreenRoute Co.** · Group 4")
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
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title(f"Quarter {st.session_state.quarter} Overview")

    st.markdown(f"""
    <div class="event-banner">
        <div class="event-label">🔴 {st.session_state.event_label}</div>
        <div style="margin-top:4px;">{st.session_state.event}</div>
    </div>
    """, unsafe_allow_html=True)

    # Main KPI row
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Global Efficiency Score",
            f"{st.session_state.score}/100",
            "Dynamic"
        )

    with c2:
        st.metric(
            "Net Profit",
            money(st.session_state.net_profit),
            "Affected by decisions"
        )

    with c3:
        st.metric(
            "Inventory Value",
            money(st.session_state.inventory_value),
            "Holding cost impact",
            delta_color="inverse"
        )

    with c4:
        st.metric(
            "Sustainability Rating",
            sustainability_rating(st.session_state.sustainability_score),
            f"{st.session_state.sustainability_score}/100 ESG"
        )

    # Extra KPI row
    k1, k2, k3 = st.columns(3)

    with k1:
        st.metric(
            "Service Level",
            f"{st.session_state.service_level}%",
            "Delivery reliability"
        )

    with k2:
        st.metric(
            "Average Lead Time",
            f"{st.session_state.lead_time_days} days",
            "Lower is better"
        )

    with k3:
        st.metric(
            "Supply Chain Risk",
            f"{st.session_state.risk_level}/100",
            risk_label(st.session_state.risk_level),
            delta_color="inverse"
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
            (1, "Team Apex", 91, False),
            (2, "NovaTrade", 88, False),
            (3, "LogiX Group", 83, False),
            (4, "GreenRoute Co.", st.session_state.score, True),
            (5, "FastLink", 69, False),
            (6, "ChainMasters", 61, False),
        ]

        leaderboard = sorted(leaderboard, key=lambda x: x[2], reverse=True)

        for i, (_, name, score, is_you) in enumerate(leaderboard, start=1):
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
                unsafe_allow_html=True
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
        st.warning("The instructor has paused the game. You can view the page, but decisions should not be submitted.")

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
        st.markdown("> The Rotterdam port strike adds **+14 days** to sea freight this quarter. Choose the best supplier considering cost, lead time, and sustainability.")
        st.markdown('<span class="badge-orange">Medium difficulty</span>', unsafe_allow_html=True)
        st.markdown("")

        suppliers = {
            "Shenzhen FastMfg": {
                "Cost": "$12/unit",
                "Lead time": "28 days sea",
                "ESG": "★★☆☆☆",
                "Reliability": "91%",
                "desc": "Cheapest option, but routes through Rotterdam.",
            },
            "EuroManuf GmbH": {
                "Cost": "$19/unit",
                "Lead time": "6 days rail",
                "ESG": "★★★★☆",
                "Reliability": "97%",
                "desc": "More expensive, but uses rail and bypasses the port strike.",
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

        st.markdown("")
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
            st.info("Hint: Rotterdam is the affected port. Which supplier uses a transport mode that completely bypasses sea freight? Also consider sustainability.")

        if confirm:
            st.session_state.supp_confirmed = True
            st.session_state.supp_chosen = chosen

            if "Supplier selection" not in done:
                if chosen == "EuroManuf GmbH":
                    apply_kpi_change(
                        score=8,
                        profit=-40000,
                        inventory=0,
                        service=6,
                        sustainability=5,
                        lead_time=-4,
                        risk=-8,
                    )
                elif chosen == "Shenzhen FastMfg":
                    apply_kpi_change(
                        score=-5,
                        profit=-120000,
                        inventory=-90000,
                        service=-10,
                        sustainability=-3,
                        lead_time=14,
                        risk=12,
                    )
                else:
                    apply_kpi_change(
                        score=-3,
                        profit=-190000,
                        inventory=0,
                        service=4,
                        sustainability=-8,
                        lead_time=-8,
                        risk=-3,
                    )

                st.session_state.completed_games.append("Supplier selection")

        if st.session_state.supp_confirmed:
            ch = st.session_state.supp_chosen

            if ch == "EuroManuf GmbH":
                st.markdown("""
                <div class="result-correct">
                ✅ <strong>Correct!</strong> EuroManuf GmbH avoids Rotterdam via rail. The higher unit cost is balanced by better reliability, shorter lead time and stronger ESG performance.
                <br><br>
                <strong>KPI impact:</strong> +8 score, +6 service level, +5 ESG, −8 risk.
                </div>
                """, unsafe_allow_html=True)
            elif ch == "Shenzhen FastMfg":
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Not optimal.</strong> Shenzhen FastMfg is cheap, but sea freight through Rotterdam is disrupted. This increases lead time and stockout risk.
                <br><br>
                <strong>KPI impact:</strong> −5 score, −$120k profit, −10 service level, +14 lead time days.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Too costly.</strong> SwiftAir is fast, but air freight damages profit and sustainability. It is useful for emergencies, not for regular bulk supply.
                <br><br>
                <strong>KPI impact:</strong> −3 score, −$190k profit, −8 ESG.
                </div>
                """, unsafe_allow_html=True)

    # ── GAME 2: DEMAND FORECASTING ─────────────────────────────────────────────
    elif game_tab == "Demand forecast":
        st.subheader("📈 Demand Forecasting Quiz")
        st.markdown("> Read the market report below, then set your Q4 demand forecast. Accuracy within **15%** earns full points.")
        st.markdown('<span class="badge-blue">Hard difficulty</span>', unsafe_allow_html=True)
        st.markdown("")

        col_report, col_slider = st.columns([1, 1])

        with col_report:
            st.markdown("**📋 Market Intelligence — Q4 Outlook**")
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
            st.caption("The Bullwhip Effect means small demand changes can become amplified upstream. Be careful not to over-order.")

        col_b1, col_b2, _ = st.columns([1, 1, 4])
        confirm_fc = col_b1.button(
            "✅ Submit forecast",
            key="fc_confirm",
            disabled=st.session_state.forecast_confirmed or st.session_state.game_paused,
        )
        hint_fc = col_b2.button("💡 Bullwhip effect?", key="fc_hint")

        if hint_fc:
            st.info("Bullwhip Effect: small changes in customer demand can create larger order changes upstream. Anchor forecasts to real demand instead of panic-ordering.")

        if confirm_fc:
            st.session_state.forecast_confirmed = True
            correct = 48000
            pct_off = abs(forecast - correct) / correct * 100

            if "Demand forecast" not in done:
                if pct_off <= 15:
                    apply_kpi_change(
                        score=6,
                        profit=90000,
                        revenue=60000,
                        inventory=-20000,
                        service=5,
                        sustainability=2,
                        risk=-4,
                    )
                elif forecast > correct:
                    apply_kpi_change(
                        score=-4,
                        profit=-85000,
                        inventory=120000,
                        service=-2,
                        sustainability=-5,
                        risk=6,
                    )
                else:
                    apply_kpi_change(
                        score=-5,
                        profit=-110000,
                        revenue=-70000,
                        inventory=-100000,
                        service=-8,
                        sustainability=0,
                        risk=8,
                    )

                st.session_state.completed_games.append("Demand forecast")

        if st.session_state.forecast_confirmed:
            correct = 48000
            forecast = st.session_state.forecast_value
            pct_off = abs(forecast - correct) / correct * 100

            if pct_off <= 15:
                st.markdown(f"""
                <div class="result-correct">
                ✅ <strong>Good forecast!</strong> The correct answer was approximately 48,000 units. Your estimate was {pct_off:.1f}% off, which is within the 15% threshold.
                <br><br>
                <strong>KPI impact:</strong> +6 score, +$90k profit, +5 service level, −4 risk.
                </div>
                """, unsafe_allow_html=True)
            elif forecast > correct:
                st.markdown(f"""
                <div class="result-wrong">
                ❌ <strong>Overforecast.</strong> You predicted {forecast:,} units versus expected demand of approximately 48,000. This creates excess inventory and higher holding costs.
                <br><br>
                <strong>KPI impact:</strong> −4 score, −$85k profit, +$120k inventory, −5 ESG.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-wrong">
                ❌ <strong>Underforecast.</strong> You predicted {forecast:,} units versus expected demand of approximately 48,000. This creates stockouts and lost sales.
                <br><br>
                <strong>KPI impact:</strong> −5 score, −$110k profit, −8 service level, +8 risk.
                </div>
                """, unsafe_allow_html=True)

    # ── GAME 3: CRISIS RESPONSE ───────────────────────────────────────────────
    elif game_tab == "Crisis response":
        st.subheader("🚨 Crisis Response — 20% Tariff Hike")
        st.markdown('<span class="badge-red">Urgent</span>', unsafe_allow_html=True)
        st.markdown("")

        st.error("""
**🚨 Breaking — Trade Policy Alert**

The government just announced a **20% import tariff** on all electronics components, effective next quarter.

Your primary supplier is abroad. Estimated profit impact: **−$380,000** unless you act now.

Impact: `Margin: −$380k` · `Lead time risk: High` · `Supplier options: Limited`
        """)

        options = {
            "A — Absorb the cost": "Keep current supplier and reduce margins this quarter. Maintains delivery reliability, but no mitigation strategy.",
            "B — Emergency domestic switch": "Urgently onboard a local supplier. Tariff-exempt, but possible quality issues in Q4.",
            "C — Pass cost to customer": "Raise prices 8% to offset the tariff. Protects margin, but risks volume loss.",
            "D — Pre-buy safety stock now": "Place a large order at pre-tariff prices before the policy kicks in. Holding cost increases, but tariff exposure is avoided.",
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
            st.info("Hint: The tariff applies to future orders. Can you act before it takes effect? Think about buying forward and warehouse capacity.")

        if confirm_cr:
            st.session_state.crisis_confirmed = True
            st.session_state.crisis_chosen = crisis_choice

            if "Crisis response" not in done:
                if crisis_choice.startswith("D"):
                    apply_kpi_change(
                        score=10,
                        profit=-90000,
                        inventory=180000,
                        service=7,
                        sustainability=-2,
                        risk=-10,
                    )
                elif crisis_choice.startswith("A"):
                    apply_kpi_change(
                        score=-6,
                        profit=-380000,
                        service=0,
                        risk=12,
                    )
                elif crisis_choice.startswith("B"):
                    apply_kpi_change(
                        score=-3,
                        profit=-160000,
                        inventory=-40000,
                        service=-6,
                        sustainability=4,
                        lead_time=-3,
                        risk=8,
                    )
                else:
                    apply_kpi_change(
                        score=-4,
                        profit=-130000,
                        revenue=-150000,
                        inventory=30000,
                        service=-5,
                        risk=5,
                    )

                st.session_state.completed_games.append("Crisis response")

        if st.session_state.crisis_confirmed:
            ch = st.session_state.crisis_chosen

            if ch.startswith("D"):
                st.markdown("""
                <div class="result-correct">
                ✅ <strong>Correct!</strong> Pre-buying safety stock at pre-tariff prices is a buying-forward strategy. The holding cost is lower than the full tariff exposure.
                <br><br>
                <strong>KPI impact:</strong> +10 score, −$90k profit, +$180k inventory, +7 service level, −10 risk.
                </div>
                """, unsafe_allow_html=True)
            elif ch.startswith("A"):
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Passive choice.</strong> Absorbing the full cost protects operations for now, but profit drops heavily and risk remains high.
                <br><br>
                <strong>KPI impact:</strong> −6 score, −$380k profit, +12 risk.
                </div>
                """, unsafe_allow_html=True)
            elif ch.startswith("B"):
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Risky pivot.</strong> A domestic switch can reduce tariff exposure, but emergency onboarding creates quality and service risks.
                <br><br>
                <strong>KPI impact:</strong> −3 score, −$160k profit, −6 service level, +8 risk.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Demand risk.</strong> Passing costs to customers protects margin, but demand and service performance may fall.
                <br><br>
                <strong>KPI impact:</strong> −4 score, −$130k profit, −$150k revenue, −5 service level.
                </div>
                """, unsafe_allow_html=True)

    # ── GAME 4: LOGISTICS ROUTE ───────────────────────────────────────────────
    elif game_tab == "Logistics route":
        st.subheader("🗺️ Logistics Route Picker")
        st.markdown("> Ship **10,000 units** from **Shanghai → Amsterdam**. Balance speed, cost, and carbon emissions.")
        st.markdown('<span class="badge-green">Strategy challenge</span>', unsafe_allow_html=True)
        st.markdown("")

        st.markdown("**Route: 📦 Shanghai → [Transit] → Amsterdam**")
        st.markdown("")

        routes = {
            "🚢 Sea freight": {
                "cost": "$2.10/unit",
                "total": "$21,000",
                "transit": "28 days",
                "co2": "0.01 kg/unit",
                "note": "⚠️ Rotterdam strike active — +14 day delay.",
                "note_color": "red",
            },
            "✈️ Air freight": {
                "cost": "$8.40/unit",
                "total": "$84,000",
                "transit": "3 days",
                "co2": "0.89 kg/unit",
                "note": "Fast but expensive — 4× the cost of rail.",
                "note_color": "orange",
            },
            "🚂 Rail freight": {
                "cost": "$3.80/unit",
                "total": "$38,000",
                "transit": "14 days",
                "co2": "0.04 kg/unit",
                "note": "✅ Best ESG balance — avoids Rotterdam.",
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
            st.info("Hint: One route is disrupted by the active event. Of the remaining routes, which gives the best balance between cost, speed and ESG?")

        if confirm_rt:
            st.session_state.route_confirmed = True
            st.session_state.route_chosen = route_choice

            if "Logistics route" not in done:
                if "Rail" in route_choice:
                    apply_kpi_change(
                        score=7,
                        profit=-38000,
                        service=5,
                        sustainability=4,
                        lead_time=0,
                        risk=-6,
                    )
                elif "Sea" in route_choice:
                    apply_kpi_change(
                        score=-6,
                        profit=-90000,
                        inventory=-80000,
                        service=-10,
                        sustainability=3,
                        lead_time=14,
                        risk=10,
                    )
                else:
                    apply_kpi_change(
                        score=-3,
                        profit=-84000,
                        service=7,
                        sustainability=-8,
                        lead_time=-8,
                        risk=-2,
                    )

                st.session_state.completed_games.append("Logistics route")

        if st.session_state.route_confirmed:
            ch = st.session_state.route_chosen

            if "Rail" in ch:
                st.markdown("""
                <div class="result-correct">
                ✅ <strong>Correct!</strong> Rail is optimal this quarter. Sea freight is disrupted and air freight is too expensive. Rail gives the best balance of cost, lead time and ESG.
                <br><br>
                <strong>KPI impact:</strong> +7 score, −$38k profit, +5 service level, +4 ESG, −6 risk.
                </div>
                """, unsafe_allow_html=True)
            elif "Sea" in ch:
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Port blocked.</strong> Sea freight is normally cheap and sustainable, but the Rotterdam strike creates a major delay and stockout risk.
                <br><br>
                <strong>KPI impact:</strong> −6 score, −$90k profit, −10 service level, +14 lead time days.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-wrong">
                ❌ <strong>Too expensive.</strong> Air freight is fast, but the cost and emissions are too high for this shipment.
                <br><br>
                <strong>KPI impact:</strong> −3 score, −$84k profit, +7 service level, −8 ESG.
                </div>
                """, unsafe_allow_html=True)


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
                unsafe_allow_html=True
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
                    unsafe_allow_html=True
                )

    st.markdown("---")

    st.markdown("**Quarter-by-Quarter Performance**")

    performance_rows = []

    for row in st.session_state.history:
        performance_rows.append({
            "Quarter": row["Quarter"],
            "Revenue": money(row["Revenue"]),
            "Net Profit": money(row["Net Profit"]),
            "Efficiency Score": row["Efficiency Score"],
            "Service Level": f"{row['Service Level']}%",
            "ESG Score": row["ESG Score"],
            "Inventory Value": money(row["Inventory Value"]),
        })

    current_q = f"Q{st.session_state.quarter}"

    if current_q not in [row["Quarter"] for row in st.session_state.history]:
        performance_rows.append({
            "Quarter": f"{current_q} current",
            "Revenue": money(st.session_state.revenue),
            "Net Profit": money(st.session_state.net_profit),
            "Efficiency Score": st.session_state.score,
            "Service Level": f"{st.session_state.service_level}%",
            "ESG Score": st.session_state.sustainability_score,
            "Inventory Value": money(st.session_state.inventory_value),
        })

    st.table(performance_rows)

    st.markdown("---")

    st.markdown("**KPI Explanation**")
    st.markdown("""
    <div class="white-card">
    <p class="kpi-note">
    The financial overview is now linked to player decisions. Choices in the mini-games influence profit, inventory, service level, sustainability, lead time and supply chain risk.
    This makes the game more realistic because supply chain decisions involve trade-offs. For example, air freight improves service level but lowers profit and ESG performance.
    </p>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# PAGE: INSTRUCTOR
# ═══════════════════════════════════════════════════════
elif page == "👨‍🏫 Instructor view":
    st.title("Instructor — God Mode")
    st.markdown('<span class="badge-red">Instructor only</span>', unsafe_allow_html=True)
    st.markdown("")

    col_ev, col_ctrl = st.columns([1, 1])

    with col_ev:
        st.markdown("**🌍 Trigger a Global Event**")

        events = {
            "Suez Canal blockage": {
                "label": "Supply disruption",
                "desc": "All sea freight suspended globally for 1 quarter.",
                "kpi": {"lead_time": 10, "risk": 12, "service": -5},
            },
            "Factory fire — Taiwan": {
                "label": "Production crisis",
                "desc": "Semiconductor supply reduced by 40%.",
                "kpi": {"inventory": -120000, "risk": 15, "service": -8},
            },
            "Currency shock": {
                "label": "Financial shock",
                "desc": "EUR/USD moves 15% against all teams.",
                "kpi": {"profit": -150000, "risk": 8},
            },
            "Pandemic scenario": {
                "label": "Demand shock",
                "desc": "Medical demand +200%, consumer goods −30%.",
                "kpi": {"revenue": -180000, "inventory": 90000, "risk": 10},
            },
            "Import tariff hike 20%": {
                "label": "Policy change",
                "desc": "All foreign sourcing costs increase by 20%.",
                "kpi": {"profit": -120000, "risk": 9},
            },
            "Labour strike — logistics hubs": {
                "label": "Ops disruption",
                "desc": "All road freight delayed by 1 week globally.",
                "kpi": {"lead_time": 7, "service": -6, "risk": 10},
            },
        }

        for name, info in events.items():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{name}**  \n{info['desc']}")

            if c2.button("Trigger", key=f"ev_{name}"):
                st.session_state.event_label = f"⚡ {info['label']}"
                st.session_state.event = info["desc"]

                apply_kpi_change(
                    profit=info["kpi"].get("profit", 0),
                    revenue=info["kpi"].get("revenue", 0),
                    inventory=info["kpi"].get("inventory", 0),
                    service=info["kpi"].get("service", 0),
                    sustainability=info["kpi"].get("sustainability", 0),
                    lead_time=info["kpi"].get("lead_time", 0),
                    risk=info["kpi"].get("risk", 0),
                )

                st.success(f"✅ Event triggered: {name}. KPI impact applied.")

    with col_ctrl:
        st.markdown("**⚙️ Game Controls**")

        col_p1, col_p2 = st.columns(2)

        if col_p1.button("⏸ Pause game" if not st.session_state.game_paused else "▶️ Resume game"):
            st.session_state.game_paused = not st.session_state.game_paused
            status = "paused" if st.session_state.game_paused else "resumed"
            st.info(f"Game {status}.")

        if col_p2.button("⏭ Advance quarter"):
            if st.session_state.quarter < 8:
                add_current_quarter_to_history()
                st.session_state.quarter += 1

                # Small automatic market growth for the new quarter
                st.session_state.revenue = int(st.session_state.revenue * 1.04)
                st.session_state.net_profit = int(st.session_state.net_profit * 1.02)

                # Reset challenge states
                reset_quarter_games()

                st.success(f"Advanced to Q{st.session_state.quarter}. Mini-games have been reset.")
            else:
                st.warning("Already at final quarter, Q8.")

        st.markdown("---")

        if st.button("🔄 Reset entire game"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")

        st.markdown("**📊 Current Team Performance**")

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
                "Team": "⭐ GreenRoute Co.",
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

        st.markdown("---")

        st.markdown("**Current KPI Values**")

        current_kpis = {
            "KPI": [
                "Revenue",
                "Net Profit",
                "Inventory Value",
                "Service Level",
                "Sustainability Score",
                "Lead Time",
                "Supply Chain Risk",
            ],
            "Value": [
                money(st.session_state.revenue),
                money(st.session_state.net_profit),
                money(st.session_state.inventory_value),
                f"{st.session_state.service_level}%",
                f"{st.session_state.sustainability_score}/100",
                f"{st.session_state.lead_time_days} days",
                f"{st.session_state.risk_level}/100",
            ],
        }

        st.table(current_kpis)
        streamlit run linklogistics_app.py
        
