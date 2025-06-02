# core/ui.py
import streamlit as st
from core.handlers import handle_scan


def render_inputs(session):
    customer = st.text_input("Customer Name", value=session["customer_name"])
    meeting_desc = st.text_input("Meeting Description", key="meeting_description", value=session.get("meeting_description", ""))
    executive_options = ["", "Becky", "Darshan", "Glory", "Heather", "Kathy", 
                         "Niraj Mehta", "Niraj Parekh", "Renato", "Rosanna", "Tahnee"]
    index = executive_options.index(session.get("executive_name", "")) if session.get("executive_name", "") in executive_options else 0
    executive = st.selectbox("Account Executive", executive_options, index=index)
    session["customer_name"] = customer
    session["executive_name"] = executive

    if st.session_state.get("clear_barcode", False):
        st.session_state["barcode_input"] = ""
        st.session_state["clear_barcode"] = False

    return customer, meeting_desc, executive

def render_comment_input():
    return st.text_input("Comment (optional)", key="comment_input")

def render_barcode_input(on_change=None):
    return st.text_input(
        "💎 Scan Barcode",
        key="barcode_input",
        placeholder="Waiting for scan…",
        on_change=on_change
    )

def render_comment_input():
    return st.text_input("Comment (optional)", key="comment_input")

def render_barcode_feedback(barcode, lookup_df):
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

def render_scanned_items(session):
    import streamlit as st
    st.markdown("## 📋 Scanned Items")
    if session["scanned_items"]:
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
        if st.button("🚫 Clear All Scans"):
            st.session_state["confirm_clear"] = True

        # Step 2: Show confirmation UI
        if st.session_state.get("confirm_clear"):
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


    else:
        st.info("No items scanned yet.")
