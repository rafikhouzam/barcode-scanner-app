# app.py (clean version)
import streamlit as st
from core.logo import render_logo_and_caption
from core.lookup import load_lookup_df, lookup_barcode
from core.session import init_session_state, load_session, save_session, clear_session_file
from core.exporter import export_to_csv
from core.ui import render_scanned_items, render_inputs, render_barcode_feedback, render_comment_input, render_barcode_input
from core.handlers import handle_scan
import os
import pandas as pd

# === App Setup ===
init_session_state()
session = st.session_state.session
render_logo_and_caption()
os.makedirs("data", exist_ok=True)

# === Business Unit Selection and Lookup Load ===
business_unit = st.selectbox("Select Business Unit", ("", "Aneri Jewels", "EDB"))
try:
    lookup_df = load_lookup_df(business_unit)

    if lookup_df.empty:
        st.warning("Please select a Business Unit to begin scanning.")
        st.stop()
 
except Exception as e:
    st.error(f"❌ Failed to load barcode lookup file: {e}")
    st.stop()

if lookup_df.empty:
    st.warning("Please select a Business Unit to begin scanning.")
    st.stop()

# === Resume Prompt ===
if (
    st.session_state.initial_load
    and session["scanned_items"]
    and not st.session_state.get("confirmed_resume")
):
    st.warning("⚠️ Previous session detected.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Resume Previous Session"):
            st.session_state.confirmed_resume = True
            st.session_state.initial_load = False
            st.rerun()
    with col2:
        if st.button("Start New Session"):
            session = {"customer_name": "", "executive_name": "", "scanned_items": []}
            st.session_state.session = session
            clear_session_file()
            st.session_state.confirmed_resume = True
            st.session_state.initial_load = False
            st.rerun()
    st.stop()

# === Main UI ===
if st.session_state.get("clear_barcode"):
    st.session_state["barcode_input"] = ""
    st.session_state["clear_barcode"] = False

if st.session_state.get("clear_comment"):
    st.session_state["comment_input"] = ""
    st.session_state["clear_comment"] = False


# First input section
customer, meeting_desc, executive = render_inputs(session)

# Optional comment input below
comment = render_comment_input()

# === Barcode Scanning Logic ===

# Duplicate check
if st.session_state.get("clear_barcode"):
    st.session_state["barcode_input"] = ""
    st.session_state["clear_barcode"] = False

if st.session_state.get("clear_comment"):
    st.session_state["comment_input"] = ""
    st.session_state["clear_comment"] = False

# Wrap the handler so it can be passed to on_change without args
def scan_callback():
    handle_scan(session, lookup_df)

barcode = render_barcode_input(on_change=scan_callback)

# Immediately show feedback right under the barcode input
render_barcode_feedback(barcode, lookup_df)

# Step 2: Process scan if barcode is entered and it's different from last
if barcode.strip():
    if barcode != st.session_state.get("last_scanned"):

        item = lookup_barcode(barcode, lookup_df, comment=comment)

        if item:
            item["customer"] = session["customer_name"]
            item["executive"] = session["executive_name"]
            session["scanned_items"].append(item)

            save_session(session)

            st.session_state["last_scanned"] = barcode
            st.session_state["barcode_input"] = ""         # Clear scan box
            st.session_state["comment_input"] = ""         # Clear comment box

            st.success(f"✅ Added {item['style_cd']} — {item['description']}")

        else:
            st.error("❌ Tag not found. Please scan again.")


render_scanned_items(session)

# === Export ===
if session["scanned_items"] and st.button("📤 Finish & Export to CSV"):
    export_to_csv(session)
    st.success("✅ Export complete.")
