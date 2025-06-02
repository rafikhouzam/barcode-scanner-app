#core/exporter.py
import pandas as pd, os
from datetime import datetime
import streamlit as st
import re
from core.session import clear_session_file

def export_to_csv(session):
    df = pd.DataFrame(session["scanned_items"])
    df["meeting_description"] = session.get("meeting_description", "")
    df["customer"] = session.get("customer_name", "")
    df["executive"] = session.get("executive_name", "")

    def sanitize_filename(s):
        return re.sub(r"[^\w\-]", "_", s.strip())

    safe_customer = sanitize_filename(session["customer_name"])
    safe_exec = sanitize_filename(session["executive_name"])
    safe_meeting = sanitize_filename(session.get("meeting_description", ""))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{safe_customer}_{safe_meeting}_{safe_exec}_{ts}.csv"
    filepath = os.path.join("data", filename)

    # Save CSV
    df.to_csv(filepath, index=False)

    # Store preview info for UI
    session["customer_name"] = ""
    session["meeting_description"] = ""
    session["last_export"] = df.to_dict(orient="records") # make it json serializable
    session["last_filename"] = filename
    session["show_export_preview"] = True  # one-time flag

    # Clear session
    clear_session_file()
    session["scanned_items"] = []
    st.session_state.confirmed_resume = False
