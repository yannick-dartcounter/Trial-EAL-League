import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="European League Totaalstand", layout="wide")
st.title("🏆 Total ranking – European League")

# 📁 Excelbestand ophalen vanaf GitHub
url = "https://raw.githubusercontent.com/yannick-dartcounter/European-League/main/totaalstand_EL1_EL8.xlsx"

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
    st.error("❌ Fout bij het laden van de totaaltabel:")
    st.exception(e)
    st.stop()

# ✅ Alleen gewenste kolommen selecteren en volgorde corrigeren
df = df[[
    "Rang", "Speler", "Score", "180'ers", "100+ finishes", "3-Darts Gemiddelde", "Totaal", "Winnaar"
]]

# 🔁 Kolomnamen hernoemen voor weergave
df.rename(columns={
    "Rang": "Pos",
    "Speler": "Player",
    "Score": "Legs",
    "180'ers": "180s",
    "100+ finishes": "100+ finishes",
    "3-Darts Gemiddelde": "3-Dart Avg",
    "Totaal": "Total",
    "Winnaar": "Tournaments won"
}, inplace=True)

# 📊 Tabel instellen en weergeven
df.set_index("Pos", inplace=True)
st.caption(f"📅 Laatste update: {last_updated.strftime('%d-%m-%Y %H:%M:%S')} UTC")

st.dataframe(
    df.style.format({"3-Dart Avg": "{:.2f}"}),
    use_container_width=True,
    height=len(df) * 35  # Dynamische hoogte per speler
)
