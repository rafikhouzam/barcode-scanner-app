import streamlit as st
from core.lookup import lookup_barcode
from core.session import save_session

def handle_scan(session, lookup_df):
    bc = st.session_state.get("barcode_input", "").strip()
    comment = st.session_state.get("comment_input", "")

    if not bc or bc == st.session_state.get("last_scanned"):
        return

    item = lookup_barcode(bc, lookup_df, comment)
    if item is None:
        st.error(f"❌ Barcode '{bc}' not found.")
        st.session_state["clear_barcode"] = True
        return

    is_duplicate = any(i["barcode"] == bc for i in session["scanned_items"])
    if is_duplicate:
        st.warning("⚠️ Already scanned.")
        st.session_state["clear_barcode"] = True
        return

    item["customer"] = session["customer_name"]
    item["executive"] = session["executive_name"]
    session["scanned_items"].append(item)

    from core.session import save_session
    save_session(session)

    st.success(f"✅ Added {item['style_cd']} — {item['description']}")
    st.session_state["last_scanned"] = bc
    st.session_state["clear_barcode"] = True
    st.session_state["clear_comment"] = True
