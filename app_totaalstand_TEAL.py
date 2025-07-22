import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Trial EAL League Total ranking", layout="wide")
st.title("🏆 Total ranking – Trial EAL League")

# 📁 GitHub-bestand
url = "https://raw.githubusercontent.com/yannick-dartcounter/Trial-EAL-League/main/totaalstand_TEAL1_TEAL5.xlsx"

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

# 📥 Data ophalen (met fallback naar upload)
df = None
last_updated = None

try:
    df, last_updated = laad_excel_van_github(url)
    if df.empty or df.shape[1] == 0:
        raise ValueError("Leeg of ongeldig bestand")
except Exception as e:
    st.warning("⚠️ Kon het Excel-bestand niet laden vanaf GitHub. Upload het handmatig hieronder.")
    uploaded_file = st.file_uploader("📤 Upload Excel-bestand", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        last_updated = datetime.now()
    else:
        st.stop()

# ✅ Alleen gewenste kolommen selecteren en volgorde corrigeren
df = df[[
    "Rang", "Speler", "Score", "180'ers", "100+ finishes",
    "3-Darts Gemiddelde", "Totaal", "Winnaar"
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

# 📊 Zet index en toon laatste update
df.set_index("Pos", inplace=True)
st.caption(f"📅 Laatste update: {last_updated.strftime('%d-%m-%Y %H:%M:%S')} UTC")

# 📊 Toon de rankingtabel
st.dataframe(
    df.style.format({"3-Dart Avg": "{:.2f}"}),
    use_container_width=True,
    height=len(df) * 35
)
