"""
FinTrack — Personal Finance Tracker
Entry point. Initializes DB, renders sidebar, routes to pages.
Run: streamlit run app.py
"""
import streamlit as st
from datetime import date

# ── Must be first Streamlit call ──────────────────────────────────────────────
st.set_page_config(
    page_title="FinTrack",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Init DB & inject CSS ───────────────────────────────────────────────────────
from utils.db import init_db
from utils.ui import CSS
init_db()
st.markdown(CSS, unsafe_allow_html=True)

# ── Import pages ───────────────────────────────────────────────────────────────
from modules.dashboard      import render as dashboard
from modules.add_transaction import render as add_transaction
from modules.budget          import render as budget
from modules.goals           import render as goals
from modules.split           import render as split
from modules.ai_assistant    import render as ai_assistant

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.6rem 1.4rem 1.2rem;border-bottom:1px solid rgba(255,255,255,.05);">
      <div style="display:flex;align-items:center;gap:11px;margin-bottom:4px;">
        <div style="width:36px;height:36px;
                    background:linear-gradient(135deg,#00e5a0,#4f8ef7);
                    border-radius:11px;display:flex;align-items:center;justify-content:center;
                    font-size:1rem;box-shadow:0 4px 14px rgba(0,229,160,.28);">💎</div>
        <div>
          <div style="font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:800;
                      background:linear-gradient(135deg,#00e5a0,#4f8ef7);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            FinTrack
          </div>
          <div style="font-size:.6rem;color:#4a5270;font-weight:600;letter-spacing:.06em;">
            PERSONAL FINANCE
          </div>
        </div>
      </div>
    </div>
    <div style="padding:.8rem .4rem .3rem;font-size:.62rem;font-weight:700;
                letter-spacing:.14em;color:#4a5270;text-transform:uppercase;padding-left:1.3rem;">
      Main Menu
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "📊  Dashboard",
        "➕  Add Transaction",
        "💰  Monthly Budget",
        "🎯  Savings Goals",
        "👥  Split Expenses",
        "🤖  AI Assistant",
    ], label_visibility="collapsed")

    st.markdown(f"""
    <div style="margin:.8rem .7rem 0;background:linear-gradient(135deg,
                rgba(0,229,160,.07),rgba(79,142,247,.05));
                border:1px solid rgba(0,229,160,.14);border-radius:11px;padding:.8rem 1rem;">
      <div style="font-size:.6rem;color:#4a5270;font-weight:700;
                  letter-spacing:.1em;text-transform:uppercase;margin-bottom:3px;">Today</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:.76rem;color:#8892b0;">
        {date.today().strftime("%d %b %Y")}
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Route ─────────────────────────────────────────────────────────────────────
p = page.split("  ")[1]

if   p == "Dashboard":       dashboard()
elif p == "Add Transaction":  add_transaction()
elif p == "Monthly Budget":   budget()
elif p == "Savings Goals":    goals()
elif p == "Split Expenses":   split()
elif p == "AI Assistant":     ai_assistant()
