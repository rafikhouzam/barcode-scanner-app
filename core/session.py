# core/session.py
def init_session_state():
    import streamlit as st, os, json
    if "initial_load" not in st.session_state:
        st.session_state.initial_load = True
    if st.session_state.get("confirmed_resume") and st.session_state.initial_load:
        st.session_state.initial_load = False
    if "session" not in st.session_state:
        st.session_state.session = load_session()

def load_session():
    import os, json
    if os.path.exists("temp_session.json"):
        with open("temp_session.json", "r") as f:
            return json.load(f)
    return {"customer_name": "", "executive_name": "", "scanned_items": []}

def save_session(state):
    import json
    with open("temp_session.json", "w") as f:
        json.dump(state, f)

def clear_session_file():
    import os
    if os.path.exists("temp_session.json"):
        os.remove("temp_session.json")