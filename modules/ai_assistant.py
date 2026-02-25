"""
AI Assistant page — chat, monthly report generator, what-if simulator.
"""
import streamlit as st
import requests
from datetime import date
from utils.db import load_tx, load_budgets
from utils.ui import inr, inr2, div_label, page_hero

GROQ_MODEL = "llama-3.3-70b-versatile"

def build_context(df):
    if df.empty: return "No transaction data yet."
    inc = df[df["type"]=="Income"]["amount"].sum()
    exp = df[df["type"]=="Expense"]["amount"].sum()
    sav = inc - exp
    rate = (sav/inc*100) if inc else 0
    cats = df[df["type"]=="Expense"].groupby("category")["amount"].sum().sort_values(ascending=False)
    cat_lines = "\n".join([f"  - {c}: ₹{a:,.2f}" for c,a in cats.items()])
    df2 = df.copy(); df2["month"] = df2["date"].dt.strftime("%Y-%m")
    monthly = df2.groupby(["month","type"])["amount"].sum().unstack(fill_value=0).tail(4)
    m_lines = ""
    for month,row in monthly.iterrows():
        i,e = row.get("Income",0), row.get("Expense",0)
        m_lines += f"  - {month}: Income ₹{i:,.2f}, Expense ₹{e:,.2f}, Net ₹{i-e:,.2f}\n"
    rec = df[df.get("recurring","None")!="None"] if "recurring" in df.columns else df.head(0)
    return f"""FINANCIAL SUMMARY:
- Total Income: ₹{inc:,.2f} | Expenses: ₹{exp:,.2f} | Net Savings: ₹{sav:,.2f} ({rate:.1f}%)

EXPENSE BREAKDOWN BY CATEGORY:
{cat_lines}

MONTHLY TREND (last 4 months):
{m_lines}
TOTAL TRANSACTIONS: {len(df)}"""

def call_groq(key, messages, max_tokens=1200):
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
            json={"model":GROQ_MODEL,"messages":messages,"temperature":0.7,"max_tokens":max_tokens},
            timeout=30
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError:
        code = r.status_code
        if code==401: return "❌ Invalid API key."
        if code==429: return "⏳ Rate limit hit. Try again in a moment."
        return f"❌ API error {code}."
    except Exception as e:
        return f"❌ Error: {e}"

