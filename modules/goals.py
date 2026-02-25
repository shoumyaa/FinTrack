"""
Savings Goals page — create goals, track progress, AI-predicted completion dates.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from utils.db import add_goal, load_goals, update_goal_saved, delete_goal, load_tx
from utils.ui import inr, inr2, CHART, div_label, page_hero, GOAL_ICONS

def predict_completion(goal_row, df):
    """Use average monthly savings to predict when goal will be reached."""
    if df.empty: return None
    df2 = df.copy(); df2["month"] = df2["date"].dt.to_period("M").astype(str)
    monthly = df2.groupby(["month","type"])["amount"].sum().unstack(fill_value=0)
    if "Income" not in monthly.columns: return None
    monthly["savings"] = monthly.get("Income",0) - monthly.get("Expense",0)
    avg_monthly = monthly["savings"].tail(3).mean()
    if avg_monthly <= 0: return None
    remaining = float(goal_row["target"]) - float(goal_row["saved"])
    if remaining <= 0: return "Completed! 🎉"
    months_needed = remaining / avg_monthly
    completion = date.today() + timedelta(days=int(months_needed*30.5))
    return completion.strftime("%b %Y")

def render():
    page_hero("Savings Goals","Set targets, track progress, and let AI predict your completion date.")

    df_goals = load_goals()
    df_tx    = load_tx()

    # ── Add new goal ──────────────────────────────────────────────────────────
    with st.expander("➕ Create New Goal", expanded=df_goals.empty):
        with st.form("goal_form", clear_on_submit=True):
            c1,c2,c3 = st.columns([2,1,1])
            with c1: g_name = st.text_input("Goal Name", placeholder="e.g. New Laptop, Europe Trip…")
            with c2: g_target = st.number_input("Target (₹)", min_value=100.0, step=1000.0, format="%.0f")
            with c3: g_deadline = st.date_input("Deadline", value=date.today()+timedelta(days=180))
            g_icon = st.radio("Icon", GOAL_ICONS, horizontal=True)
            sub = st.form_submit_button("🎯  Create Goal", use_container_width=True)
        if sub:
            if not g_name.strip():
                st.error("Please enter a goal name.")
            elif g_target <= 0:
                st.error("Target must be greater than ₹0.")
            else:
                add_goal(g_name.strip(), g_target, g_deadline, g_icon)
                st.success(f"Goal '{g_name}' created!"); st.rerun()

    if df_goals.empty:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;background:#111420;
                    border:1px solid rgba(255,255,255,.06);border-radius:18px;">
          <div style="font-size:3.5rem;margin-bottom:1rem;">🎯</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;
                      color:#c8d0e8;margin-bottom:.4rem;">No goals yet</div>
          <div style="color:#4a5270;font-size:.85rem;">Create your first savings goal above.</div>
        </div>""", unsafe_allow_html=True)
        return

    div_label("Your Goals")

    # ── Summary KPIs ──────────────────────────────────────────────────────────
    total_target = df_goals["target"].sum()
    total_saved  = df_goals["saved"].sum()
    completed    = len(df_goals[df_goals["saved"] >= df_goals["target"]])

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card em">
        <div class="kpi-glow"></div>
        <span class="kpi-icon">🎯</span>
        <div class="kpi-label">Active Goals</div>
        <div class="kpi-value">{len(df_goals)}</div>
        <span class="kpi-badge nt">{completed} completed</span>
      </div>
      <div class="kpi-card sa">
        <div class="kpi-glow"></div>
        <span class="kpi-icon">💰</span>
        <div class="kpi-label">Total Saved</div>
        <div class="kpi-value">{inr(total_saved)}</div>
        <span class="kpi-badge up">of {inr(total_target)}</span>
      </div>
      <div class="kpi-card am">
        <div class="kpi-glow"></div>
        <span class="kpi-icon">📈</span>
        <div class="kpi-label">Overall Progress</div>
        <div class="kpi-value">{(total_saved/total_target*100) if total_target else 0:.0f}%</div>
        <span class="kpi-badge nt">across all goals</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Goal cards ────────────────────────────────────────────────────────────
    for _,g in df_goals.iterrows():
        pct      = min((float(g["saved"])/float(g["target"])*100) if g["target"]>0 else 0, 100)
        done     = float(g["saved"]) >= float(g["target"])
        deadline = datetime.strptime(str(g["deadline"]),"%Y-%m-%d").date() if g["deadline"] else None
        days_left= (deadline - date.today()).days if deadline else None
        eta      = predict_completion(g, df_tx)

        fill_col = "#00e5a0" if not done else "#4f8ef7"
        days_str = ""
        if days_left is not None:
            if days_left < 0:
                days_str = f'<span style="color:#ff4d6d">Overdue by {-days_left}d</span>'
            elif days_left <= 30:
                days_str = f'<span style="color:#ffb547">⚡ {days_left} days left</span>'
            else:
                days_str = f'<span style="color:#4a5270">{days_left} days left</span>'

        eta_str = f"AI predicts: <b style='color:#a78bfa'>{eta}</b>" if eta else ""

        st.markdown(f"""
        <div class="goal-card">
          <div class="goal-top">
            <div style="display:flex;align-items:center;gap:.8rem;">
              <span class="goal-icon">{g['icon']}</span>
              <div>
                <div class="goal-name">{g['name']}</div>
                <div class="goal-target">{inr(g['saved'])} saved of {inr(g['target'])}</div>
              </div>
            </div>
            <div style="text-align:right;">
              <div class="goal-pct" style="color:{'#4f8ef7' if done else '#00e5a0'}">
                {'✅' if done else f'{pct:.0f}%'}
              </div>
              <div style="font-size:.7rem;color:#4a5270;margin-top:2px;">{days_str}</div>
            </div>
          </div>
          <div class="goal-track">
            <div class="goal-fill" style="width:{pct:.1f}%;
                 background:linear-gradient(90deg,{fill_col},{fill_col}99);
                 box-shadow:0 0 8px {fill_col}44;"></div>
          </div>
          <div class="goal-footer">
            <span>{inr(float(g['target'])-float(g['saved']))} remaining</span>
            <span>{eta_str}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Add money + delete controls
        ca, cb, cc = st.columns([2,1,1])
        with ca:
            deposit = st.number_input(f"Add to {g['name']}", min_value=0.0,
                                      step=100.0, format="%.0f", key=f"dep_{g['id']}")
        with cb:
            st.markdown("<div style='margin-top:1.6rem;'></div>", unsafe_allow_html=True)
            if st.button("➕ Add", key=f"add_{g['id']}"):
                if deposit > 0:
                    update_goal_saved(g['id'], deposit)
                    st.success(f"Added {inr(deposit)}!"); st.rerun()
        with cc:
            st.markdown("<div style='margin-top:1.6rem;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Delete", key=f"del_{g['id']}", type="secondary"):
                delete_goal(g['id']); st.rerun()

    # ── Progress radar chart ──────────────────────────────────────────────────
    if len(df_goals) >= 2:
        div_label("Goals Overview")
        pcts = [min(float(r["saved"])/float(r["target"])*100,100) if r["target"]>0 else 0
                for _,r in df_goals.iterrows()]
        names = [f"{r['icon']} {r['name']}" for _,r in df_goals.iterrows()]
        fig = go.Figure(go.Scatterpolar(
            r=pcts+[pcts[0]], theta=names+[names[0]],
            fill='toself', fillcolor='rgba(0,229,160,0.08)',
            line=dict(color='#00e5a0', width=2),
            marker=dict(color='#00e5a0', size=7),
        ))
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True,range=[0,100],tickfont=dict(color="#4a5270",size=9),
                                gridcolor="rgba(255,255,255,0.05)"),
                angularaxis=dict(tickfont=dict(color="#8892b0",size=10),
                                 gridcolor="rgba(255,255,255,0.05)")
            ),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, height=320,
            margin=dict(t=20,b=20,l=40,r=40),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
