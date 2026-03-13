"""Add Transaction page."""
import streamlit as st
from datetime import date
from utils.db import add_tx, load_tx
from utils.ui import inr2, CAT_COLOR, EXP_CATS, INC_CATS, div_label, page_hero

def render(user_id):
    page_hero("Add Transaction","Record income or expenses to keep your books accurate.")
    col_form, col_recent = st.columns([1.2,1])

    with col_form:
        with st.form("tx_form", clear_on_submit=True):
            st.markdown('<p style="font-family:Syne,sans-serif;font-weight:700;'
                        'font-size:.95rem;color:#c8d0e8;margin-bottom:.8rem;">Transaction Details</p>',
                        unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1:
                tx_date   = st.date_input("Date", value=date.today())
                tx_amount = st.number_input("Amount (₹)", min_value=0.01, step=100.0, format="%.2f")
            with c2:
                tx_type = st.selectbox("Type", ["Expense","Income"])
                cats    = EXP_CATS if tx_type=="Expense" else INC_CATS
                tx_cat  = st.selectbox("Category", cats)
            tx_desc   = st.text_area("Description", placeholder="Optional note…", height=80)
            recurring = st.selectbox("Recurring", ["None","Daily","Weekly","Monthly"])
            sub = st.form_submit_button("💾  Save Transaction", use_container_width=True)

        if sub:
            if tx_amount <= 0:
                st.error("Amount must be greater than ₹0.")
            else:
                add_tx(user_id, tx_date, tx_amount, tx_cat, tx_type, tx_desc, recurring)
                st.success(f"✅ {tx_type} of {inr2(tx_amount)} ({tx_cat}) saved!")
                st.balloons()

    with col_recent:
        div_label("Recent Entries")
        df = load_tx(user_id)
        if df.empty:
            st.info("No transactions yet.")
        else:
            rows_html = ""
            for _,r in df.head(10).iterrows():
                dc = CAT_COLOR.get(r["category"],"#8892b0")
                ac = "inc" if r["type"]=="Income" else "exp"
                sg = "+" if r["type"]=="Income" else "−"
                rows_html += f"""
                <div class="tx-row">
                  <div class="tx-dot" style="background:{dc};box-shadow:0 0 5px {dc}55;"></div>
                  <div class="tx-cat">{r['category']}</div>
                  <div class="tx-date">{r['date'].strftime('%d %b')}</div>
                  <div class="tx-amount {ac}">{sg}{inr2(r['amount'])}</div>
                </div>"""
            st.markdown(rows_html, unsafe_allow_html=True)
