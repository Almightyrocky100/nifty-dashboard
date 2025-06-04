import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="NIFTY Live Dashboard", layout="wide")

# Fetch Option Chain
def get_option_chain():
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    session.get("https://www.nseindia.com", headers=headers)
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    res = session.get(url, headers=headers)
    return res.json()

def parse_option_data(data):
    ce, pe = [], []
    for d in data['records']['data']:
        if 'CE' in d:
            ce.append(d['CE'])
        if 'PE' in d:
            pe.append(d['PE'])
    return pd.DataFrame(ce), pd.DataFrame(pe)

def get_vix():
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}
    session.get("https://www.nseindia.com", headers=headers)
    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20VIX"
    res = session.get(url, headers=headers)
    for x in res.json()['data']:
        if x['index'] == 'NIFTY VIX':
            return float(x['lastPrice'])

# Main App
st.title("NIFTY Broader View - Live Dashboard")

with st.spinner("Fetching live data..."):
    data = get_option_chain()
    ce_df, pe_df = parse_option_data(data)
    pcr = pe_df['openInterest'].sum() / ce_df['openInterest'].sum()
    support = pe_df.loc[pe_df['openInterest'].idxmax()]['strikePrice']
    resistance = ce_df.loc[ce_df['openInterest'].idxmax()]['strikePrice']
    vix = get_vix()

    # Greeks (averages)
    theta_ce = ce_df['theta'].mean()
    theta_pe = pe_df['theta'].mean()
    vega_ce = ce_df['vega'].mean()
    vega_pe = pe_df['vega'].mean()
    iv_ce = ce_df['impliedVolatility'].mean()
    iv_pe = pe_df['impliedVolatility'].mean()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Put-Call Ratio")
    st.metric("PCR (PE/CE)", f"{pcr:.2f}")

    st.subheader("Support & Resistance")
    st.write(f"Support (Max PE OI): **{support}**")
    st.write(f"Resistance (Max CE OI): **{resistance}**")

    st.subheader("India VIX")
    st.metric("VIX", f"{vix}")

with col2:
    st.subheader("Options Greeks (Average)")
    st.write(f"Theta CE: {theta_ce:.2f}")
    st.write(f"Theta PE: {theta_pe:.2f}")
    st.write(f"Vega CE: {vega_ce:.2f}")
    st.write(f"Vega PE: {vega_pe:.2f}")
    st.write(f"IV CE: {iv_ce:.2f}%")
    st.write(f"IV PE: {iv_pe:.2f}%")