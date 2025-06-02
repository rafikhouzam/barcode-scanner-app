# core/ui.py
import streamlit as st
import os
from core.handlers import handle_scan
from core.session import init_session_state, load_session, save_session, clear_session_file
import pandas as pd


def render_inputs(session):
    customer = st.text_input("Customer Name", value=session["customer_name"])
    meeting_desc = st.text_input("Meeting Description", key="meeting_description", value=session.get("meeting_description", ""))
    executive_options = ["", "Allen", "Becky", "Darshan", "Glory", "Heather", "Kathy", 
                         "Niraj Mehta", "Niraj Parekh", "Renato", "Rosanna", "Tahnee"]
    index = executive_options.index(session.get("executive_name", "")) if session.get("executive_name", "") in executive_options else 0
    executive = st.selectbox("Account Executive", executive_options, index=index)
    session["customer_name"] = customer
    session["meeting_description"] = meeting_desc
    session["executive_name"] = executive
    
    return customer, meeting_desc, executive

def render_comment_input():
    return st.text_input("Comment (Optional)", key=st.session_state["comment_key"])

def render_barcode_input(on_change=None):
    return st.text_input(
        "💎 Scan Barcode",
        key="barcode_input",
        placeholder="Waiting for scan…",
        on_change=on_change
    )

def render_barcode_feedback_old(barcode, lookup_df):
    if not barcode.strip():
        return

    bc = barcode.strip()
    if bc in lookup_df.index:
        row = lookup_df.loc[bc]
        st.success("✅ Tag Found!")
        st.markdown(f"**Style Code:** {row['style_cd']}")
        st.markdown(f"**Description:** {row['style_description']}")
        st.markdown(f"**Category:** {row['style_category']}")
    else:
        st.error("❌ Tag not found. Please check and scan again.")

def render_barcode_feedback():
    feedback = st.session_state.get("scan_feedback")
    if feedback:
        level, msg = feedback
        if level == "error":
            st.error(msg)
        elif level == "warn":
            st.warning(msg)
        elif level == "success":
            st.success(msg)
        st.session_state["scan_feedback"] = None


def render_scanned_items(session):
    import streamlit as st
    from collections import Counter

    st.markdown("## 📋 Scanned Items")

    scanned = session.get("scanned_items", [])
    total = len(scanned)
    st.markdown(f"**Total Scanned:** {total}")

    # 🔢 Scan count by category
    categories = [item.get("category", "UNKNOWN") for item in scanned]
    cat_counts = Counter(categories)

    # Render summary like: RING: 4 | BRACELET: 2
    if cat_counts:
        summary = " | ".join([f"`{cat}: {count}`" for cat, count in cat_counts.items()])
        st.markdown(f"**By Category:** {summary}")
    if session["scanned_items"]:
        # Column titles
        col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 3, 2, 4, 1])
        col1.markdown("**Barcode**")
        col2.markdown("**Style Code**")
        col3.markdown("**Description**")
        col4.markdown("**Category**")
        col5.markdown("**Comment**")

        for i, item in enumerate(session["scanned_items"]):
            col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 3, 2, 4, 1])
            col1.markdown(f"**{item['barcode']}**")
            col2.markdown(item["style_cd"])
            col3.markdown(item["description"])
            col4.markdown(item["category"])
            col5.markdown(item["comment"] or "No comment")
            if col6.button("\u274c", key=f"remove_{i}"):
                session["scanned_items"].pop(i)
                from core.session import save_session
                save_session(session)
                st.rerun()
        
        # Handle initial clear request
        # Step 1: Only show "Clear All Scans" if not already confirming
        if not st.session_state.get("confirm_clear", False):
            if st.button("🚫 Clear All Scans"):
                st.session_state["confirm_clear"] = True
                st.rerun()

        # Step 2: Show confirmation UI
        if st.session_state.get("confirm_clear", False):
            st.warning("Are you sure you want to clear all scanned items?")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Yes, Clear"):
                    session["scanned_items"] = []
                    from core.session import save_session
                    save_session(session)
                    st.session_state["confirm_clear"] = False
                    st.success("Scanned items cleared.")
                    st.rerun()

            with col2:
                if st.button("❌ Cancel"):
                    st.session_state["confirm_clear"] = False
                    st.rerun()

    else:
        st.info("No items scanned yet.")

def render_export_preview(session, export_dir="data"):
    """
    Renders a preview of the most recent export and download button.

    Args:
        session (dict): session state or your custom session object
        export_dir (str): folder where CSV files are saved
    """
    if "last_export" in session and "last_filename" in session:
            filepath = os.path.join(export_dir, session["last_filename"])
            
            # Always show download
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    st.download_button("📥 Download CSV", f, file_name=session["last_filename"], mime="text/csv")

            # Preview only if flag is set
            if session.get("show_export_preview"):
                with st.expander("📄 Preview Export", expanded=False):
                    df_preview = pd.DataFrame(session["last_export"])
                    st.dataframe(df_preview.head(10))
                session["show_export_preview"] = False  # auto-clear after first render

