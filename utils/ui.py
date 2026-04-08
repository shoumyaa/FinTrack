"""
Shared UI — Dark & Light theme support.
Theme is read from st.session_state["theme"] — "dark" or "light"
"""
import streamlit as st

EXP_CATS  = ["Food","Rent","Bills","Transport","Shopping","Entertainment","Health","Education","Other"]
INC_CATS  = ["Salary","Freelance","Investment","Gift","Bonus","Other"]
GOAL_ICONS = ["🏠","🚗","✈️","💻","📱","💍","🎓","🏋️","🌴","💰","🎯","🛍️"]

CAT_COLOR = {
    "Food":"#f97316","Rent":"#6366f1","Bills":"#eab308",
    "Transport":"#8b5cf6","Shopping":"#ec4899","Entertainment":"#10b981",
    "Health":"#3b82f6","Education":"#f59e0b","Other":"#6b7280",
    "Salary":"#22c55e","Freelance":"#22c55e","Investment":"#6366f1",
    "Gift":"#eab308","Bonus":"#ec4899",
}

def inr(v):  return f"₹{v:,.0f}"
def inr2(v): return f"₹{v:,.2f}"

def is_dark():
    return st.session_state.get("theme","dark") == "dark"

def get_chart():
    dark = is_dark()
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif",
                  color="#9ca3af" if dark else "#374151", size=11),
        margin=dict(t=20, b=30, l=10, r=10),
        hoverlabel=dict(
            bgcolor="#1c1917" if dark else "#ffffff",
            bordercolor="#292524" if dark else "#e5e7eb",
            font=dict(family="DM Sans, sans-serif",
                      color="#f5f0eb" if dark else "#111827", size=12)
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)" if dark else "rgba(0,0,0,0.06)",
            showline=False,
            tickfont=dict(color="#57534e" if dark else "#6b7280"),
            zeroline=False
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)" if dark else "rgba(0,0,0,0.06)",
            showline=False,
            tickfont=dict(color="#57534e" if dark else "#6b7280"),
            zeroline=False
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9ca3af" if dark else "#374151", size=11),
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )

# Keep CHART as a property for backwards compat — modules that use CHART directly
CHART = get_chart()

def chart_card(title, subtitle=""):
    st.markdown(
        f'<div class="chart-card">'
        f'<div class="chart-title">{title}</div>'
        f'<div class="chart-sub">{subtitle}</div>',
        unsafe_allow_html=True
    )

def div_label(text):
    st.markdown(f"""
    <div class="section-label">
      <div class="line"></div><span>{text}</span><div class="line"></div>
    </div>""", unsafe_allow_html=True)

def page_hero(title, subtitle, icon=""):
    from datetime import date
    st.markdown(f"""
    <div class="page-hero">
      <div class="hero-inner">
        <div class="hero-tag">{date.today().strftime("%A, %d %B %Y")}</div>
        <h1 class="hero-title">{icon} {title}</h1>
        <p class="hero-sub">{subtitle}</p>
      </div>
      <div class="hero-deco"></div>
    </div>""", unsafe_allow_html=True)

