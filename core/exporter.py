# core/exporter.py
def export_to_csv(session):
    import pandas as pd, os
    from datetime import datetime
    df = pd.DataFrame(session["scanned_items"])
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_customer = session["customer_name"].replace(" ", "_")
    safe_exec = session["executive_name"].replace(" ", "_")
    filename = f"{safe_customer}_{safe_exec}_{ts}.csv"
    filepath = os.path.join("data", filename)
    df.to_csv(filepath, index=False)
    from core.session import clear_session_file
    clear_session_file()
    session["scanned_items"] = []
    import streamlit as st
    with open(filepath, "rb") as f:
        st.download_button("📥 Download CSV", f, file_name=filename, mime="text/csv")
