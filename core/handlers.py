import streamlit as st
from core.lookup import lookup_barcode

def handle_scan(session, lookup_df):
    bc = st.session_state.get("barcode_input", "").strip()

    comment_key = st.session_state.get("comment_key", "comment_input")
    comment = st.session_state.get(comment_key, "").strip()

    if not bc:
        return

    item = lookup_barcode(bc, lookup_df, comment)
    if item is None:
        st.session_state["scan_feedback"] = ("error", f"❌ Barcode '{bc}' not found.")
        st.session_state["clear_barcode"] = True
        return

    is_duplicate = any(i["barcode"] == bc for i in session["scanned_items"])
    if is_duplicate:
        st.session_state["scan_feedback"] = ("warn", "⚠️ Already scanned.")
        st.session_state["clear_barcode"] = True
        return

    item["customer"] = session["customer_name"]
    item["executive"] = session["executive_name"]
    session["scanned_items"].append(item)

    from core.session import save_session
    save_session(session)

    st.session_state["scan_feedback"] = (
        "success",
        f"✅ Added {item['style_cd']} — {item['description']}"
    )
    st.session_state["last_scanned"] = bc
    st.session_state["clear_barcode"] = True
    st.session_state["clear_comment"] = True