def get_css():
    dark = is_dark()

    # ── Token values per theme ──────────────────────────────────────────────
    if dark:
        bg    = "#0c0a09"
        s0    = "#111110"
        s1    = "#1c1917"
        s2    = "#292524"
        s3    = "#3d3a37"
        s4    = "#57534e"
        t1    = "#f5f0eb"
        t2    = "#d6cfc8"
        t3    = "#9ca3af"
        t4    = "#57534e"
        b1    = "rgba(255,255,255,0.06)"
        b2    = "rgba(255,255,255,0.10)"
        b3    = "rgba(212,168,75,0.22)"
        gold  = "#d4a84b"
        goldd = "#b8860b"
        goldg = "rgba(212,168,75,0.12)"
        golds = "rgba(212,168,75,0.06)"
        app_bg = f"""
            radial-gradient(ellipse 65% 38% at 12% 0%,rgba(212,168,75,0.055) 0%,transparent 55%),
            radial-gradient(ellipse 45% 32% at 88% 100%,rgba(99,102,241,0.04) 0%,transparent 55%),
            {bg}"""
        sidebar_bg = s0
        hero_deco  = "rgba(212,168,75,0.09)"
        inp_bg     = s2
        form_bg    = s1
        scroll_thumb = s3
        tab_list_bg  = s1
        tab_active_bg= s3
        tab_text     = t4
        tab_active_text = gold
        expander_bg  = s1
        btn_shadow   = "rgba(212,168,75,.2)"
        btn_hover_shadow = "rgba(212,168,75,.32)"
        hover_bg     = s2
        alert_warn_bg= "rgba(245,158,11,.06)"
        alert_good_bg= "rgba(34,197,94,.06)"
        alert_info_bg= "rgba(99,102,241,.06)"
        alert_bad_bg = "rgba(239,68,68,.06)"
        msg_bot_bg   = s2
        tx_bg        = s1
        kpi_bg       = s1
        budget_bg    = s1
        goal_bg      = s1
        owe_bg       = s2
    else:
        bg    = "#f8f7f4"
        s0    = "#ffffff"
        s1    = "#ffffff"
        s2    = "#f3f0eb"
        s3    = "#e8e3db"
        s4    = "#9ca3af"
        t1    = "#1c1917"
        t2    = "#3d3a37"
        t3    = "#57534e"
        t4    = "#9ca3af"
        b1    = "rgba(0,0,0,0.07)"
        b2    = "rgba(0,0,0,0.12)"
        b3    = "rgba(180,120,30,0.25)"
        gold  = "#b8860b"
        goldd = "#8b6508"
        goldg = "rgba(184,134,11,0.10)"
        golds = "rgba(184,134,11,0.05)"
        app_bg = f"""
            radial-gradient(ellipse 65% 38% at 12% 0%,rgba(212,168,75,0.07) 0%,transparent 55%),
            radial-gradient(ellipse 45% 32% at 88% 100%,rgba(99,102,241,0.04) 0%,transparent 55%),
            {bg}"""
        sidebar_bg = "#faf9f6"
        hero_deco  = "rgba(212,168,75,0.08)"
        inp_bg     = "#f3f0eb"
        form_bg    = "#ffffff"
        scroll_thumb = "#d1c9bf"
        tab_list_bg  = "#f3f0eb"
        tab_active_bg= "#ffffff"
        tab_text     = "#9ca3af"
        tab_active_text = gold
        expander_bg  = "#ffffff"
        btn_shadow   = "rgba(184,134,11,.18)"
        btn_hover_shadow = "rgba(184,134,11,.3)"
        hover_bg     = "#ede9e2"
        alert_warn_bg= "rgba(245,158,11,.07)"
        alert_good_bg= "rgba(34,197,94,.07)"
        alert_info_bg= "rgba(99,102,241,.07)"
        alert_bad_bg = "rgba(239,68,68,.07)"
        msg_bot_bg   = "#f3f0eb"
        tx_bg        = "#ffffff"
        kpi_bg       = "#ffffff"
        budget_bg    = "#ffffff"
        goal_bg      = "#ffffff"
        owe_bg       = "#f3f0eb"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Mono:wght@400;500&display=swap');

:root {{
  --bg:    {bg};
  --s0:    {s0};
  --s1:    {s1};
  --s2:    {s2};
  --s3:    {s3};
  --s4:    {s4};
  --gold:   {gold};
  --gold-d: {goldd};
  --gold-g: {goldg};
  --gold-s: {golds};
  --green:  #22c55e;
  --green-g:rgba(34,197,94,0.1);
  --red:    #ef4444;
  --red-g:  rgba(239,68,68,0.1);
  --blue:   #6366f1;
  --blue-g: rgba(99,102,241,0.1);
  --amber:  #f59e0b;
  --amber-g:rgba(245,158,11,0.1);
  --t1: {t1};
  --t2: {t2};
  --t3: {t3};
  --t4: {t4};
  --b1: {b1};
  --b2: {b2};
  --b3: {b3};
  --radius: 14px;
  --radius-sm: 9px;
}}

