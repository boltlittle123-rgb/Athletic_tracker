import os
import pandas as pd
import streamlit as st

DATA_FILE = "athlete_prs.csv"

# Configure page
st.set_page_config(page_title="Performance & PR Tracker", layout="wide")


# Load existing data or create default dataset
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(
        {
            "Date": ["2026-09-01", "2026-09-05", "2026-09-12"],
            "Event": ["100m Dash", "100m Dash", "100m Dash"],
            "Value": [13.4, 13.1, 12.9],
            "Notes": ["First meet", "Good block start", "New PR!"],
        }
    )


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = load_data()

st.title("🏃‍♀️ Athletic Performance & PR Tracker")

# Sidebar - Data Input Form
st.sidebar.header("Log New Record / Workout")
with st.sidebar.form("entry_form", clear_on_submit=True):
    date_val = st.date_input("Date")
    event_val = st.selectbox(
        "Select Event / Lift",
        [
            "100m Dash",
            "400m Dash",
            "5k Run",
            "Squat (lbs)",
            "Bench Press (lbs)",
            "Vertical Jump (in)",
        ],
    )
    metric_val = st.number_input(
        "Result (seconds, min, lbs, or in)", min_value=0.0, step=0.1
    )
    notes_val = st.text_input("Notes / Context")
    submitted = st.form_submit_button("Save Entry")

    if submitted:
        new_row = pd.DataFrame(
            {
                "Date": [str(date_val)],
                "Event": [event_val],
                "Value": [float(metric_val)],
                "Notes": [notes_val],
            }
        )
        st.session_state.data = pd.concat(
            [st.session_state.data, new_row], ignore_index=True
        )
        save_data(st.session_state.data)
        st.success("Entry saved!")

# Main Dashboard View
all_events = st.session_state.data["Event"].unique()
selected_event = st.selectbox("Select Event to Analyze:", all_events)

filtered_df = st.session_state.data[
    st.session_state.data["Event"] == selected_event
].copy()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Progress Over Time: {selected_event}")
    if not filtered_df.empty:
        st.line_chart(filtered_df, x="Date", y="Value")
    else:
        st.info("No data recorded for this event yet.")

with col2:
    st.subheader("Key Statistics")
    if not filtered_df.empty:
        # Fixed statistic calculation
        numeric_values = pd.to_numeric(filtered_df["Value"], errors="coerce")
        is_timed = any(
            unit in str(selected_event).lower() for unit in ["dash", "run"]
        )

        if is_timed:
            best_val = numeric_values.min()
        else:
            best_val = numeric_values.max()

        st.metric(
            label=f"All-Time Best ({selected_event})",
            value=f"{best_val:.1f}",
        )
        st.metric(
            label="Total Logs Saved", value=len(st.session_state.data)
        )

st.divider()
st.subheader("Complete History")
st.dataframe(st.session_state.data, use_container_width=True)
