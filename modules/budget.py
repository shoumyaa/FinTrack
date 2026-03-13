"""Monthly Budget page."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from utils.db import load_budgets, upsert_budget, load_tx
from utils.ui import inr, EXP_CATS, CHART, chart_card, div_label, page_hero

def render(user_id):
    page_hero("Monthly Budget","Set spending limits and track how well you're sticking to them.")

    months = pd.period_range(
        start=pd.Timestamp.now()-pd.DateOffset(months=11), periods=12, freq="M"
    ).strftime("%Y-%m").tolist()[::-1]
    sel = st.selectbox("Month", months)

    exist = load_budgets(user_id, sel)
    edict = dict(zip(exist["category"], exist["budget"])) if not exist.empty else {}

    with st.expander("🎯 Set / Update Budget Limits", expanded=True):
        with st.form("bform"):
            st.markdown(f'<p style="font-family:Syne,sans-serif;font-weight:700;'
                        f'color:#c8d0e8;margin-bottom:.8rem;">Limits for {sel}</p>',
                        unsafe_allow_html=True)
            cols = st.columns(3)
            binputs = {}
            for i,cat in enumerate(EXP_CATS):
                with cols[i%3]:
                    binputs[cat] = st.number_input(
                        cat, min_value=0.0, value=float(edict.get(cat,0)),
                        step=500.0, format="%.0f", key=f"b_{cat}")
            save = st.form_submit_button("💾  Save Budgets", use_container_width=True)
        if save:
            for cat,v in binputs.items():
                if v > 0: upsert_budget(user_id, sel, cat, v)
            st.success("Budgets updated!"); st.rerun()

    bdf = load_budgets(user_id, sel)
    if bdf.empty:
        st.info("No budgets set for this month yet."); return

    df = load_tx(user_id)
    actuals = {}
    if not df.empty:
        df["month"] = df["date"].dt.strftime("%Y-%m")
        mx = df[(df["month"]==sel)&(df["type"]=="Expense")]
        actuals = mx.groupby("category")["amount"].sum().to_dict()

    div_label("Budget vs Actual")
    rows = []
    for _,row in bdf.iterrows():
        cat,bgt = row["category"],row["budget"]
        act = actuals.get(cat,0.0)
        pct = min((act/bgt*100) if bgt>0 else 0, 100)
        rows.append({"cat":cat,"budget":bgt,"actual":act,"pct":pct,"over":act>bgt})

    html=""
    for r in rows:
        fc = "#ff4d6d" if r["over"] else "#00e5a0"
        status = (f'<span style="color:#ff4d6d">Over by {inr(r["actual"]-r["budget"])}</span>'
                  if r["over"] else
                  f'<span style="color:#00e5a0">{inr(r["budget"]-r["actual"])} left</span>')
        html+=f"""
        <div class="budget-card">
          <div class="budget-header">
            <div><div class="budget-cat">{r['cat']}</div></div>
            <div style="text-align:right">
              <div class="budget-actual" style="color:{'#ff4d6d' if r['over'] else '#f0f4ff'}">{inr(r['actual'])}</div>
              <div class="budget-limit">of {inr(r['budget'])}</div>
            </div>
          </div>
          <div class="budget-track">
            <div class="budget-fill" style="width:{r['pct']:.1f}%;
                 background:linear-gradient(90deg,{fc},{fc}99);
                 box-shadow:0 0 6px {fc}44;"></div>
          </div>
          <div class="budget-footer"><span>{r['pct']:.0f}% used</span><span>{status}</span></div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)

    if rows:
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Budget",x=[r["cat"] for r in rows],y=[r["budget"] for r in rows],
            marker=dict(color="rgba(79,142,247,.2)",line=dict(color="#4f8ef7",width=1)),width=0.35))
        fig.add_trace(go.Bar(name="Actual",x=[r["cat"] for r in rows],y=[r["actual"] for r in rows],
            marker=dict(color=["#ff4d6d" if r["over"] else "#00e5a0" for r in rows]),width=0.35))
        layout=dict(**CHART); layout.update(barmode="group",height=260,
            yaxis=dict(**CHART["yaxis"],tickprefix="₹"))
        fig.update_layout(**layout)
        chart_card("Budget vs Actual","Side-by-side comparison")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)
