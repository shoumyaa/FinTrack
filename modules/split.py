"""Split Expenses page."""
import streamlit as st
import pandas as pd
from datetime import date
from utils.db import (create_group, load_groups, add_member, load_members,
                      add_split_expense, load_split_expenses, load_shares,
                      settle_expense, delete_group)
from utils.ui import inr, inr2, div_label, page_hero

def compute_balances(group_id):
    expenses = load_split_expenses(group_id)
    if expenses.empty: return {}, []
    balances = {}
    members  = load_members(group_id)
    for m in members["name"].tolist():
        balances[m] = 0.0
    for _,exp in expenses.iterrows():
        if exp["settled"]: continue
        shares = load_shares(exp["id"])
        payer  = exp["paid_by"]
        total  = float(exp["amount"])
        if payer in balances: balances[payer] = balances.get(payer, 0) + total
        for _,s in shares.iterrows():
            m = s["member"]
            balances[m] = balances.get(m, 0) - float(s["share"])
    creditors = sorted([(v,k) for k,v in balances.items() if v>0.01], reverse=True)
    debtors   = sorted([(v,k) for k,v in balances.items() if v<-0.01])
    settlements = []
    i,j = 0,0
    while i < len(creditors) and j < len(debtors):
        credit_amt, creditor = creditors[i]
        debt_amt,   debtor   = debtors[j]
        amt = min(credit_amt, -debt_amt)
        settlements.append((debtor, creditor, amt))
        creditors[i] = (credit_amt - amt, creditor)
        debtors[j]   = (debt_amt + amt, debtor)
        if creditors[i][0] < 0.01: i+=1
        if debtors[j][0]   > -0.01: j+=1
    return balances, settlements

