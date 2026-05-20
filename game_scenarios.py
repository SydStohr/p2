"""
Simulation Scenario Engine for HAN Supply Chain Game
Based on The Fresh Connection and SUPCHM51.

This file defines quarter-based events and KPI modifiers that
can be applied directly to the Streamlit simulation.
"""

EVENTS = {
    1: {
        "title": "Quarter 1 - Current State Analysis",
        "description": "The new management team analyses the current supply chain.",
        "learning_objective": "Supply Chain Mapping and KPI Diagnosis",
        "kpi_modifier": {
            "risk": 0,
            "lead_time": 0,
            "service_level": 0,
            "esg": 0,
            "profit": 0,
        },
    },

    2: {
        "title": "Quarter 2 - Supplier Strategy",
        "description": "Suppliers differ in cost, quality and reliability.",
        "learning_objective": "Supplier Selection and Sourcing Strategy",
        "kpi_modifier": {
            "risk": 5,
            "lead_time": 3,
            "service_level": -2,
            "profit": 20000,
        },
    },

    3: {
        "title": "Quarter 3 - Rotterdam Port Strike",
        "description": "Port strike in Rotterdam increases lead times by 14 days.",
        "learning_objective": "Risk Management and Resilience",
        "kpi_modifier": {
            "lead_time": 14,
            "risk": 12,
            "service_level": -4,
            "profit": -80000,
        },
    },

    4: {
        "title": "Quarter 4 - Demand Surge",
        "description": "Customer demand increases unexpectedly.",
        "learning_objective": "Forecasting and Capacity Planning",
        "kpi_modifier": {
            "service_level": -5,
            "inventory": -100000,
            "profit": 50000,
        },
    },

    5: {
        "title": "Quarter 5 - Sustainability Pressure",
        "description": "Customers demand greener sourcing.",
        "learning_objective": "ESG and Sustainable Supply Chains",
        "kpi_modifier": {
            "esg": 8,
            "profit": -30000,
            "risk": -2,
        },
    },

    6: {
        "title": "Quarter 6 - Tariff Shock",
        "description": "Import tariffs increase sourcing costs.",
        "learning_objective": "Global Sourcing and Total Landed Cost",
        "kpi_modifier": {
            "profit": -120000,
            "risk": 4,
        },
    },

    7: {
        "title": "Quarter 7 - Market Volatility",
        "description": "Demand becomes highly uncertain.",
        "learning_objective": "Agility and Flexibility",
        "kpi_modifier": {
            "risk": 8,
            "service_level": -3,
        },
    },

    8: {
        "title": "Quarter 8 - CEO Challenge",
        "description": "The CEO expects maximum ROI and alignment.",
        "learning_objective": "Integrated Decision-Making",
        "kpi_modifier": {
            "profit": 100000,
            "risk": -5,
            "service_level": 3,
            "esg": 3,
        },
    },
}


def get_event_for_quarter(quarter):
    return EVENTS.get(quarter, EVENTS[1])


def apply_event_modifiers(state, quarter):
    """
    Apply KPI impacts of the quarter event to the existing session state.
    """
    event = get_event_for_quarter(quarter)
    modifiers = event["kpi_modifier"]

    for key, change in modifiers.items():
        if key in state:
            state[key] += change

    return state