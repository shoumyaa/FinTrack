"""FinTrack — entry point. Run: streamlit run app.py"""
import streamlit as st
from datetime import date

st.set_page_config(page_title="FinTrack", page_icon="💎", layout="wide",
                   initial_sidebar_state="expanded")

from utils.db import init_db
from utils.ui import CSS
init_db()
st.markdown(CSS, unsafe_allow_html=True)

from modules.auth            import render as auth_page
from modules.dashboard       import render as dashboard
from modules.add_transaction import render as add_transaction
from modules.budget          import render as budget
from modules.goals           import render as goals
from modules.split           import render as split
from modules.ai_assistant    import render as ai_assistant

# ── Auth gate ──────────────────────────────────────────────────────────────────
if "user" not in st.session_state:
    auth_page()
    st.stop()

user    = st.session_state["user"]
user_id = user["id"]
uname   = user["username"].title()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown(f"""
    <div style="padding:1.5rem 1.2rem 1rem;border-bottom:1px solid rgba(255,255,255,.05);">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:34px;height:34px;
                    background:linear-gradient(135deg,#d4a84b,#b8860b);
                    border-radius:10px;display:flex;align-items:center;
                    justify-content:center;font-size:.95rem;
                    box-shadow:0 4px 14px rgba(212,168,75,.28);flex-shrink:0;">💎</div>
        <div>
          <div style="font-family:'DM Serif Display',serif;font-size:1.15rem;
                      font-weight:400;color:#f5f0eb;letter-spacing:-.02em;">FinTrack</div>
          <div style="font-family:'DM Mono',monospace;font-size:.58rem;
                      color:#57534e;letter-spacing:.08em;text-transform:uppercase;">
            Personal Finance
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # User pill
    st.markdown(f"""
    <div style="padding:.8rem .9rem .3rem;">
      <div style="display:flex;align-items:center;gap:8px;
                  background:rgba(212,168,75,.06);
                  border:1px solid rgba(212,168,75,.18);
                  border-radius:9px;padding:.6rem .85rem;">
        <div style="width:26px;height:26px;border-radius:50%;
                    background:linear-gradient(135deg,#d4a84b,#b8860b);
                    display:flex;align-items:center;justify-content:center;
                    font-family:'DM Serif Display',serif;
                    font-size:.82rem;font-weight:400;color:#0c0a09;flex-shrink:0;">
          {uname[0]}
        </div>
        <div>
          <div style="font-size:.8rem;font-weight:500;color:#f5f0eb;">{uname}</div>
          <div style="font-family:'DM Mono',monospace;font-size:.6rem;color:#57534e;">signed in</div>
        </div>
      </div>
    </div>
    <div style="padding:.5rem .5rem .2rem 1rem;
                font-family:'DM Mono',monospace;font-size:.61rem;
                letter-spacing:.14em;color:#3d3a37;text-transform:uppercase;">
      Navigation
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("nav", [
        "📊  Dashboard",
        "➕  Add Transaction",
        "💰  Monthly Budget",
        "🎯  Savings Goals",
        "👥  Split Expenses",
        "🤖  AI Assistant",
    ], label_visibility="collapsed")

    # Date + logout
    st.markdown(f"""
    <div style="margin:.6rem .7rem 0;
                background:rgba(255,255,255,.02);
                border:1px solid rgba(255,255,255,.05);
                border-radius:9px;padding:.65rem .9rem;">
      <div style="font-family:'DM Mono',monospace;font-size:.61rem;
                  color:#3d3a37;text-transform:uppercase;letter-spacing:.1em;margin-bottom:2px;">
        Today
      </div>
      <div style="font-size:.78rem;color:#9ca3af;">
        {date.today().strftime("%d %B %Y")}
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪  Sign Out", use_container_width=True, type="secondary"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ── Route ──────────────────────────────────────────────────────────────────────
p = page.split("  ")[1]
if   p == "Dashboard":       dashboard(user_id)
elif p == "Add Transaction":  add_transaction(user_id)
elif p == "Monthly Budget":   budget(user_id)
elif p == "Savings Goals":    goals(user_id)
elif p == "Split Expenses":   split(user_id)
elif p == "AI Assistant":     ai_assistant(user_id)
