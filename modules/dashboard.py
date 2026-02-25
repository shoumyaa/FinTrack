"""
Dashboard page — Financial health score, smart alerts, KPIs, charts, transactions.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
from utils.db import load_tx, load_budgets, del_tx
from utils.ui import inr, inr2, CAT_COLOR, CHART, chart_card, div_label, page_hero

def health_score(income, expense, savings_rate, budget_adherence):
    """Compute a 0-100 financial health score from key metrics."""
    s = 0
    # Savings rate (max 40pts)
    s += min(savings_rate / 30 * 40, 40)
    # Expense ratio (max 30pts)
    ratio = (expense / income) if income else 1
    s += max(0, 30 - ratio * 30)
    # Budget adherence (max 30pts)
    s += budget_adherence * 30
    return min(int(s), 100)

def score_color(score):
    if score >= 75: return "#00e5a0"
    if score >= 50: return "#ffb547"
    return "#ff4d6d"

def score_label(score):
    if score >= 80: return "Excellent 🌟"
    if score >= 65: return "Good 👍"
    if score >= 50: return "Fair ⚡"
    if score >= 35: return "Needs Work ⚠️"
    return "Critical 🚨"

def generate_alerts(df, income, expense, savings_rate):
    """Generate smart, data-driven alert messages."""
    alerts = []
    if df.empty:
        return [("info","💡","Add your first transaction to get personalized insights.")]

    current_month = date.today().strftime("%Y-%m")
    df2 = df.copy(); df2["month"] = df2["date"].dt.strftime("%Y-%m")
    this_month = df2[df2["month"]==current_month]

    # Budget warnings
    budgets = load_budgets(current_month)
    if not budgets.empty and not this_month.empty:
        exp_m = this_month[this_month["type"]=="Expense"]
        actuals = exp_m.groupby("category")["amount"].sum().to_dict()
        for _, row in budgets.iterrows():
            cat, bgt = row["category"], row["budget"]
            act = actuals.get(cat, 0)
            pct = (act/bgt*100) if bgt>0 else 0
            days_left = (date(date.today().year, date.today().month%12+1, 1) - date.today()).days
            if pct > 100:
                alerts.append(("bad","🚨",f"<b>{cat}</b> budget exceeded by <b>{inr(act-bgt)}</b>!"))
            elif pct > 80:
                alerts.append(("warn","⚠️",f"<b>{cat}</b> at <b>{pct:.0f}%</b> of budget with <b>{days_left} days</b> left this month."))

    # Savings rate
    if savings_rate < 10 and income > 0:
        alerts.append(("bad","📉",f"Savings rate is only <b>{savings_rate:.1f}%</b>. Aim for at least 20%."))
    elif savings_rate >= 30:
        alerts.append(("good","🎉",f"Great job! You're saving <b>{savings_rate:.1f}%</b> of income this month."))

    # Top spending category
    if not df.empty:
        top = df[df["type"]=="Expense"].groupby("category")["amount"].sum().idxmax() if not df[df["type"]=="Expense"].empty else None
        if top:
            top_amt = df[df["type"]=="Expense"].groupby("category")["amount"].sum().max()
            alerts.append(("info","📊",f"Your biggest expense category is <b>{top}</b> at <b>{inr(top_amt)}</b>."))

    if not alerts:
        alerts.append(("good","✅","Your finances look healthy. Keep it up!"))

    return alerts[:4]

def render():
    page_hero("Dashboard","Your complete financial picture — health score, insights, and trends.")
    df = load_tx()

    income  = df[df["type"]=="Income"]["amount"].sum()  if not df.empty else 0
    expense = df[df["type"]=="Expense"]["amount"].sum() if not df.empty else 0
    savings = income - expense
    rate    = (savings/income*100) if income else 0
    tx_ct   = len(df)

    # Health score
    budgets_month = load_budgets(date.today().strftime("%Y-%m"))
    adherence = 0.7  # default
    if not budgets_month.empty and not df.empty:
        df2 = df.copy(); df2["month"] = df2["date"].dt.strftime("%Y-%m")
        this = df2[(df2["month"]==date.today().strftime("%Y-%m")) & (df2["type"]=="Expense")]
        acts = this.groupby("category")["amount"].sum().to_dict()
        under = sum(1 for _, r in budgets_month.iterrows() if acts.get(r["category"],0) <= r["budget"])
        adherence = under / len(budgets_month) if len(budgets_month) > 0 else 0.7

    score = health_score(income, expense, rate, adherence)
    sc    = score_color(score)
    sl    = score_label(score)

    # ── Top row: health score + KPIs ──────────────────────────────────────────
    col_score, col_kpis = st.columns([1, 2.5])

    with col_score:
        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number=dict(font=dict(family="Syne", size=42, color=sc), suffix=""),
            gauge=dict(
                axis=dict(range=[0,100], tickwidth=0, tickcolor="#0c0e15",
                          tickfont=dict(color="#4a5270", size=9)),
                bar=dict(color=sc, thickness=0.7),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
                steps=[
                    dict(range=[0,35],  color="rgba(255,77,109,0.12)"),
                    dict(range=[35,65], color="rgba(255,181,71,0.10)"),
                    dict(range=[65,100],color="rgba(0,229,160,0.10)"),
                ],
                threshold=dict(line=dict(color=sc, width=3), thickness=0.85, value=score)
            )
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10,b=0,l=20,r=20),
            height=200,
            font=dict(family="Inter", color="#8892b0")
        )
        st.markdown('<div class="chart-card" style="text-align:center;">'
                    '<div class="chart-title">Financial Health</div>'
                    f'<div class="chart-sub">{sl}</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_kpis:
        st.markdown(f"""
        <div class="kpi-grid">
          <div class="kpi-card em">
            <div class="kpi-glow"></div>
            <span class="kpi-icon">💵</span>
            <div class="kpi-label">Total Income</div>
            <div class="kpi-value">{inr(income)}</div>
            <span class="kpi-badge up">↑ All-time</span>
          </div>
          <div class="kpi-card ro">
            <div class="kpi-glow"></div>
            <span class="kpi-icon">💸</span>
            <div class="kpi-label">Total Expenses</div>
            <div class="kpi-value">{inr(expense)}</div>
            <span class="kpi-badge dn">↓ {tx_ct} entries</span>
          </div>
          <div class="kpi-card sa">
            <div class="kpi-glow"></div>
            <span class="kpi-icon">🏦</span>
            <div class="kpi-label">Net Savings</div>
            <div class="kpi-value">{inr(savings)}</div>
            <span class="kpi-badge {'up' if rate>=0 else 'dn'}">{rate:.1f}% rate</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Smart alerts
        alerts = generate_alerts(df, income, expense, rate)
        alerts_html = ""
        for kind, icon, msg in alerts:
            alerts_html += f'<div class="alert-card {kind}"><span class="alert-icon">{icon}</span><div class="alert-text">{msg}</div></div>'
        st.markdown(alerts_html, unsafe_allow_html=True)

    if df.empty:
        st.info("No transactions yet — add some to see charts!")
        return

    # ── Charts ────────────────────────────────────────────────────────────────
    div_label("Trends & Breakdown")
    c1, c2 = st.columns([1, 1.6])

    with c1:
        exp_df = df[df["type"]=="Expense"]
        if not exp_df.empty:
            cg = exp_df.groupby("category")["amount"].sum().reset_index()
            colors = [CAT_COLOR.get(c,"#8892b0") for c in cg["category"]]
            fig = go.Figure(go.Pie(
                labels=cg["category"], values=cg["amount"], hole=0.6,
                marker=dict(colors=colors, line=dict(color="#080a0f", width=3)),
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
                pull=[0.02]*len(cg),
            ))
            fig.add_annotation(text=f"<b>{inr(expense)}</b><br><span style='font-size:9px;color:#4a5270'>SPENT</span>",
                               x=0.5, y=0.5, showarrow=False,
                               font=dict(size=13, color="#f0f4ff", family="Syne"))
            layout = dict(**CHART); layout.update(height=300, showlegend=True,
                legend=dict(font=dict(size=9,color="#8892b0"),bgcolor="rgba(0,0,0,0)",
                            orientation="v", x=1.02, y=0.5))
            fig.update_layout(**layout)
            chart_card("Expense Breakdown","By category")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        df2 = df.copy(); df2["month"] = df2["date"].dt.to_period("M").astype(str)
        pivot = (df2.groupby(["month","type"])["amount"].sum()
                 .unstack(fill_value=0).reset_index().sort_values("month"))
        fig2 = go.Figure()
        if "Income" in pivot.columns:
            fig2.add_trace(go.Scatter(x=pivot["month"],y=pivot["Income"],name="Income",
                mode="lines+markers",line=dict(color="#00e5a0",width=2.5,shape="spline"),
                marker=dict(size=7,color="#00e5a0",line=dict(color="#080a0f",width=2)),
                fill="tozeroy",fillcolor="rgba(0,229,160,0.05)",
                hovertemplate="<b>Income</b> %{x}<br>₹%{y:,.0f}<extra></extra>"))
        if "Expense" in pivot.columns:
            fig2.add_trace(go.Scatter(x=pivot["month"],y=pivot["Expense"],name="Expense",
                mode="lines+markers",line=dict(color="#ff4d6d",width=2.5,shape="spline"),
                marker=dict(size=7,color="#ff4d6d",line=dict(color="#080a0f",width=2)),
                fill="tozeroy",fillcolor="rgba(255,77,109,0.05)",
                hovertemplate="<b>Expense</b> %{x}<br>₹%{y:,.0f}<extra></extra>"))
        layout2 = dict(**CHART); layout2.update(height=300,hovermode="x unified",
            yaxis=dict(**CHART["yaxis"],tickprefix="₹"))
        fig2.update_layout(**layout2)
        chart_card("Income vs Expense","Monthly cashflow")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Savings bar
    if len(pivot) > 1:
        pivot["Savings"] = pivot.get("Income",pd.Series([0]*len(pivot))).values - pivot.get("Expense",pd.Series([0]*len(pivot))).values
        fig3 = go.Figure(go.Bar(
            x=pivot["month"], y=pivot["Savings"],
            marker=dict(color=["#00e5a0" if s>=0 else "#ff4d6d" for s in pivot["Savings"]],
                        line=dict(color="rgba(0,0,0,.3)",width=1)),
            width=0.5,
            hovertemplate="<b>%{x}</b><br>Net: ₹%{y:,.0f}<extra></extra>"))
        layout3 = dict(**CHART); layout3.update(height=200,showlegend=False,
            yaxis=dict(**CHART["yaxis"],tickprefix="₹"))
        fig3.update_layout(**layout3)
        chart_card("Monthly Net Savings","Green = surplus · Red = deficit")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Transactions ──────────────────────────────────────────────────────────
    div_label("Recent Transactions")
    fc1, fc2, _ = st.columns([1,1,2])
    with fc1: ft = st.selectbox("Type",["All","Income","Expense"],key="d_ft")
    with fc2:
        cl = ["All"]+sorted(df["category"].unique().tolist())
        fc = st.selectbox("Category",cl,key="d_fc")

    view = df.copy()
    if ft!="All": view=view[view["type"]==ft]
    if fc!="All": view=view[view["category"]==fc]

    rows_html=""
    for _,r in view.head(25).iterrows():
        dc=CAT_COLOR.get(r["category"],"#8892b0")
        ac="inc" if r["type"]=="Income" else "exp"
        sg="+" if r["type"]=="Income" else "−"
        desc=str(r["description"] or r["category"])[:35]
        rows_html+=f"""
        <div class="tx-row">
          <div class="tx-dot" style="background:{dc};box-shadow:0 0 6px {dc}55;"></div>
          <div class="tx-cat">{r['category']}</div>
          <div class="tx-desc">{desc}</div>
          <div class="tx-date">{r['date'].strftime('%d %b %Y')}</div>
          <div class="tx-amount {ac}">{sg}{inr2(r['amount'])}</div>
        </div>"""
    st.markdown(rows_html, unsafe_allow_html=True)

    with st.expander("🗑️ Delete a transaction"):
        did = st.number_input("Transaction ID",min_value=1,step=1,key="del_id")
        if st.button("Delete",type="secondary",key="del_btn"):
            del_tx(int(did)); st.success(f"Deleted #{did}"); st.rerun()
