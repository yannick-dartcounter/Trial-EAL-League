import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Test Trial EAL League Ranking", layout="wide")
st.title("🏆 Total Ranking Test Trial EAL League")

# 📁 URL naar Excelbestand op GitHub
url = "https://raw.githubusercontent.com/yannick-dartcounter/Trial-EAL-league/main/totaalstand_TEALT.xlsx"

@st.cache_data(ttl=60)
def laad_excel_van_github(url):
    response = requests.get(url)
    response.raise_for_status()
    df = pd.read_excel(BytesIO(response.content))
    last_updated = response.headers.get("Last-Modified", "")
    if last_updated:
        last_updated = datetime.strptime(last_updated, "%a, %d %b %Y %H:%M:%S %Z")
    else:
        last_updated = datetime.now()
    return df, last_updated

# 📥 Data ophalen
try:
    df, last_updated = laad_excel_van_github(url)
    if df.empty or df.shape[1] == 0:
        st.cache_data.clear()
        st.experimental_rerun()
except Exception as e:
    st.error("❌ Error loading Excel file:")
    st.exception(e)
    st.stop()

# 🔧 Verwijder index en vertaal kolomnamen
df.reset_index(drop=True, inplace=True)
df.rename(columns={
    "Rang": "Rank",
    "Speler": "Player",
    "180'ers": "180's",
    "Totaal": "Total"
    "Winnaar": "Tournament wins"
}, inplace=True)

# 🚫 Verberg index (0,1,2...) in st.table
df.index = [""] * len(df)

# 🕒 Laatste update tonen
st.caption(f"📅 Last updated: {last_updated.strftime('%d-%m-%Y %H:%M:%S')} UTC")

# 📊 Toon de tabel zonder afkappen
st.table(df)

# 🔽 Downloadknop
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="ranking_european_league.csv",
    mime="text/csv"
)