*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
html,body,[class*="css"],.stApp{{
  font-family:'DM Sans',sans-serif!important;
  background:var(--bg)!important;
  color:var(--t1)!important;
  -webkit-font-smoothing:antialiased;
}}
.stApp{{
  background:{app_bg}!important;
}}
#MainMenu,footer,.stDeployButton{{display:none!important;}}
::-webkit-scrollbar{{width:4px;height:4px;}}
::-webkit-scrollbar-track{{background:var(--s0);}}
::-webkit-scrollbar-thumb{{background:{scroll_thumb};border-radius:2px;}}

/* SIDEBAR */
section[data-testid="stSidebar"]{{background:{sidebar_bg}!important;border-right:1px solid var(--b1)!important;width:258px!important;}}
section[data-testid="stSidebar"]>div{{padding:0!important;}}
section[data-testid="stSidebar"] .stRadio>div{{gap:2px!important;flex-direction:column!important;}}
section[data-testid="stSidebar"] .stRadio label{{display:none!important;}}
section[data-testid="stSidebar"] .stRadio>div>label{{
  display:flex!important;align-items:center;gap:9px;
  padding:10px 14px!important;border-radius:var(--radius-sm)!important;
  margin:2px 7px!important;cursor:pointer;transition:all .14s ease;
  border:1px solid transparent!important;color:var(--t4)!important;
  font-size:.83rem!important;font-weight:500!important;
}}
section[data-testid="stSidebar"] .stRadio>div>label:hover{{background:var(--s2)!important;color:var(--t2)!important;}}
section[data-testid="stSidebar"] .stRadio input[type="radio"]{{display:none!important;}}
section[data-testid="stSidebar"] .stRadio>div>label:has(input:checked){{
  background:var(--gold-s)!important;border-color:var(--b3)!important;color:var(--gold)!important;
}}

/* HERO */
.page-hero{{
  position:relative;overflow:hidden;
  background:var(--s1);border:1px solid var(--b1);
  border-top:1px solid var(--b3);border-radius:var(--radius);
  padding:1.9rem 2.2rem;margin-bottom:1.5rem;
}}
.hero-inner{{position:relative;z-index:1;}}
.hero-deco{{
  position:absolute;top:-60px;right:-60px;
  width:220px;height:220px;border-radius:50%;
  background:radial-gradient(circle,{hero_deco} 0%,transparent 65%);
}}
.hero-tag{{
  display:inline-block;font-family:'DM Mono',monospace;
  font-size:.66rem;color:var(--gold);
  background:var(--gold-g);border:1px solid var(--b3);
  border-radius:20px;padding:3px 11px;
  margin-bottom:.65rem;letter-spacing:.06em;text-transform:uppercase;
}}
.hero-title{{
  font-family:'DM Serif Display',serif!important;
  font-size:2rem!important;font-weight:400!important;
  color:var(--t1)!important;line-height:1.1!important;
  letter-spacing:-.02em!important;margin-bottom:.3rem!important;
}}
.hero-sub{{color:var(--t4)!important;font-size:.86rem!important;font-weight:300!important;}}

