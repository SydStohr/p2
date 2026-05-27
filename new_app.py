import streamlit as st
import pandas as pd
from game_scenarios import EVENTS

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Supply Chain Game HAN",
    page_icon="🚚",
    layout="wide"
)

# =========================================================
# DEFAULT SESSION STATE
# =========================================================

defaults = {
    "team_name": "GreenRoute Co.",
    "quarter": 1,
    "score": 74,
    "revenue": 3800000,
    "net_profit": 1240000,
    "inventory_value": 860000,
    "service_level": 87,
    "sustainability_score": 76,
    "lead_time_days": 14,
    "risk_level": 42,
    "selected_department": "Purchasing",
    "decision_log": [],
    "completed_games": [],
    "current_page": "Dashboard"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# FUNCTIONS
# =========================================================

def get_event_for_quarter(quarter):
    return EVENTS.get(quarter)

def money(value):
    return f"${value:,.0f}"

def risk_label(score):
    if score <= 30:
        return "Low"
    elif score <= 60:
        return "Medium"
    return "High"

def sustainability_rating(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B+"
    elif score >= 70:
        return "B"
    return "C"

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🚚 Supply Chain Game")

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Decision Log",
            "Quarter Summary"
        ]
    )

    st.markdown("---")

    st.session_state.team_name = st.text_input(
        "Team Name",
        value=st.session_state.team_name
    )

    st.session_state.quarter = st.slider(
        "Quarter",
        1,
        8,
        st.session_state.quarter
    )

# =========================================================
# CURRENT EVENT
# =========================================================

current_event = get_event_for_quarter(
    st.session_state.quarter
)

# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    st.title("📊 Supply Chain Dashboard")

    st.markdown(f"""
## {current_event['title']}

{current_event['description']}

### Learning Objective
{current_event['learning_objective']}

### Main Calculation
{current_event['main_calculation']}

### Strategy Focus
{current_event['strategy_focus']}
""")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Net Profit",
        money(st.session_state.net_profit)
    )

    col2.metric(
        "Service Level",
        f"{st.session_state.service_level}%"
    )

    col3.metric(
        "ESG Rating",
        sustainability_rating(
            st.session_state.sustainability_score
        )
    )

    col4.metric(
        "Risk",
        risk_label(
            st.session_state.risk_level
        )
    )

    st.markdown("---")

    st.subheader("Current KPI Status")

    st.write(f"Revenue: {money(st.session_state.revenue)}")
    st.write(f"Inventory Value: {money(st.session_state.inventory_value)}")
    st.write(f"Lead Time: {st.session_state.lead_time_days} days")

# =========================================================
# DECISION LOG
# =========================================================

elif page == "Decision Log":

    st.title("📝 Decision Log")

    st.markdown(f"""
## {current_event['title']}

{current_event['description']}

### Learning Objective
{current_event['learning_objective']}

### Main Calculation
{current_event['main_calculation']}

### Strategy Focus
{current_event['strategy_focus']}
""")

    st.markdown("---")

    department = st.selectbox(
        "Select Department",
        list(current_event["department_decisions"].keys())
    )

    st.session_state.selected_department = department

    decision = st.radio(
        f"{department} Decision",
        current_event["department_decisions"][department]
    )

    if st.button("✅ Confirm Decision"):

        st.session_state.decision_log.append({

            "Quarter":
            st.session_state.quarter,

            "Department":
            department,

            "Decision":
            decision,

            "Scenario":
            current_event["title"],

            "Learning Objective":
            current_event["learning_objective"]
        })

        st.success(
            f"{department} decision recorded successfully."
        )

# =========================================================
# QUARTER SUMMARY
# =========================================================

elif page == "Quarter Summary":

    st.title("📋 Quarter Summary")

    st.markdown(f"""
### Quarter {st.session_state.quarter}

**Scenario:** {current_event['title']}

**Learning Objective:**  
{current_event['learning_objective']}
""")

    st.markdown("---")

    if len(st.session_state.decision_log) == 0:

        st.warning(
            "No decisions recorded yet."
        )

    else:

        df = pd.DataFrame(
            st.session_state.decision_log
        )

        st.dataframe(
            df,
            use_container_width=True
        )

    st.markdown("---")

    st.subheader("Reflection Questions")

    st.markdown("""
1. Which decision created the biggest KPI impact?

2. Did your departments align strategically?

3. What would you improve next quarter?

4. Did you focus more on profit, resilience, or sustainability?
""")

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Supply Chain Game HAN • Educational SCM Simulation"
)
