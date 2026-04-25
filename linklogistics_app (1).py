import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LinkLogistics",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ────────────────────────────────────────────────────
defaults = {
    "score": 74,
    "quarter": 3,
    "event": "Port strike in Rotterdam — sea freight lead times +14 days.",
    "event_label": "Active Black Swan",
    "supp_chosen": None,
    "supp_confirmed": False,
    "forecast_confirmed": False,
    "crisis_chosen": None,
    "crisis_confirmed": False,
    "route_chosen": None,
    "route_confirmed": False,
    "game_paused": False,
    "completed_games": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

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
section[data-testid="stSidebar"] * { color: #E8E6E0 !important; }
section[data-testid="stSidebar"] .stRadio label { color: rgba(232,230,224,0.7) !important; }

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
.stButton > button:hover { border-color: rgba(28,27,25,0.5); }

/* Progress bar */
.stProgress > div > div { background-color: #185FA5 !important; }

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
.event-label { font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #633806; }

/* Result boxes */
.result-correct {
    background: #EAF3DE; border: 1px solid #97C459; border-radius: 10px;
    padding: 14px 16px; font-size: 13px; color: #173404; margin-top: 12px; line-height: 1.6;
}
.result-wrong {
    background: #FAECE7; border: 1px solid #F09595; border-radius: 10px;
    padding: 14px 16px; font-size: 13px; color: #501313; margin-top: 12px; line-height: 1.6;
}
.result-hint {
    background: #EDECE8; border: 1px solid rgba(28,27,25,0.15); border-radius: 10px;
    padding: 14px 16px; font-size: 13px; color: #5F5E5A; margin-top: 12px; line-height: 1.6;
}

/* Supplier card */
.supp-card {
    background: #FFFFFF; border: 1px solid rgba(28,27,25,0.12);
    border-radius: 10px; padding: 14px 16px; height: 100%;
}
.supp-card.selected {
    border: 2px solid #185FA5; background: #E6F1FB;
}
.supp-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #1C1B19; }
.supp-row { display: flex; justify-content: space-between; font-size: 12px; color: #888780; padding: 2px 0; }
.supp-val { color: #1C1B19; font-family: 'DM Mono', monospace; }

/* Leaderboard */
.lb-row {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 0; border-bottom: 1px solid rgba(28,27,25,0.08); font-size: 14px;
}
.lb-row:last-child { border-bottom: none; }
.lb-you { color: #185FA5; font-weight: 600; }
.you-tag {
    font-size: 10px; background: #E6F1FB; color: #0C447C;
    border-radius: 4px; padding: 1px 6px; margin-left: 4px;
}

/* PnL table */
.pnl-row {
    display: flex; justify-content: space-between;
    font-size: 13px; padding: 6px 0; border-bottom: 1px solid rgba(28,27,25,0.08);
}
.pnl-row:last-child { border-bottom: none; font-weight: 600; font-size: 14px; }
.pnl-label { color: #5F5E5A; }
.pnl-pos { color: #0F6E56; font-family: 'DM Mono', monospace; }
.pnl-neg { color: #993C1D; font-family: 'DM Mono', monospace; }

/* Sustain */
.sus-row { display: flex; align-items: center; gap: 10px; font-size: 13px; margin-bottom: 8px; }
.sus-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }

/* Cards white background */
.white-card {
    background: #FFFFFF; border: 1px solid rgba(28,27,25,0.12);
    border-radius: 12px; padding: 18px 20px; margin-bottom: 16px;
}
.card-label {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.6px; color: #888780; margin-bottom: 12px;
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
    st.markdown(f"**GreenRoute Co.** · Group 4")
    st.markdown(f"Quarter {st.session_state.quarter} of 8")
    st.progress(st.session_state.quarter / 8)
    st.markdown(f"**Score: {st.session_state.score}**")
    st.caption("Global Efficiency Score")

    if st.session_state.game_paused:
        st.warning("⏸ Game is paused")

# ═══════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title(f"Quarter {st.session_state.quarter} Overview")

    # Event banner
    st.markdown(f"""
    <div class="event-banner">
        <div class="event-label">🔴 {st.session_state.event_label}</div>
        <div style="margin-top:4px;">{st.session_state.event}</div>
    </div>
    """, unsafe_allow_html=True)

    # Stat cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Global Efficiency Score", st.session_state.score, "+6 from Q2")
    with c2:
        st.metric("Net Profit", "$1.24M", "+$210k")
    with c3:
        st.metric("Inventory Value", "$860k", "-High holding cost", delta_color="inverse")
    with c4:
        st.metric("Sustainability Rating", "B+", "Target A by Q6")

    st.markdown("---")

    # Mid row
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="white-card"><div class="card-label">Inventory Levels</div>', unsafe_allow_html=True)
        inventory = {
            "Raw materials": (82, "#185FA5"),
            "Work in progress": (55, "#1D9E75"),
            "Finished goods": (31, "#D85A30"),
            "Safety stock": (68, "#BA7517"),
        }
        for name, (pct, color) in inventory.items():
            cols = st.columns([3, 1])
            cols[0].markdown(f"**{name}**")
            cols[1].markdown(f"`{pct}%`")
            st.progress(pct / 100)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="white-card"><div class="card-label">Leaderboard — Q3</div>', unsafe_allow_html=True)
        leaderboard = [
            (1, "Team Apex", 91, False),
            (2, "NovaTrade", 88, False),
            (3, "LogiX Group", 83, False),
            (4, "GreenRoute Co.", st.session_state.score, True),
            (5, "FastLink", 69, False),
            (6, "ChainMasters", 61, False),
        ]
        for rank, name, score, is_you in leaderboard:
            medal = "🥇" if rank == 1 else f"{rank}."
            if is_you:
                st.markdown(f"**{medal} 🔵 {name}** ← you &nbsp;&nbsp; **{score}**")
            else:
                st.markdown(f"{medal} {name} &nbsp;&nbsp; {score}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    col_l2, col_r2 = st.columns(2)

    with col_l2:
        st.markdown('<div class="white-card"><div class="card-label">P&L — Q3 Snapshot</div>', unsafe_allow_html=True)
        pnl = [
            ("Revenue", "$3,800,000", True),
            ("Cost of goods sold", "−$2,100,000", False),
            ("Logistics costs", "−$340,000", False),
            ("Holding costs", "−$120,000", False),
            ("Net profit", "$1,240,000", True),
        ]
        for label, val, pos in pnl:
            col_a, col_b = st.columns([3, 2])
            col_a.markdown(f"{'**' if label == 'Net profit' else ''}{label}{'**' if label == 'Net profit' else ''}")
            color = "green" if pos else "red"
            col_b.markdown(f"<span style='color:{'#0F6E56' if pos else '#993C1D'};font-family:monospace;'>{'**' if label == 'Net profit' else ''}{val}{'**' if label == 'Net profit' else ''}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r2:
        st.markdown('<div class="white-card"><div class="card-label">Sustainability Breakdown</div>', unsafe_allow_html=True)
        sustain = [
            ("Carbon emissions", 72, "#1D9E75"),
            ("Supplier ESG rating", 80, "#185FA5"),
            ("Packaging waste", 58, "#BA7517"),
            ("Labour practices", 66, "#D85A30"),
        ]
        for name, val, color in sustain:
            cols = st.columns([3, 1])
            cols[0].markdown(f"**{name}**")
            cols[1].markdown(f"`{val}/100`")
            st.progress(val / 100)
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# PAGE: MINI-GAMES
# ═══════════════════════════════════════════════════════
elif page == "🎮 Mini-games":
    st.title("Learning Activities")
    st.caption(f"Complete all four challenges this quarter · Q{st.session_state.quarter}")

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
        st.markdown('<span style="background:#FAEEDA;color:#633806;border-radius:6px;padding:3px 9px;font-size:12px;font-weight:500;">Medium difficulty</span>', unsafe_allow_html=True)
        st.markdown("")

        suppliers = {
            "Shenzhen FastMfg": {
                "Cost": "$12/unit", "Lead time": "28 days (sea)", "ESG": "★★☆☆☆", "Reliability": "91%",
                "desc": "Cheapest option — but routes through Rotterdam."
            },
            "EuroManuf GmbH": {
                "Cost": "$19/unit", "Lead time": "6 days (rail)", "ESG": "★★★★☆", "Reliability": "97%",
                "desc": "More expensive — but uses rail, bypassing the port strike."
            },
            "SwiftAir Logistics": {
                "Cost": "$31/unit", "Lead time": "2 days (air)", "ESG": "★★☆☆☆", "Reliability": "99%",
                "desc": "Fastest option — but very costly and high emissions."
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
                st.caption(info['desc'])

        st.markdown("")
        chosen = st.radio(
            "Select your supplier:",
            list(suppliers.keys()),
            key="supp_radio",
            horizontal=True,
        )

        col_btn1, col_btn2, _ = st.columns([1, 1, 4])
        confirm = col_btn1.button("✅ Confirm selection", key="supp_confirm_btn", disabled=st.session_state.supp_confirmed)
        hint = col_btn2.button("💡 Show hint", key="supp_hint_btn")

        if hint:
            st.info("**Hint:** Rotterdam is the affected port. Which supplier uses a transport mode that completely bypasses sea freight? Also consider how your choice affects your sustainability leaderboard position.")

        if confirm:
            st.session_state.supp_confirmed = True
            st.session_state.supp_chosen = chosen
            if chosen == "EuroManuf GmbH" and "Supplier selection" not in done:
                st.session_state.score += 8
                st.session_state.completed_games.append("Supplier selection")

        if st.session_state.supp_confirmed:
            ch = st.session_state.supp_chosen
            if ch == "EuroManuf GmbH":
                st.markdown('<div class="result-correct">✅ <strong>Correct!</strong> EuroManuf GmbH avoids Rotterdam entirely via rail. Their higher cost ($19 vs $12) is offset by avoiding a stockout from the 14-day delay. Their ESG rating also boosts your sustainability score. <strong>+8 points added to your score!</strong></div>', unsafe_allow_html=True)
            elif ch == "Shenzhen FastMfg":
                st.markdown('<div class="result-wrong">❌ <strong>Not optimal.</strong> Shenzhen FastMfg ships through Rotterdam — the port strike adds 14+ days, causing a stockout risk. When a key node is disrupted, routing <em>around</em> it is the core SCM principle to apply.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-wrong">❌ <strong>Too costly.</strong> SwiftAir at $31/unit collapses your margin. Air freight is a last resort for emergencies, not bulk orders. Your P&L takes a $190k hit vs the rail option.</div>', unsafe_allow_html=True)

    # ── GAME 2: DEMAND FORECASTING ─────────────────────────────────────────────
    elif game_tab == "Demand forecast":
        st.subheader("📈 Demand Forecasting Quiz")
        st.markdown("> Read the market report below, then set your Q4 demand forecast. Accuracy within **15%** earns full points.")
        st.markdown('<span style="background:#E6F1FB;color:#0C447C;border-radius:6px;padding:3px 9px;font-size:12px;font-weight:500;">Hard difficulty</span>', unsafe_allow_html=True)
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
                "Drag to set your forecast (units)",
                min_value=30000,
                max_value=70000,
                value=47000,
                step=500,
                key="forecast_slider",
                disabled=st.session_state.forecast_confirmed,
            )
            st.markdown(f"### `{forecast:,} units`")
            st.caption("The Bullwhip Effect: small demand changes get amplified upstream. Be careful not to over-order — excess safety stock compounds holding costs.")

        col_b1, col_b2, _ = st.columns([1, 1, 4])
        confirm_fc = col_b1.button("✅ Submit forecast", key="fc_confirm", disabled=st.session_state.forecast_confirmed)
        hint_fc = col_b2.button("💡 Bullwhip effect?", key="fc_hint")

        if hint_fc:
            st.info("**Bullwhip Effect:** A small 5% change in customer demand can cause a 30–40% order surge at the manufacturer level. Always anchor forecasts to end-consumer data, not upstream orders. Over-forecasting is often more expensive than under-forecasting.")

        if confirm_fc:
            st.session_state.forecast_confirmed = True
            correct = 48000
            pct_off = abs(forecast - correct) / correct * 100
            if pct_off <= 15 and "Demand forecast" not in done:
                st.session_state.score += 6
                st.session_state.completed_games.append("Demand forecast")

        if st.session_state.forecast_confirmed:
            correct = 48000
            pct_off = abs(forecast - correct) / correct * 100
            if pct_off <= 15:
                st.markdown(f'<div class="result-correct">✅ <strong>Good forecast!</strong> The correct answer was ~48,000 units. Q3 actual: 42,000 + 12% seasonal = 47,040, and competitor stockout adds ~2%, partially offset by the 5% tariff. Your estimate was {pct_off:.1f}% off — within the 15% accuracy threshold. <strong>+6 points added!</strong></div>', unsafe_allow_html=True)
            elif forecast > correct:
                st.markdown(f'<div class="result-wrong">❌ <strong>Overforecast.</strong> You predicted {forecast:,} vs actual ~48,000. Over-ordering triggers the Bullwhip Effect: excess inventory, high holding costs, and amplified waste upstream. Try to anchor closer to historical data + seasonal trend.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="result-wrong">❌ <strong>Underforecast.</strong> You predicted {forecast:,} vs actual ~48,000. Underestimating demand causes stockouts, lost sales, and a damaged service level score.</div>', unsafe_allow_html=True)

    # ── GAME 3: CRISIS RESPONSE ───────────────────────────────────────────────
    elif game_tab == "Crisis response":
        st.subheader("🚨 Crisis Response — 20% Tariff Hike")
        st.markdown('<span style="background:#FAECE7;color:#993C1D;border-radius:6px;padding:3px 9px;font-size:12px;font-weight:500;">⚡ Urgent</span>', unsafe_allow_html=True)
        st.markdown("")

        st.error("""
**🚨 Breaking — Trade Policy Alert**

The government just announced a **20% import tariff** on all electronics components, effective next quarter.
Your primary supplier is abroad. Estimated profit impact: **−$380,000** unless you act now.

Impact: `Margin: −$380k` · `Lead time risk: High` · `Supplier options: Limited`
        """)

        options = {
            "A — Absorb the cost": "Keep current supplier, reduce margins this quarter. Maintains delivery reliability but no mitigation strategy.",
            "B — Emergency domestic switch": "Urgently onboard a local supplier (+$7/unit, tariff-exempt). Risk of quality issues in Q4.",
            "C — Pass cost to customer": "Raise prices 8% to offset tariff. Protects margins but risks −15% volume loss.",
            "D — Pre-buy safety stock now": "Place a large order at pre-tariff prices before policy kicks in. Holding cost +$90k but avoids tariff exposure.",
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
        confirm_cr = col_c1.button("✅ Confirm response", key="crisis_confirm", disabled=st.session_state.crisis_confirmed)
        hint_cr = col_c2.button("💡 Show hint", key="crisis_hint")

        if hint_cr:
            st.info("**Hint:** The tariff applies to *future* orders. Is there a way to protect yourself by acting *before* it takes effect? Think about what your warehouse capacity allows.")

        if confirm_cr:
            st.session_state.crisis_confirmed = True
            st.session_state.crisis_chosen = crisis_choice
            if crisis_choice.startswith("D") and "Crisis response" not in done:
                st.session_state.score += 10
                st.session_state.completed_games.append("Crisis response")

        if st.session_state.crisis_confirmed:
            ch = st.session_state.crisis_chosen
            if ch.startswith("D"):
                st.markdown('<div class="result-correct">✅ <strong>Correct!</strong> Pre-buying safety stock at pre-tariff prices is the classic "buying forward" strategy. You lock in lower costs before the policy kicks in. The $90k holding cost is far lower than $380k tariff exposure. This is a real-world tactic used by Apple and Toyota. <strong>+10 points added!</strong></div>', unsafe_allow_html=True)
            elif ch.startswith("A"):
                st.markdown('<div class="result-wrong">❌ <strong>Passive choice.</strong> Absorbing the full cost without any mitigation is rarely optimal in SCM. It signals to stakeholders that you have no resilience plan.</div>', unsafe_allow_html=True)
            elif ch.startswith("B"):
                st.markdown('<div class="result-wrong">❌ <strong>Risky pivot.</strong> Emergency supplier onboarding in one quarter typically causes quality issues and delivery delays, hurting your Q4 service level score significantly.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-wrong">❌ <strong>Demand risk.</strong> A 15% volume loss often outweighs margin gains from a price increase. Market share, once lost, is expensive to recover.</div>', unsafe_allow_html=True)

    # ── GAME 4: LOGISTICS ROUTE ───────────────────────────────────────────────
    elif game_tab == "Logistics route":
        st.subheader("🗺️ Logistics Route Picker")
        st.markdown("> Ship **10,000 units** from **Shanghai → Amsterdam**. Balance speed, cost, and carbon emissions.")
        st.markdown('<span style="background:#EAF3DE;color:#0F6E56;border-radius:6px;padding:3px 9px;font-size:12px;font-weight:500;">Strategy challenge</span>', unsafe_allow_html=True)
        st.markdown("")

        st.markdown("**Route: 📦 Shanghai → [Transit] → Amsterdam**")
        st.markdown("")

        routes = {
            "🚢 Sea freight": {
                "cost": "$2.10/unit", "total": "$21,000", "transit": "28 days",
                "co2": "0.01 kg/unit", "note": "⚠️ Rotterdam strike active — +14 day delay!",
                "note_color": "red",
            },
            "✈️ Air freight": {
                "cost": "$8.40/unit", "total": "$84,000", "transit": "3 days",
                "co2": "0.89 kg/unit", "note": "Fast but expensive — 4× the cost of rail",
                "note_color": "orange",
            },
            "🚂 Rail freight": {
                "cost": "$3.80/unit", "total": "$38,000", "transit": "14 days",
                "co2": "0.04 kg/unit", "note": "✅ Best ESG balance — avoids Rotterdam",
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
        confirm_rt = col_r1.button("✅ Confirm route", key="route_confirm", disabled=st.session_state.route_confirmed)
        hint_rt = col_r2.button("💡 Show hint", key="route_hint")

        if hint_rt:
            st.info("**Hint:** One route is blocked by the active event. Of the remaining two, which gives the best balance of cost and ESG? Think: Total Landed Cost = cost per unit × volume.")

        if confirm_rt:
            st.session_state.route_confirmed = True
            st.session_state.route_chosen = route_choice
            if "Rail" in route_choice and "Logistics route" not in done:
                st.session_state.score += 7
                st.session_state.completed_games.append("Logistics route")

        if st.session_state.route_confirmed:
            ch = st.session_state.route_chosen
            if "Rail" in ch:
                st.markdown('<div class="result-correct">✅ <strong>Correct!</strong> Rail is optimal this quarter. Sea is disrupted (+14 days delay). Air costs $84k vs rail\'s $38k — a $46,000 difference on this shipment alone. Rail also has the best ESG score of the available alternatives. <strong>+7 points added!</strong></div>', unsafe_allow_html=True)
            elif "Sea" in ch:
                st.markdown('<div class="result-wrong">❌ <strong>Port blocked.</strong> Sea freight via Rotterdam faces a 14+ day delay on top of the normal 28 days. This creates a stockout and drops your service level score significantly.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-wrong">❌ <strong>Too expensive.</strong> Air freight costs $84,000 vs $38,000 by rail — a $46,000 unnecessary spend. Air freight is justified only for urgent, high-margin, low-volume shipments.</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# PAGE: FINANCIALS
# ═══════════════════════════════════════════════════════
elif page == "💰 Financials":
    st.title("Financial Statements")
    st.caption("Auto-generated after every quarter.")

    col_fl, col_fr = st.columns(2)

    with col_fl:
        st.markdown("**Income Statement — Year to Q3**")
        income = [
            ("Q1 Revenue", "$3,200,000", True),
            ("Q2 Revenue", "$3,550,000", True),
            ("Q3 Revenue", "$3,800,000", True),
            ("Total Revenue", "$10,550,000", True),
            ("Total COGS", "−$5,900,000", False),
            ("Total Logistics", "−$980,000", False),
            ("Total Holding Costs", "−$310,000", False),
            ("Net Profit YTD", "$3,360,000", True),
        ]
        for label, val, pos in income:
            c1, c2 = st.columns([3, 2])
            bold = label in ("Total Revenue", "Net Profit YTD")
            c1.markdown(f"{'**' if bold else ''}{label}{'**' if bold else ''}")
            c2.markdown(f"<span style='color:{'#0F6E56' if pos else '#993C1D'};font-family:monospace;'>{'**' if bold else ''}{val}{'**' if bold else ''}</span>", unsafe_allow_html=True)

    with col_fr:
        st.markdown("**Balance Sheet**")
        balance = [
            ("— ASSETS —", "", None),
            ("Cash", "$2,100,000", True),
            ("Inventory", "$860,000", True),
            ("Accounts Receivable", "$540,000", True),
            ("— LIABILITIES —", "", None),
            ("Accounts Payable", "−$320,000", False),
            ("Short-term Debt", "−$150,000", False),
            ("Net Equity", "$3,030,000", True),
        ]
        for label, val, pos in balance:
            c1, c2 = st.columns([3, 2])
            if pos is None:
                c1.markdown(f"**{label}**")
            else:
                bold = label == "Net Equity"
                c1.markdown(f"{'**' if bold else ''}{label}{'**' if bold else ''}")
                c2.markdown(f"<span style='color:{'#0F6E56' if pos else '#993C1D'};font-family:monospace;'>{'**' if bold else ''}{val}{'**' if bold else ''}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Quarter-by-Quarter Performance**")
    perf_data = {
        "Quarter": ["Q1", "Q2", "Q3 (current)"],
        "Revenue": ["$3,200,000", "$3,550,000", "$3,800,000"],
        "Net Profit": ["$900,000", "$1,030,000", "$1,240,000"],
        "Efficiency Score": [62, 68, st.session_state.score],
    }
    st.table(perf_data)

# ═══════════════════════════════════════════════════════
# PAGE: INSTRUCTOR
# ═══════════════════════════════════════════════════════
elif page == "👨‍🏫 Instructor view":
    st.title("Instructor — God Mode")
    st.markdown('<span style="background:#FAECE7;color:#993C1D;border-radius:6px;padding:3px 9px;font-size:12px;font-weight:500;">Instructor only</span>', unsafe_allow_html=True)
    st.markdown("")

    col_ev, col_ctrl = st.columns([1, 1])

    with col_ev:
        st.markdown("**🌍 Trigger a Global Event**")
        events = {
            "Suez Canal blockage": ("Supply disruption", "All sea freight suspended globally for 1 quarter."),
            "Factory fire — Taiwan": ("Production crisis", "Semiconductor supply reduced by 40%."),
            "Currency shock": ("Financial shock", "EUR/USD moves 15% against all teams."),
            "Pandemic scenario": ("Demand shock", "Medical demand +200%, consumer goods −30%."),
            "Import tariff hike (20%)": ("Policy change", "All foreign sourcing costs increase by 20%."),
            "Labour strike — logistics hubs": ("Ops disruption", "All road freight delayed by 1 week globally."),
        }
        for name, (label, desc) in events.items():
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{name}**  \n{desc}")
            if c2.button("Trigger", key=f"ev_{name}"):
                st.session_state.event_label = f"⚡ {label}"
                st.session_state.event = desc
                st.success(f"✅ Event triggered: {name} — all teams notified.")

    with col_ctrl:
        st.markdown("**⚙️ Game Controls**")
        col_p1, col_p2 = st.columns(2)
        if col_p1.button("⏸ Pause game" if not st.session_state.game_paused else "▶️ Resume game"):
            st.session_state.game_paused = not st.session_state.game_paused
            status = "paused" if st.session_state.game_paused else "resumed"
            st.info(f"Game {status}.")

        if col_p2.button("⏭ Advance quarter"):
            if st.session_state.quarter < 8:
                st.session_state.quarter += 1
                # Reset game states for new quarter
                for k in ["supp_confirmed", "forecast_confirmed", "crisis_confirmed", "route_confirmed"]:
                    st.session_state[k] = False
                st.session_state.completed_games = []
                st.success(f"Advanced to Q{st.session_state.quarter}. All teams notified.")
            else:
                st.warning("Already at final quarter (Q8).")

        st.markdown("---")
        st.markdown("**📊 All Teams — Q3 Performance**")
        teams = [
            {"Team": "Team Apex", "Score": 91, "Profit": "$1.82M", "ESG": "A"},
            {"Team": "NovaTrade", "Score": 88, "Profit": "$1.71M", "ESG": "B+"},
            {"Team": "LogiX Group", "Score": 83, "Profit": "$1.58M", "ESG": "B"},
            {"Team": "⭐ GreenRoute Co.", "Score": st.session_state.score, "Profit": "$1.24M", "ESG": "B+"},
            {"Team": "FastLink", "Score": 69, "Profit": "$1.10M", "ESG": "C+"},
            {"Team": "ChainMasters", "Score": 61, "Profit": "−$220k", "ESG": "C"},
        ]
        st.table(teams)
