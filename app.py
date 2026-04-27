import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIG ---
st.set_page_config(page_title="Bharat Austere", page_icon="🏦", layout="centered")

# --- DATA ---
STATE_CODES = {
    '01':'Jammu & Kashmir','02':'Himachal Pradesh','03':'Punjab',
    '04':'Chandigarh','05':'Uttarakhand','06':'Haryana',
    '07':'Delhi','08':'Rajasthan','09':'Uttar Pradesh',
    '10':'Bihar','18':'Assam','19':'West Bengal',
    '20':'Jharkhand','21':'Odisha','22':'Chhattisgarh',
    '23':'Madhya Pradesh','24':'Gujarat','27':'Maharashtra',
    '29':'Karnataka','30':'Goa','32':'Kerala',
    '33':'Tamil Nadu','36':'Telangana','37':'Andhra Pradesh'
}
ENTITY_TYPES = {
    'P':'Individual/Proprietor','C':'Pvt/Public Ltd Company',
    'H':'Hindu Undivided Family','F':'Firm/Partnership',
    'A':'Association of Persons','T':'Trust','G':'Government'
}
SAMPLE_DATA = {
    "27AABCS1429B1Z1": {"company_name":"Sharma Steel Works","annual_turnover_lakh":85,"gst_filed_on_time":11,"years_in_business":8,"existing_loans_lakh":10,"payment_delays_last_year":1},
    "29AABCK1234D1Z2": {"company_name":"Kumar Textiles","annual_turnover_lakh":12,"gst_filed_on_time":6,"years_in_business":2,"existing_loans_lakh":8,"payment_delays_last_year":4},
    "24AABCG5678E1Z3": {"company_name":"Gupta Chemicals","annual_turnover_lakh":240,"gst_filed_on_time":12,"years_in_business":15,"existing_loans_lakh":0,"payment_delays_last_year":0},
}

# --- FUNCTIONS ---
def decode_gstin(gstin):
    gstin = gstin.strip().upper()
    if len(gstin) != 15:
        return None
    return {
        'gstin': gstin,
        'state': STATE_CODES.get(gstin[:2], 'Unknown'),
        'pan': gstin[2:12],
        'entity_type': ENTITY_TYPES.get(gstin[5], 'Other')
    }

def get_score(data):
    score  = (data['gst_filed_on_time'] / 12) * 30
    score += min(data['years_in_business'] / 10, 1) * 20
    score += min(data['annual_turnover_lakh'] / 200, 1) * 25
    debt   = data['existing_loans_lakh'] / max(data['annual_turnover_lakh'], 1)
    score += max(0, 1 - debt) * 15
    score += max(0, 1 - data['payment_delays_last_year'] / 6) * 10
    return round(score, 1)

def show_chart(data, score):
    factors  = ['GST Compliance','Business Age','Turnover','Debt Ratio','Payment History']
    values   = [
        (data['gst_filed_on_time']/12)*30,
        min(data['years_in_business']/10,1)*20,
        min(data['annual_turnover_lakh']/200,1)*25,
        max(0,1-data['existing_loans_lakh']/max(data['annual_turnover_lakh'],1))*15,
        max(0,1-data['payment_delays_last_year']/6)*10
    ]
    max_vals = [30,20,25,15,10]
    colors   = ['#27ae60' if v/m>=0.7 else '#f39c12' if v/m>=0.4 else '#e74c3c' for v,m in zip(values,max_vals)]
    fig, ax  = plt.subplots(figsize=(9,4))
    ax.barh(factors, max_vals, color='#f0f0f0', height=0.5, zorder=0)
    ax.barh(factors, values,   color=colors,    height=0.5)
    for i,(v,m) in enumerate(zip(values,max_vals)):
        ax.text(m+0.3, i, f'{v:.1f}/{m}', va='center', fontsize=10)
    ax.set_xlim(0,35)
    ax.set_title(f"{data['company_name']} | Score: {score}/100", fontweight='bold')
    ax.set_xlabel('Points Scored')
    plt.tight_layout()
    st.pyplot(fig)

# --- UI ---
st.title("🏦 Bharat Austere Credit Intelligence")
st.caption("MSME Credit Scoring Platform — v0.3")
st.divider()

gstin = st.text_input("GSTIN Number Daalo", placeholder="e.g. 27AABCS1429B1Z1")

if st.button("Score Nikalo ▶", type="primary"):
    if not gstin:
        st.error("GSTIN daalna zaroori hai!")
    else:
        info = decode_gstin(gstin)
        if not info:
            st.error("Invalid GSTIN — exactly 15 characters chahiye")
        else:
            st.success(f"✅ State: {info['state']}  |  Entity: {info['entity_type']}")
            data = SAMPLE_DATA.get(gstin.strip().upper())
            if data:
                score = get_score(data)
                c1, c2, c3 = st.columns(3)
                c1.metric("Company", data['company_name'])
                c2.metric("Credit Score", f"{score} / 100")
                if score >= 75:   c3.success("🟢 APPROVE")
                elif score >= 50: c3.warning("🟡 REVIEW")
                else:             c3.error("🔴 REJECT")
                show_chart(data, score)
            else:
                st.warning("Yeh GSTIN sample DB mein nahi — Real GST API se connect hone ke baad live data aayega.")

st.divider()
st.caption("Powered by Bharat Austere © 2026")
