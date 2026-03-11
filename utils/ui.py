"""
Shared UI constants, CSS, chart theme, and helper functions.
"""
import streamlit as st
import plotly.graph_objects as go

# ── Categories ─────────────────────────────────────────────────────────────────
EXP_CATS = ["Food","Rent","Bills","Transport","Shopping","Entertainment","Health","Education","Other"]
INC_CATS  = ["Salary","Freelance","Investment","Gift","Bonus","Other"]
GOAL_ICONS = ["🏠","🚗","✈️","💻","📱","💍","🎓","🏋️","🌴","💰","🎯","🛍️"]

CAT_COLOR = {
    "Food":"#ff6b6b","Rent":"#4f8ef7","Bills":"#ffb547",
    "Transport":"#a78bfa","Shopping":"#f472b6","Entertainment":"#34d399",
    "Health":"#60a5fa","Education":"#fb923c","Other":"#8892b0",
    "Salary":"#00e5a0","Freelance":"#00e5a0","Investment":"#4f8ef7",
    "Gift":"#ffb547","Bonus":"#f472b6",
}

# ── Formatters ─────────────────────────────────────────────────────────────────
def inr(v):  return f"₹{v:,.0f}"
def inr2(v): return f"₹{v:,.2f}"

# ── Chart base layout ──────────────────────────────────────────────────────────
CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#8892b0", size=11),
    margin=dict(t=20, b=30, l=10, r=10),
    hoverlabel=dict(bgcolor="#1c2135", bordercolor="#222843",
                    font=dict(family="Inter", color="#f0f4ff", size=12)),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False,
               tickfont=dict(color="#4a5270"), zeroline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showline=False,
               tickfont=dict(color="#4a5270"), zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8892b0", size=11),
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

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
      <span class="hero-date">{date.today().strftime("%A, %d %b %Y")}</span>
      <h1>{icon} {title}</h1>
      <p>{subtitle}</p>
    </div>""", unsafe_allow_html=True)

# ── CSS ────────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --black:#080a0f; --s0:#0c0e15; --s1:#111420; --s2:#161a28;
  --s3:#1c2135; --s4:#222843;
  --em:#00e5a0; --em-d:#00b37e; --em-g:rgba(0,229,160,0.12);
  --ro:#ff4d6d; --ro-d:#cc2d4a; --ro-g:rgba(255,77,109,0.12);
  --sa:#4f8ef7; --sa-d:#2d6ad4; --sa-g:rgba(79,142,247,0.12);
  --am:#ffb547; --vi:#a78bfa;
  --t1:#f0f4ff; --t2:#c8d0e8; --t3:#8892b0; --t4:#4a5270;
  --b1:rgba(255,255,255,0.06); --b2:rgba(255,255,255,0.10);
}

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"],.stApp{
  font-family:'Inter',sans-serif;
  background:var(--black)!important;
  color:var(--t1);-webkit-font-smoothing:antialiased;
}
.stApp{
  background:
    radial-gradient(ellipse 80% 50% at 20% -10%,rgba(0,229,160,0.06) 0%,transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 110%,rgba(79,142,247,0.05) 0%,transparent 60%),
    var(--black)!important;
}
#MainMenu,footer,.stDeployButton{display:none!important;visibility:hidden!important;}
/* ── Sidebar ── */
section[data-testid="stSidebar"]{
  background:var(--s0)!important;
  border-right:1px solid var(--b1)!important;
  width:256px!important;
}
section[data-testid="stSidebar"]>div{padding:0!important;}
section[data-testid="stSidebar"] .stRadio>div{gap:2px!important;flex-direction:column;}
section[data-testid="stSidebar"] .stRadio label{display:none!important;}
section[data-testid="stSidebar"] .stRadio>div>label{
  display:flex!important;align-items:center;gap:10px;
  padding:11px 18px!important;border-radius:10px!important;
  margin:2px 10px!important;cursor:pointer;transition:all .18s ease;
  border:1px solid transparent!important;color:var(--t3)!important;
  font-size:.86rem!important;font-weight:500!important;
}
section[data-testid="stSidebar"] .stRadio>div>label:hover{
  background:var(--s2)!important;color:var(--t1)!important;
  border-color:var(--b1)!important;
}
section[data-testid="stSidebar"] .stRadio input[type="radio"]{display:none!important;}
section[data-testid="stSidebar"] .stRadio>div>label:has(input:checked){
  background:linear-gradient(135deg,rgba(0,229,160,0.13),rgba(79,142,247,0.08))!important;
  border-color:rgba(0,229,160,0.28)!important;color:var(--em)!important;
}

/* ── Page hero ── */
.page-hero{
  background:linear-gradient(135deg,var(--s1),var(--s2));
  border:1px solid var(--b1);border-radius:20px;
  padding:1.8rem 2.2rem;margin-bottom:1.8rem;position:relative;overflow:hidden;
}
.page-hero::before{
  content:'';position:absolute;top:-50px;right:-50px;
  width:200px;height:200px;
  background:radial-gradient(circle,rgba(0,229,160,0.09) 0%,transparent 70%);
  border-radius:50%;
}
.page-hero h1{
  font-family:'Syne',sans-serif!important;font-size:1.8rem!important;
  font-weight:800!important;color:var(--t1)!important;
  letter-spacing:-.03em;line-height:1.1;margin-bottom:.3rem;
}
.page-hero p{color:var(--t3);font-size:.88rem;}
.hero-date{
  position:absolute;top:1.2rem;right:1.5rem;
  font-family:'JetBrains Mono',monospace;font-size:.7rem;color:var(--t4);
  background:var(--s3);padding:5px 12px;border-radius:20px;border:1px solid var(--b1);
}

/* ── KPI Cards ── */
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.9rem;margin-bottom:1.8rem;}
.kpi-card{
  background:var(--s1);border-radius:16px;padding:1.4rem 1.6rem;
  border:1px solid var(--b1);position:relative;overflow:hidden;
  transition:transform .2s ease,box-shadow .2s ease;
}
.kpi-card:hover{transform:translateY(-3px);box-shadow:0 20px 50px rgba(0,0,0,.4);}
.kpi-card.em{border-top:2px solid var(--em);}
.kpi-card.ro{border-top:2px solid var(--ro);}
.kpi-card.sa{border-top:2px solid var(--sa);}
.kpi-card.am{border-top:2px solid var(--am);}
.kpi-card.vi{border-top:2px solid var(--vi);}
.kpi-glow{position:absolute;top:-25px;right:-25px;width:90px;height:90px;border-radius:50%;filter:blur(25px);opacity:.35;}
.kpi-card.em .kpi-glow{background:var(--em);}
.kpi-card.ro .kpi-glow{background:var(--ro);}
.kpi-card.sa .kpi-glow{background:var(--sa);}
.kpi-card.am .kpi-glow{background:var(--am);}
.kpi-card.vi .kpi-glow{background:var(--vi);}
.kpi-icon{font-size:1.3rem;margin-bottom:.8rem;display:block;}
.kpi-label{font-size:.68rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--t4);margin-bottom:.4rem;}
.kpi-value{font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;line-height:1;letter-spacing:-.03em;margin-bottom:.5rem;}
.kpi-card.em .kpi-value{color:var(--em);}
.kpi-card.ro .kpi-value{color:var(--ro);}
.kpi-card.sa .kpi-value{color:var(--sa);}
.kpi-card.am .kpi-value{color:var(--am);}
.kpi-card.vi .kpi-value{color:var(--vi);}
.kpi-badge{display:inline-flex;align-items:center;gap:3px;font-size:.68rem;font-weight:600;padding:2px 8px;border-radius:20px;}
.kpi-badge.up{background:rgba(0,229,160,.15);color:var(--em);}
.kpi-badge.dn{background:rgba(255,77,109,.15);color:var(--ro);}
.kpi-badge.nt{background:rgba(79,142,247,.15);color:var(--sa);}

/* ── Section label ── */
.section-label{display:flex;align-items:center;gap:10px;margin:1.8rem 0 1rem;}
.section-label .line{flex:1;height:1px;background:var(--b1);}
.section-label span{font-family:'Syne',sans-serif;font-size:.68rem;font-weight:700;
  letter-spacing:.14em;text-transform:uppercase;color:var(--t4);white-space:nowrap;}

/* ── Chart card ── */
.chart-card{background:var(--s1);border:1px solid var(--b1);border-radius:16px;padding:1.4rem;margin-bottom:.9rem;}
.chart-title{font-family:'Syne',sans-serif;font-size:.95rem;font-weight:700;color:var(--t2);margin-bottom:.2rem;}
.chart-sub{font-size:.73rem;color:var(--t4);margin-bottom:1rem;}

/* ── Transaction rows ── */
.tx-row{display:flex;align-items:center;gap:.9rem;padding:.8rem 1.1rem;
  border-radius:10px;border:1px solid var(--b1);background:var(--s1);
  margin-bottom:.4rem;transition:background .15s;}
.tx-row:hover{background:var(--s2);}
.tx-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0;}
.tx-cat{font-size:.78rem;font-weight:600;color:var(--t2);min-width:85px;}
.tx-desc{font-size:.75rem;color:var(--t4);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.tx-date{font-family:'JetBrains Mono',monospace;font-size:.7rem;color:var(--t4);min-width:80px;text-align:right;}
.tx-amount{font-family:'JetBrains Mono',monospace;font-size:.88rem;font-weight:600;min-width:105px;text-align:right;}
.tx-amount.inc{color:var(--em);}
.tx-amount.exp{color:var(--ro);}

/* ── Goal cards ── */
.goal-card{background:var(--s1);border:1px solid var(--b1);border-radius:16px;
  padding:1.3rem 1.5rem;margin-bottom:.8rem;transition:border-color .2s;}
.goal-card:hover{border-color:var(--b2);}
.goal-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.9rem;}
.goal-icon{font-size:1.8rem;}
.goal-name{font-family:'Syne',sans-serif;font-size:.95rem;font-weight:700;color:var(--t1);}
.goal-target{font-family:'JetBrains Mono',monospace;font-size:.78rem;color:var(--t4);margin-top:2px;}
.goal-pct{font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:var(--em);}
.goal-track{height:8px;background:var(--s3);border-radius:4px;overflow:hidden;margin-bottom:.6rem;}
.goal-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,var(--em),var(--sa));transition:width .7s cubic-bezier(.4,0,.2,1);}
.goal-footer{display:flex;justify-content:space-between;font-size:.72rem;color:var(--t4);}
.goal-days{color:var(--am);font-weight:600;}

/* ── Health score ── */
.health-ring{text-align:center;padding:1.5rem;}
.health-score-num{font-family:'Syne',sans-serif;font-size:3.5rem;font-weight:800;}
.health-label{font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;color:var(--t4);}

/* ── Alert cards ── */
.alert-card{display:flex;align-items:flex-start;gap:.9rem;
  padding:.9rem 1.1rem;border-radius:10px;border:1px solid;margin-bottom:.5rem;}
.alert-card.warn{background:rgba(255,181,71,.06);border-color:rgba(255,181,71,.25);}
.alert-card.good{background:rgba(0,229,160,.06);border-color:rgba(0,229,160,.2);}
.alert-card.info{background:rgba(79,142,247,.06);border-color:rgba(79,142,247,.2);}
.alert-card.bad {background:rgba(255,77,109,.06);border-color:rgba(255,77,109,.2);}
.alert-icon{font-size:1.1rem;flex-shrink:0;margin-top:1px;}
.alert-text{font-size:.82rem;color:var(--t2);line-height:1.5;}
.alert-text b{color:var(--t1);}

/* ── Budget bars ── */
.budget-card{background:var(--s1);border:1px solid var(--b1);border-radius:14px;
  padding:1.1rem 1.4rem;margin-bottom:.7rem;transition:border-color .2s;}
.budget-card:hover{border-color:var(--b2);}
.budget-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.7rem;}
.budget-cat{font-family:'Syne',sans-serif;font-size:.88rem;font-weight:700;color:var(--t2);}
.budget-actual{font-family:'JetBrains Mono',monospace;font-size:.88rem;font-weight:600;}
.budget-limit{font-family:'JetBrains Mono',monospace;font-size:.68rem;color:var(--t4);}
.budget-track{height:7px;background:var(--s3);border-radius:4px;overflow:hidden;margin-bottom:.5rem;}
.budget-fill{height:100%;border-radius:4px;transition:width .6s cubic-bezier(.4,0,.2,1);}
.budget-footer{display:flex;justify-content:space-between;font-size:.7rem;color:var(--t4);}

/* ── Split cards ── */
.group-card{background:var(--s1);border:1px solid var(--b1);border-radius:14px;
  padding:1.2rem 1.4rem;margin-bottom:.7rem;cursor:pointer;transition:all .18s ease;}
.group-card:hover{background:var(--s2);border-color:var(--b2);transform:translateX(3px);}
.group-name{font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:var(--t1);}
.group-meta{font-size:.73rem;color:var(--t4);margin-top:3px;}
.owe-row{display:flex;align-items:center;justify-content:space-between;
  padding:.7rem 1rem;border-radius:8px;background:var(--s2);
  border:1px solid var(--b1);margin-bottom:.4rem;}
.owe-names{font-size:.82rem;color:var(--t2);font-weight:500;}
.owe-amount{font-family:'JetBrains Mono',monospace;font-size:.88rem;font-weight:600;}

/* ── Chat ── */
.chat-wrap{display:flex;flex-direction:column;gap:1rem;padding:.5rem 0 1rem;}
.msg-row{display:flex;gap:10px;align-items:flex-start;}
.msg-row.user{flex-direction:row-reverse;}
.msg-avatar{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:.85rem;flex-shrink:0;}
.msg-avatar.bot{background:linear-gradient(135deg,var(--em),var(--sa));}
.msg-avatar.user{background:linear-gradient(135deg,var(--vi),var(--sa));}
.msg-bubble{max-width:74%;padding:.85rem 1.1rem;border-radius:14px;
  font-size:.86rem;line-height:1.65;}
.msg-bubble.bot{background:var(--s2);border:1px solid var(--b1);color:var(--t2);border-bottom-left-radius:3px;}
.msg-bubble.user{background:linear-gradient(135deg,rgba(0,229,160,.16),rgba(0,179,126,.1));
  border:1px solid rgba(0,229,160,.22);color:var(--t1);border-bottom-right-radius:3px;}

/* ── Forms ── */
div[data-testid="stForm"]{background:var(--s1)!important;border:1px solid var(--b1)!important;
  border-radius:18px!important;padding:1.8rem!important;}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stTextArea textarea,.stSelectbox>div>div{
  background:var(--s2)!important;border:1px solid var(--b2)!important;
  border-radius:9px!important;color:var(--t1)!important;
  font-family:'Inter',sans-serif!important;font-size:.86rem!important;}
label[data-testid="stWidgetLabel"] p{
  color:var(--t3)!important;font-size:.73rem!important;font-weight:600!important;
  letter-spacing:.05em!important;text-transform:uppercase!important;}
.stButton>button{
  background:linear-gradient(135deg,var(--em),var(--em-d))!important;
  color:#080a0f!important;border:none!important;border-radius:9px!important;
  font-family:'Syne',sans-serif!important;font-weight:700!important;
  font-size:.84rem!important;padding:.6rem 1.6rem!important;
  transition:all .2s ease!important;
  box-shadow:0 4px 18px rgba(0,229,160,.2)!important;}
.stButton>button:hover{transform:translateY(-2px)!important;
  box-shadow:0 8px 28px rgba(0,229,160,.33)!important;}
button[kind="secondary"]{background:transparent!important;
  border:1px solid var(--ro)!important;color:var(--ro)!important;box-shadow:none!important;}
.stSuccess>div{background:rgba(0,229,160,.1)!important;border:1px solid rgba(0,229,160,.3)!important;
  border-radius:9px!important;color:var(--em)!important;}
.stInfo>div{background:rgba(79,142,247,.1)!important;border:1px solid rgba(79,142,247,.3)!important;border-radius:9px!important;}
.stError>div{background:rgba(255,77,109,.1)!important;border:1px solid rgba(255,77,109,.3)!important;border-radius:9px!important;}
.stWarning>div{background:rgba(255,181,71,.1)!important;border:1px solid rgba(255,181,71,.3)!important;border-radius:9px!important;}
div[data-testid="stExpander"]{background:var(--s1)!important;border:1px solid var(--b1)!important;border-radius:14px!important;}
.stDataFrame{border:1px solid var(--b1)!important;border-radius:12px!important;}
h1,h2,h3,h4{color:var(--t1)!important;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--s0);}
::-webkit-scrollbar-thumb{background:var(--s4);border-radius:3px;}
</style>
"""
