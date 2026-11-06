import json
import operator
import streamlit as st

# Scholarship rules supplied in the assignment.
# Keep the rule names, priorities, conditions, actions, and reasons unchanged.
DEFAULT_RULES = [
    {
        "name": "Top merit candidate",
        "priority": 100,
        "conditions": [
            ["cgpa", ">=", 3.7],
            ["co_curricular_score", ">=", 80],
            ["family_income", "<=", 8000],
            ["disciplinary_actions", "==", 0]
        ],
        "action": {
            "decision": "AWARD_FULL",
            "reason": "Excellent academic & co-curricular performance, with acceptable need"
        }
    },
    {
        "name": "Good candidate - partial scholarship",
        "priority": 80,
        "conditions": [
            ["cgpa", ">=", 3.3],
            ["co_curricular_score", ">=", 60],
            ["family_income", "<=", 12000],
            ["disciplinary_actions", "<=", 1]
        ],
        "action": {
            "decision": "AWARD_PARTIAL",
            "reason": "Good academic & involvement record with moderate need"
        }
    },
    {
        "name": "Need-based review",
        "priority": 70,
        "conditions": [
            ["cgpa", ">=", 2.5],
            ["family_income", "<=", 4000]
        ],
        "action": {
            "decision": "REVIEW",
            "reason": "High need but borderline academic score"
        }
    },
    {
        "name": "Low CGPA – not eligible",
        "priority": 95,
        "conditions": [
            ["cgpa", "<", 2.5]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "CGPA below minimum scholarship requirement"
        }
    },
    {
        "name": "Serious disciplinary record",
        "priority": 90,
        "conditions": [
            ["disciplinary_actions", ">=", 2]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "Too many disciplinary records"
        }
    }
]

OPERATORS = {
    "==": operator.eq,
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt
}


def evaluate_condition(applicant, condition):
    """Return True when one condition is satisfied."""
    attribute, comparison, required_value = condition

    if attribute not in applicant:
        raise ValueError(f"Unknown applicant attribute: {attribute}")

    if comparison not in OPERATORS:
        raise ValueError(f"Unsupported comparison operator: {comparison}")

    return OPERATORS[comparison](applicant[attribute], required_value)


def evaluate_rules(applicant, rules):
    """Find all matching rules and select the one with the highest priority."""
    matched_rules = []

    for rule in rules:
        conditions = rule.get("conditions", [])

        # All conditions in a rule must be true.
        if all(evaluate_condition(applicant, condition) for condition in conditions):
            matched_rules.append(rule)

    if not matched_rules:
        return None, []

    # Highest priority wins. If priorities tie, the first rule in the JSON is selected.
    selected_rule = max(matched_rules, key=lambda rule: rule["priority"])
    return selected_rule, matched_rules


st.set_page_config(
    page_title="Scholarship Advisory System",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Scholarship Advisory System")
st.write(
    "Enter the applicant's information and click **Evaluate Eligibility** "
    "to receive a scholarship recommendation."
)

st.subheader("Applicant Information")

with st.form("applicant_form"):
    cgpa = st.number_input(
        "CGPA",
        min_value=0.0,
        max_value=4.0,
        value=3.50,
        step=0.01,
        format="%.2f"
    )

    co_curricular_score = st.number_input(
        "Co-curricular Score",
        min_value=0.0,
        max_value=100.0,
        value=70.0,
        step=1.0
    )

    family_income = st.number_input(
        "Family Income (RM)",
        min_value=0.0,
        value=5000.0,
        step=100.0
    )

    disciplinary_actions = st.number_input(
        "Number of Disciplinary Actions",
        min_value=0,
        value=0,
        step=1
    )

    submitted = st.form_submit_button(
        "Evaluate Eligibility",
        type="primary",
        use_container_width=True
    )

# The assignment requires the supplied rules to be entered in a JSON editor.
# The editor is placed in an expander to keep the main interface simple.
with st.expander("View / Edit JSON Rules"):
    st.caption(
        "The five default rules are provided below. Keep their original values "
        "as specified in the assignment."
    )
    rules_json = st.text_area(
        "JSON Rule Editor",
        value=json.dumps(DEFAULT_RULES, indent=4, ensure_ascii=False),
        height=420
    )

if submitted:
    applicant_data = {
        "cgpa": cgpa,
        "co_curricular_score": co_curricular_score,
        "family_income": family_income,
        "disciplinary_actions": disciplinary_actions
    }

    try:
        rules = json.loads(rules_json)

        if not isinstance(rules, list):
            raise ValueError("The JSON rules must be a list of rule objects.")

        selected_rule, matched_rules = evaluate_rules(applicant_data, rules)

        st.divider()
        st.subheader("Scholarship Assessment Result")

        if selected_rule is None:
            st.warning("NO MATCHING RULE")
            st.write(
                "No scholarship rule matches the applicant's information. "
                "Please refer the application for manual assessment."
            )
        else:
            decision = selected_rule["action"]["decision"]
            reason = selected_rule["action"]["reason"]

            if decision == "REJECT":
                st.error(f"Decision: {decision}")
            elif decision == "REVIEW":
                st.warning(f"Decision: {decision}")
            else:
                st.success(f"Decision: {decision}")

            st.write(f"**Selected Rule:** {selected_rule['name']}")
            st.write(f"**Priority:** {selected_rule['priority']}")
            st.write(f"**Reason:** {reason}")

            with st.expander("View matching rules"):
                for rule in sorted(
                    matched_rules,
                    key=lambda item: item["priority"],
                    reverse=True
                ):
                    st.write(
                        f"- {rule['name']} (Priority: {rule['priority']})"
                    )

    except json.JSONDecodeError as error:
        st.error(f"Invalid JSON format: {error}")
    except (KeyError, TypeError, ValueError) as error:
        st.error(f"Unable to evaluate the rules: {error}")

st.divider()
st.caption("Rule-Based Expert System | Knowledge Representation System")