def render():
    page_hero("AI Assistant","Powered by Llama 3.3 · Knows your full transaction history.")

    # ── API Key ────────────────────────────────────────────────────────────────
    with st.expander("🔑 Groq API Key", expanded="groq_key" not in st.session_state):
        st.markdown("Free key at [console.groq.com](https://console.groq.com) → API Keys → Create")
        k = st.text_input("Paste key", type="password", placeholder="gsk_…", key="k_input")
        if st.button("Save Key"):
            if k.strip().startswith("gsk_"):
                st.session_state["groq_key"] = k.strip()
                st.success("Saved!"); st.rerun()
            else:
                st.error("Key should start with gsk_")

    if "groq_key" not in st.session_state:
        st.markdown("""
        <div style="text-align:center;padding:3rem;background:#111420;
                    border:1px solid rgba(255,255,255,.06);border-radius:18px;margin-top:1rem;">
          <div style="font-size:3rem;margin-bottom:1rem;">🔑</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
                      color:#c8d0e8;margin-bottom:.4rem;">Add your free Groq API key</div>
          <div style="color:#4a5270;font-size:.83rem;">console.groq.com → API Keys → Create → Paste above</div>
        </div>""", unsafe_allow_html=True)
        return

    key = st.session_state["groq_key"]
    df  = load_tx()
    ctx = build_context(df)
    SYSTEM = f"""You are FinBot, a world-class personal finance advisor inside the FinTrack app.
You have the user's real data:
{ctx}

Rules:
- Be specific, warm, and concise
- Use ₹ for all amounts
- Reference the user's actual numbers
- Give actionable, personalized advice
- Never fabricate data"""

    # ── Three tabs ─────────────────────────────────────────────────────────────
    tab_chat, tab_report, tab_whatif = st.tabs(["💬 Chat","📄 Monthly Report","🔮 What-If Simulator"])

    # ── Chat ──────────────────────────────────────────────────────────────────
    with tab_chat:
        if "chat" not in st.session_state: st.session_state["chat"] = []

        if not st.session_state["chat"]:
            st.markdown('<div style="margin:.5rem 0;font-size:.72rem;font-weight:700;'
                        'letter-spacing:.1em;color:#4a5270;text-transform:uppercase;">✨ Quick prompts</div>',
                        unsafe_allow_html=True)
            suggestions = [
                "Where am I overspending?","What's my savings rate?",
                "Give me a budget plan","How to cut expenses?",
                "Analyze my spending habits","What is the 50/30/20 rule?",
            ]
            cols = st.columns(3)
            for i,s in enumerate(suggestions):
                with cols[i%3]:
                    if st.button(s, key=f"s{i}", use_container_width=True):
                        st.session_state["pending"] = s; st.rerun()

        if st.session_state["chat"]:
            html = '<div class="chat-wrap">'
            for msg in st.session_state["chat"]:
                rc = "user" if msg["role"]=="user" else "bot"
                av = "🧑" if msg["role"]=="user" else "🤖"
                content = msg["content"].replace("\n","<br>")
                html += f"""
                <div class="msg-row {rc}">
                  <div class="msg-avatar {rc}">{av}</div>
                  <div><div class="msg-bubble {rc}">{content}</div></div>
                </div>"""
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)
            st.markdown("---")
            _,cb = st.columns([5,1])
            with cb:
                if st.button("Clear",type="secondary"):
                    st.session_state["chat"]=[]; st.rerun()

        user_in = st.chat_input("Ask anything about your finances…")
        if "pending" in st.session_state:
            user_in = st.session_state.pop("pending")
        if user_in:
            st.session_state["chat"].append({"role":"user","content":user_in})
            msgs = [{"role":"system","content":SYSTEM}]+st.session_state["chat"]
            with st.spinner("FinBot thinking…"):
                reply = call_groq(key, msgs)
            st.session_state["chat"].append({"role":"assistant","content":reply})
            st.rerun()

    # ── Monthly Report ────────────────────────────────────────────────────────
    with tab_report:
        st.markdown('<p style="color:#8892b0;font-size:.88rem;">Generate a full AI-written monthly '
                    'financial review with insights and recommendations.</p>', unsafe_allow_html=True)

        import pandas as pd
        months = pd.period_range(
            start=pd.Timestamp.now()-pd.DateOffset(months=5), periods=6, freq="M"
        ).strftime("%Y-%m").tolist()[::-1]
        sel_month = st.selectbox("Select month for report", months)

        if st.button("📄  Generate Monthly Report", use_container_width=True):
            if df.empty:
                st.warning("Add some transactions first!")
            else:
                df2 = df.copy(); df2["month"] = df2["date"].dt.strftime("%Y-%m")
                mdf = df2[df2["month"]==sel_month]
                if mdf.empty:
                    st.warning(f"No transactions for {sel_month}.")
                else:
                    m_inc = mdf[mdf["type"]=="Income"]["amount"].sum()
                    m_exp = mdf[mdf["type"]=="Expense"]["amount"].sum()
                    m_sav = m_inc - m_exp
                    cats  = mdf[mdf["type"]=="Expense"].groupby("category")["amount"].sum()
                    cat_str = "\n".join([f"  {c}: ₹{a:,.2f}" for c,a in cats.items()])
                    budgets = load_budgets(sel_month)
                    bgt_str = ""
                    if not budgets.empty:
                        acts = mdf[mdf["type"]=="Expense"].groupby("category")["amount"].sum().to_dict()
                        for _,r in budgets.iterrows():
                            act = acts.get(r["category"],0)
                            status = "OVER" if act>r["budget"] else "under"
                            bgt_str += f"  {r['category']}: spent ₹{act:,.0f} vs budget ₹{r['budget']:,.0f} ({status})\n"

                    report_prompt = f"""Write a comprehensive personal finance monthly report for {sel_month}.

DATA:
- Income: ₹{m_inc:,.2f}
- Expenses: ₹{m_exp:,.2f}
- Net Savings: ₹{m_sav:,.2f}
- Savings Rate: {(m_sav/m_inc*100) if m_inc else 0:.1f}%

Expense breakdown:
{cat_str}

Budget performance:
{bgt_str if bgt_str else "  No budgets set for this month."}

Write a warm, professional report with these sections:
1. 📊 Month Summary (2-3 sentences overview)
2. ✅ What Went Well
3. ⚠️ Areas of Concern
4. 💡 Specific Recommendations (3-4 actionable tips)
5. 🎯 Goal for Next Month

Use clear formatting. Be specific with numbers. Max 400 words."""

                    with st.spinner("Generating your monthly report…"):
                        report = call_groq(key, [
                            {"role":"system","content":"You are a professional financial advisor writing monthly reports."},
                            {"role":"user","content":report_prompt}
                        ], max_tokens=1500)

                    st.markdown(f"""
                    <div style="background:#111420;border:1px solid rgba(79,142,247,.25);
                                border-radius:16px;padding:1.8rem;margin-top:1rem;
                                border-top:2px solid #4f8ef7;">
                      <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
                                  color:#4f8ef7;margin-bottom:1rem;">
                        📄 Financial Report — {sel_month}
                      </div>
                      <div style="color:#c8d0e8;font-size:.87rem;line-height:1.75;
                                  white-space:pre-wrap;">{report}</div>
                    </div>""", unsafe_allow_html=True)

    # ── What-If Simulator ─────────────────────────────────────────────────────
    with tab_whatif:
        st.markdown('<p style="color:#8892b0;font-size:.88rem;">Simulate changes to your spending '
                    'and see projected savings impact over time.</p>', unsafe_allow_html=True)

        c1,c2,c3 = st.columns(3)
        with c1:
            cat_sel = st.selectbox("Category to change",
                                   ["Food","Rent","Bills","Transport","Shopping",
                                    "Entertainment","Health","Education","Other"])
        with c2:
            change_pct = st.slider("Reduce spending by", 5, 80, 20, step=5,
                                   format="%d%%")
        with c3:
            horizon = st.selectbox("Projection period", ["3 months","6 months","12 months","24 months"])

        if st.button("🔮  Run Simulation", use_container_width=True):
            if df.empty:
                st.warning("Add some transactions first!")
            else:
                # Compute actual category spend
                cat_spend = df[df["type"]=="Expense"].groupby("category")["amount"].sum().to_dict()
                cur_monthly = cat_spend.get(cat_sel, 0) / max(
                    df["date"].dt.to_period("M").nunique(), 1)
                saving_per_month = cur_monthly * (change_pct/100)
                months_int = int(horizon.split()[0])
                total_extra = saving_per_month * months_int

                inc = df[df["type"]=="Income"]["amount"].sum()
                exp = df[df["type"]=="Expense"]["amount"].sum()
                cur_sav = inc - exp
                new_rate = ((cur_sav + total_extra) / inc * 100) if inc else 0

                sim_prompt = f"""The user wants to reduce {cat_sel} spending by {change_pct}%.

Current data:
- Monthly {cat_sel} spend: ₹{cur_monthly:,.0f}
- Monthly reduction: ₹{saving_per_month:,.0f}
- Over {horizon}: ₹{total_extra:,.0f} extra savings
- New savings rate would be approximately {new_rate:.1f}%

Give a motivating, specific 3-paragraph analysis:
1. Impact of this change with exact numbers
2. What they could do with the extra ₹{total_extra:,.0f}
3. Practical tips to actually achieve this {change_pct}% reduction in {cat_sel}

Be encouraging and specific."""

                with st.spinner("Simulating…"):
                    sim_result = call_groq(key, [
                        {"role":"system","content":"You are a financial advisor running spending simulations."},
                        {"role":"user","content":sim_prompt}
                    ])

                st.markdown(f"""
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;margin:1.2rem 0;">
                  <div class="kpi-card em" style="padding:1rem;">
                    <div class="kpi-glow"></div>
                    <div class="kpi-label">Monthly Saving</div>
                    <div class="kpi-value" style="font-size:1.4rem;">{inr(saving_per_month)}</div>
                  </div>
                  <div class="kpi-card sa" style="padding:1rem;">
                    <div class="kpi-glow"></div>
                    <div class="kpi-label">Over {horizon}</div>
                    <div class="kpi-value" style="font-size:1.4rem;">{inr(total_extra)}</div>
                  </div>
                  <div class="kpi-card am" style="padding:1rem;">
                    <div class="kpi-glow"></div>
                    <div class="kpi-label">New Savings Rate</div>
                    <div class="kpi-value" style="font-size:1.4rem;">{new_rate:.1f}%</div>
                  </div>
                </div>
                <div style="background:#111420;border:1px solid rgba(167,139,250,.25);
                            border-radius:16px;padding:1.5rem;border-top:2px solid #a78bfa;">
                  <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
                              color:#a78bfa;margin-bottom:.8rem;">🔮 AI Analysis</div>
                  <div style="color:#c8d0e8;font-size:.86rem;line-height:1.75;
                              white-space:pre-wrap;">{sim_result}</div>
                </div>""", unsafe_allow_html=True)

    # ── Change key ─────────────────────────────────────────────────────────────
    with st.expander("🔄 Change API Key"):
        if st.button("Remove key", type="secondary"):
            del st.session_state["groq_key"]; st.rerun()