/* KPI */
.kpi-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin-bottom:1.3rem;}}
.kpi-card{{
  position:relative;overflow:hidden;
  background:{kpi_bg};border:1px solid var(--b1);
  border-radius:var(--radius);padding:1.2rem 1.4rem;
  transition:transform .18s ease,box-shadow .18s ease;
}}
.kpi-card:hover{{transform:translateY(-2px);box-shadow:0 16px 40px rgba(0,0,0,.15);}}
.kpi-card.em{{border-bottom:2px solid var(--green);}}
.kpi-card.ro{{border-bottom:2px solid var(--red);}}
.kpi-card.sa{{border-bottom:2px solid var(--blue);}}
.kpi-card.am{{border-bottom:2px solid var(--amber);}}
.kpi-card.gd{{border-bottom:2px solid var(--gold);}}
.kpi-glow{{position:absolute;bottom:-30px;right:-30px;width:90px;height:90px;border-radius:50%;filter:blur(28px);opacity:.15;}}
.kpi-card.em .kpi-glow{{background:var(--green);}}
.kpi-card.ro .kpi-glow{{background:var(--red);}}
.kpi-card.sa .kpi-glow{{background:var(--blue);}}
.kpi-card.am .kpi-glow{{background:var(--amber);}}
.kpi-card.gd .kpi-glow{{background:var(--gold);}}
.kpi-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.8rem;}}
.kpi-icon-wrap{{width:34px;height:34px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.95rem;border:1px solid var(--b2);}}
.kpi-card.em .kpi-icon-wrap{{background:var(--green-g);}}
.kpi-card.ro .kpi-icon-wrap{{background:var(--red-g);}}
.kpi-card.sa .kpi-icon-wrap{{background:var(--blue-g);}}
.kpi-card.am .kpi-icon-wrap{{background:var(--amber-g);}}
.kpi-card.gd .kpi-icon-wrap{{background:var(--gold-g);}}
.kpi-badge{{font-family:'DM Mono',monospace;font-size:.61rem;padding:2px 7px;border-radius:20px;font-weight:500;}}
.kpi-badge.up{{background:var(--green-g);color:var(--green);border:1px solid rgba(34,197,94,.2);}}
.kpi-badge.dn{{background:var(--red-g);color:var(--red);border:1px solid rgba(239,68,68,.2);}}
.kpi-badge.nt{{background:var(--blue-g);color:var(--blue);border:1px solid rgba(99,102,241,.2);}}
.kpi-badge.gd{{background:var(--gold-g);color:var(--gold);border:1px solid var(--b3);}}
.kpi-label{{font-size:.66rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--t4);margin-bottom:.28rem;}}
.kpi-value{{font-family:'DM Serif Display',serif;font-size:1.85rem;line-height:1;letter-spacing:-.02em;margin-bottom:.45rem;}}
.kpi-card.em .kpi-value{{color:var(--green);}}
.kpi-card.ro .kpi-value{{color:var(--red);}}
.kpi-card.sa .kpi-value{{color:#6366f1;}}
.kpi-card.am .kpi-value{{color:var(--amber);}}
.kpi-card.gd .kpi-value{{color:var(--gold);}}

/* SECTION LABEL */
.section-label{{display:flex;align-items:center;gap:12px;margin:1.5rem 0 .9rem;}}
.section-label .line{{flex:1;height:1px;background:var(--b1);}}
.section-label span{{font-family:'DM Mono',monospace;font-size:.63rem;font-weight:500;letter-spacing:.15em;text-transform:uppercase;color:var(--t4);white-space:nowrap;}}

/* CHART CARD */
.chart-card{{background:var(--s1);border:1px solid var(--b1);border-radius:var(--radius);padding:1.2rem 1.3rem;margin-bottom:.75rem;}}
.chart-title{{font-family:'DM Serif Display',serif;font-size:.98rem;font-weight:400;color:var(--t2);margin-bottom:.12rem;}}
.chart-sub{{font-size:.71rem;color:var(--t4);margin-bottom:.85rem;}}

/* TX ROWS */
.tx-row{{display:flex;align-items:center;gap:.8rem;padding:.7rem .95rem;border-radius:var(--radius-sm);border:1px solid var(--b1);background:{tx_bg};margin-bottom:.32rem;transition:background .11s,border-color .11s;}}
.tx-row:hover{{background:{hover_bg};border-color:var(--b2);}}
.tx-dot{{width:7px;height:7px;border-radius:50%;flex-shrink:0;}}
.tx-cat{{font-size:.78rem;font-weight:600;color:var(--t2);min-width:88px;}}
.tx-desc{{font-size:.73rem;color:var(--t4);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
.tx-date{{font-family:'DM Mono',monospace;font-size:.67rem;color:var(--t4);min-width:76px;text-align:right;}}
.tx-amount{{font-family:'DM Mono',monospace;font-size:.84rem;font-weight:500;min-width:105px;text-align:right;}}
.tx-amount.inc{{color:var(--green);}}
.tx-amount.exp{{color:var(--red);}}

/* ALERTS */
.alert-card{{display:flex;align-items:flex-start;gap:.8rem;padding:.8rem .95rem;border-radius:var(--radius-sm);border:1px solid;margin-bottom:.42rem;font-size:.8rem;line-height:1.55;}}
.alert-card.warn{{background:{alert_warn_bg};border-color:rgba(245,158,11,.22);color:var(--t2);}}
.alert-card.good{{background:{alert_good_bg};border-color:rgba(34,197,94,.2);color:var(--t2);}}
.alert-card.info{{background:{alert_info_bg};border-color:rgba(99,102,241,.2);color:var(--t2);}}
.alert-card.bad {{background:{alert_bad_bg};border-color:rgba(239,68,68,.2);color:var(--t2);}}
.alert-icon{{font-size:.95rem;flex-shrink:0;margin-top:1px;}}
.alert-text b{{color:var(--t1);}}

/* BUDGET */
.budget-card{{background:{budget_bg};border:1px solid var(--b1);border-radius:var(--radius);padding:1rem 1.2rem;margin-bottom:.55rem;transition:border-color .14s;}}
.budget-card:hover{{border-color:var(--b2);}}
.budget-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.6rem;}}
.budget-cat{{font-family:'DM Serif Display',serif;font-size:.9rem;font-weight:400;color:var(--t2);}}
.budget-actual{{font-family:'DM Mono',monospace;font-size:.83rem;font-weight:500;}}
.budget-limit{{font-family:'DM Mono',monospace;font-size:.66rem;color:var(--t4);}}
.budget-track{{height:4px;background:var(--s3);border-radius:2px;overflow:hidden;margin-bottom:.48rem;}}
.budget-fill{{height:100%;border-radius:2px;transition:width .6s cubic-bezier(.4,0,.2,1);}}
.budget-footer{{display:flex;justify-content:space-between;font-size:.68rem;color:var(--t4);}}

/* GOALS */
.goal-card{{background:{goal_bg};border:1px solid var(--b1);border-radius:var(--radius);padding:1.1rem 1.3rem;margin-bottom:.7rem;transition:border-color .14s,transform .14s;}}
.goal-card:hover{{border-color:var(--b3);transform:translateY(-1px);}}
.goal-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.8rem;}}
.goal-icon{{font-size:1.6rem;}}
.goal-name{{font-family:'DM Serif Display',serif;font-size:.98rem;font-weight:400;color:var(--t1);}}
.goal-target{{font-family:'DM Mono',monospace;font-size:.7rem;color:var(--t4);margin-top:2px;}}
.goal-pct{{font-family:'DM Serif Display',serif;font-size:1.45rem;font-weight:400;color:var(--gold);}}
.goal-track{{height:5px;background:var(--s3);border-radius:3px;overflow:hidden;margin-bottom:.52rem;}}
.goal-fill{{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--gold),#f59e0b);transition:width .7s cubic-bezier(.4,0,.2,1);}}
.goal-footer{{display:flex;justify-content:space-between;font-size:.69rem;color:var(--t4);}}

/* SPLIT */
.owe-row{{display:flex;align-items:center;justify-content:space-between;padding:.68rem .95rem;border-radius:var(--radius-sm);background:{owe_bg};border:1px solid var(--b1);margin-bottom:.38rem;}}
.owe-names{{font-size:.81rem;color:var(--t2);font-weight:500;}}
.owe-amount{{font-family:'DM Mono',monospace;font-size:.84rem;font-weight:500;}}

/* CHAT */
.chat-wrap{{display:flex;flex-direction:column;gap:.85rem;padding:.5rem 0 1rem;}}
.msg-row{{display:flex;gap:9px;align-items:flex-start;}}
.msg-row.user{{flex-direction:row-reverse;}}
.msg-avatar{{width:29px;height:29px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.78rem;flex-shrink:0;}}
.msg-avatar.bot{{background:linear-gradient(135deg,var(--gold),#f59e0b);}}
.msg-avatar.user{{background:linear-gradient(135deg,#6366f1,#818cf8);}}
.msg-bubble{{max-width:72%;padding:.75rem .95rem;border-radius:11px;font-size:.84rem;line-height:1.65;}}
.msg-bubble.bot{{background:{msg_bot_bg};border:1px solid var(--b1);color:var(--t2);border-bottom-left-radius:3px;}}
.msg-bubble.user{{background:linear-gradient(135deg,var(--gold-g),rgba(245,158,11,.08));border:1px solid var(--b3);color:var(--t1);border-bottom-right-radius:3px;}}

/* FORMS */
div[data-testid="stForm"]{{background:{form_bg}!important;border:1px solid var(--b1)!important;border-radius:var(--radius)!important;padding:1.6rem!important;}}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stTextArea textarea,.stSelectbox>div>div{{background:{inp_bg}!important;border:1px solid var(--b2)!important;border-radius:var(--radius-sm)!important;color:var(--t1)!important;font-family:'DM Sans',sans-serif!important;font-size:.85rem!important;}}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus,.stTextArea textarea:focus{{border-color:var(--b3)!important;box-shadow:0 0 0 2px {goldg}!important;outline:none!important;}}
label[data-testid="stWidgetLabel"] p{{color:var(--t4)!important;font-size:.71rem!important;font-weight:600!important;letter-spacing:.08em!important;text-transform:uppercase!important;}}

/* BUTTONS */
.stButton>button{{background:linear-gradient(135deg,var(--gold),var(--gold-d))!important;color:{'#0c0a09' if dark else '#ffffff'}!important;border:none!important;border-radius:var(--radius-sm)!important;font-family:'DM Sans',sans-serif!important;font-weight:600!important;font-size:.83rem!important;padding:.58rem 1.5rem!important;transition:all .18s ease!important;box-shadow:0 4px 16px {btn_shadow}!important;letter-spacing:.02em!important;}}
.stButton>button:hover{{transform:translateY(-2px)!important;box-shadow:0 8px 26px {btn_hover_shadow}!important;}}
button[kind="secondary"]{{background:transparent!important;border:1px solid var(--red)!important;color:var(--red)!important;box-shadow:none!important;}}

/* FEEDBACK */
.stSuccess>div{{background:rgba(34,197,94,.08)!important;border:1px solid rgba(34,197,94,.25)!important;border-radius:var(--radius-sm)!important;color:var(--green)!important;}}
.stInfo>div{{background:rgba(99,102,241,.08)!important;border:1px solid rgba(99,102,241,.25)!important;border-radius:var(--radius-sm)!important;}}
.stError>div{{background:rgba(239,68,68,.08)!important;border:1px solid rgba(239,68,68,.25)!important;border-radius:var(--radius-sm)!important;}}
.stWarning>div{{background:rgba(245,158,11,.08)!important;border:1px solid rgba(245,158,11,.25)!important;border-radius:var(--radius-sm)!important;}}
div[data-testid="stExpander"]{{background:{expander_bg}!important;border:1px solid var(--b1)!important;border-radius:var(--radius)!important;}}

/* TABS */
.stTabs [data-baseweb="tab-list"]{{background:{tab_list_bg}!important;border-radius:var(--radius-sm)!important;border:1px solid var(--b1)!important;padding:3px!important;gap:2px!important;}}
.stTabs [data-baseweb="tab"]{{background:transparent!important;color:{tab_text}!important;border-radius:7px!important;font-family:'DM Sans',sans-serif!important;font-size:.81rem!important;font-weight:500!important;padding:6px 13px!important;border:none!important;transition:all .14s!important;}}
.stTabs [aria-selected="true"]{{background:{tab_active_bg}!important;color:{tab_active_text}!important;}}
.stTabs [data-baseweb="tab-highlight"]{{display:none!important;}}
.stTabs [data-baseweb="tab-border"]{{display:none!important;}}

h1,h2,h3,h4{{color:var(--t1)!important;}}
.stDataFrame{{border:1px solid var(--b1)!important;border-radius:var(--radius)!important;}}
</style>
"""
