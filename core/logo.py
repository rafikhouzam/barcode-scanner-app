# core/logo.py

def render_logo_and_caption():
    import streamlit as st, base64
    with open("./img/aneriInveno_transparent.png", "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
        <div style='text-align: center; margin-top: -30px; margin-bottom: 20px;'>
            <img src="data:image/png;base64,{logo_base64}" style="max-height: 80px;" />
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; font-size: 0.9rem; color: grey; margin-top: -30px;'>
            Smart product lookup powered by barcode scanning
        </div>
    """, unsafe_allow_html=True)