def render(user_id):
    page_hero("Split Expenses","Track group expenses, see who owes whom, and settle up easily.")
    groups = load_groups(user_id)

    with st.expander("➕ Create New Group", expanded=groups.empty):
        with st.form("new_group"):
            c1,c2 = st.columns([2,1])
            with c1: gname = st.text_input("Group Name", placeholder="e.g. Goa Trip, Flat Expenses…")
            with c2: members_raw = st.text_input("Members", placeholder="Alice, Bob, Charlie")
            sub = st.form_submit_button("🚀  Create Group", use_container_width=True)
        if sub:
            if not gname.strip():
                st.error("Enter a group name.")
            else:
                members = [m.strip() for m in members_raw.split(",") if m.strip()]
                if len(members) < 2:
                    st.error("Add at least 2 members (comma-separated).")
                else:
                    gid = create_group(user_id, gname.strip())
                    for m in members: add_member(gid, m)
                    st.success(f"Group '{gname}' created!"); st.rerun()

    if groups.empty:
        st.markdown("""
        <div style="text-align:center;padding:4rem;background:#111420;
                    border:1px solid rgba(255,255,255,.06);border-radius:18px;">
          <div style="font-size:3.5rem;margin-bottom:1rem;">👥</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:700;
                      color:#c8d0e8;margin-bottom:.4rem;">No groups yet</div>
          <div style="color:#4a5270;font-size:.85rem;">Create a group above to start splitting expenses.</div>
        </div>""", unsafe_allow_html=True)
        return

    div_label("Your Groups")
    group_names = groups["name"].tolist()
    group_ids   = groups["id"].tolist()
    sel_name    = st.radio("Select group", group_names, horizontal=True, label_visibility="collapsed")
    sel_gid     = group_ids[group_names.index(sel_name)]

    members_df = load_members(sel_gid)
    members    = members_df["name"].tolist() if not members_df.empty else []
    if not members:
        st.warning("This group has no members."); return

    expenses_df = load_split_expenses(sel_gid)
    total_spent = expenses_df["amount"].sum() if not expenses_df.empty else 0
    unsettled   = len(expenses_df[expenses_df["settled"]==0]) if not expenses_df.empty else 0

    st.markdown(f"""
    <div style="display:flex;gap:.8rem;margin:1rem 0 1.4rem;">
      <div class="kpi-card sa" style="flex:1;padding:1rem 1.2rem;">
        <div class="kpi-glow"></div>
        <div class="kpi-label">Members</div>
        <div class="kpi-value" style="font-size:1.6rem;">{len(members)}</div>
      </div>
      <div class="kpi-card ro" style="flex:1;padding:1rem 1.2rem;">
        <div class="kpi-glow"></div>
        <div class="kpi-label">Unsettled</div>
        <div class="kpi-value" style="font-size:1.6rem;">{unsettled}</div>
      </div>
      <div class="kpi-card em" style="flex:1;padding:1rem 1.2rem;">
        <div class="kpi-glow"></div>
        <div class="kpi-label">Total Spent</div>
        <div class="kpi-value" style="font-size:1.6rem;">{inr(total_spent)}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["💸 Add Expense", "📊 Balances", "📋 All Expenses"])

    with tabs[0]:
        with st.form("add_expense_form"):
            c1,c2,c3 = st.columns([2,1,1])
            with c1: desc   = st.text_input("Description", placeholder="Dinner, Hotel, Fuel…")
            with c2: amount = st.number_input("Amount (₹)", min_value=1.0, step=50.0, format="%.2f")
            with c3: paid_by= st.selectbox("Paid by", members)
            exp_date   = st.date_input("Date", value=date.today())
            split_type = st.radio("Split type", ["Equal","Custom"], horizontal=True)
            shares = {}
            if split_type == "Equal":
                selected = st.multiselect("Select members", members, default=members)
                if selected:
                    per = amount / len(selected)
                    for m in selected: shares[m] = per
            else:
                cols = st.columns(len(members))
                for i,m in enumerate(members):
                    with cols[i]:
                        shares[m] = st.number_input(m, min_value=0.0,
                                                     value=round(amount/len(members),2),
                                                     step=10.0, format="%.2f", key=f"sh_{m}")
            sub2 = st.form_submit_button("💾  Add Expense", use_container_width=True)
        if sub2:
            if not desc.strip():
                st.error("Enter a description.")
            elif abs(sum(shares.values()) - amount) > 0.5:
                st.error(f"Shares must add up to {inr2(amount)}.")
            else:
                add_split_expense(sel_gid, desc, amount, paid_by, exp_date, shares)
                st.success(f"Expense '{desc}' added!"); st.rerun()

    with tabs[1]:
        balances, settlements = compute_balances(sel_gid)
        if not balances:
            st.info("No unsettled expenses yet.")
        else:
            div_label("Net Balances")
            bal_html=""
            for member, bal in sorted(balances.items(), key=lambda x: -x[1]):
                color = "#00e5a0" if bal>0.01 else ("#ff4d6d" if bal<-0.01 else "#8892b0")
                label = "gets back" if bal>0.01 else ("owes" if bal<-0.01 else "settled")
                bal_html += f"""
                <div class="owe-row">
                  <span class="owe-names">👤 {member}</span>
                  <span class="owe-amount" style="color:{color}">
                    {'+' if bal>0 else ''}{inr2(bal)} <span style="font-size:.7rem;color:#4a5270">({label})</span>
                  </span>
                </div>"""
            st.markdown(bal_html, unsafe_allow_html=True)
            if settlements:
                div_label("Who Pays Whom")
                for frm, to, amt in settlements:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;
                                padding:.75rem 1.1rem;border-radius:10px;background:#161a28;
                                border:1px solid rgba(255,255,255,.06);margin-bottom:.4rem;">
                      <span style="font-size:.85rem;color:#c8d0e8;">
                        <b style="color:#ff4d6d">{frm}</b>
                        <span style="color:#4a5270;margin:0 .5rem;">→ pays →</span>
                        <b style="color:#00e5a0">{to}</b>
                      </span>
                      <span style="font-family:'JetBrains Mono',monospace;
                                   font-size:.95rem;font-weight:700;color:#ffb547;">
                        {inr2(amt)}
                      </span>
                    </div>""", unsafe_allow_html=True)

    with tabs[2]:
        if expenses_df.empty:
            st.info("No expenses recorded yet.")
        else:
            for _,exp in expenses_df.iterrows():
                shares_df = load_shares(exp["id"])
                settled   = bool(exp["settled"])
                status_color = "#00e5a0" if settled else "#ffb547"
                status_text  = "Settled ✅" if settled else "Pending ⏳"
                shares_text  = " · ".join([f"{r['member']}: {inr2(r['share'])}" for _,r in shares_df.iterrows()])
                st.markdown(f"""
                <div style="background:#111420;border:1px solid rgba(255,255,255,.06);
                            border-radius:12px;padding:1rem 1.2rem;margin-bottom:.6rem;">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.5rem;">
                    <div>
                      <span style="font-family:'Syne',sans-serif;font-weight:700;
                                   font-size:.92rem;color:#f0f4ff;">{exp['description']}</span>
                      <span style="font-size:.72rem;color:#4a5270;margin-left:.7rem;">{exp['date']}</span>
                    </div>
                    <span style="font-family:'JetBrains Mono',monospace;font-weight:700;
                                 font-size:1rem;color:#f0f4ff;">{inr2(float(exp['amount']))}</span>
                  </div>
                  <div style="font-size:.75rem;color:#4a5270;">
                    Paid by <b style="color:#c8d0e8">{exp['paid_by']}</b> ·
                    <span style="color:{status_color}">{status_text}</span>
                  </div>
                  <div style="font-size:.72rem;color:#4a5270;margin-top:.3rem;">{shares_text}</div>
                </div>""", unsafe_allow_html=True)
                if not settled:
                    if st.button(f"✅ Settle #{exp['id']}", key=f"settle_{exp['id']}"):
                        settle_expense(exp["id"]); st.rerun()

    with st.expander("⚠️ Delete Group"):
        st.warning("This will permanently delete the group and all its expenses.")
        if st.button("🗑️ Delete Group", type="secondary", key="del_group"):
            delete_group(sel_gid); st.rerun()
