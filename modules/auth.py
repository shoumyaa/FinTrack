"""Auth page — Login and Signup with warm obsidian design."""
import streamlit as st
from utils.db import create_user, login_user

def render():
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem 0 1.8rem;">
          <div style="display:inline-flex;align-items:center;justify-content:center;
                      width:54px;height:54px;
                      background:linear-gradient(135deg,#d4a84b,#b8860b);
                      border-radius:14px;font-size:1.4rem;
                      box-shadow:0 8px 28px rgba(212,168,75,0.32);
                      margin-bottom:1rem;">💎</div>
          <div style="font-family:'DM Serif Display',serif;font-size:1.8rem;
                      font-weight:400;color:#f5f0eb;letter-spacing:-.02em;">FinTrack</div>
          <div style="font-size:.72rem;color:#57534e;margin-top:.25rem;
                      font-family:'DM Mono',monospace;letter-spacing:.1em;
                      text-transform:uppercase;">Personal Finance</div>
        </div>
        """, unsafe_allow_html=True)

        tab_in, tab_up = st.tabs(["Sign In", "Create Account"])

        with tab_in:
            st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="your username")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                sub = st.form_submit_button("Sign In →", use_container_width=True)
            if sub:
                if not username or not password:
                    st.error("Please fill in all fields.")
                else:
                    user = login_user(username, password)
                    if user:
                        st.session_state["user"] = user
                        st.success(f"Welcome back, {user['username'].title()}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab_up:
            st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
            with st.form("signup_form"):
                new_user = st.text_input("Username", placeholder="choose a username")
                new_pass = st.text_input("Password", type="password", placeholder="min 6 characters")
                conf_pass= st.text_input("Confirm Password", type="password", placeholder="repeat password")
                sub2 = st.form_submit_button("Create Account →", use_container_width=True)
            if sub2:
                if not new_user or not new_pass or not conf_pass:
                    st.error("Please fill in all fields.")
                elif len(new_user.strip()) < 3:
                    st.error("Username must be at least 3 characters.")
                elif len(new_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_pass != conf_pass:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = create_user(new_user, new_pass)
                    if ok: st.success("Account created! Sign in above.")
                    else:  st.error(msg)

        st.markdown("""
        <div style="text-align:center;padding:1.4rem 0 0;
                    font-family:'DM Mono',monospace;font-size:.66rem;
                    color:#3d3a37;letter-spacing:.04em;">
          Your data is stored locally & securely.
        </div>
        """, unsafe_allow_html=True)
