import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Trial EAL League Total ranking", layout="wide")
st.title("🏆 Total ranking – Trial EAL League")

# 📁 Excelbestand ophalen vanaf GitHub
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

# ✅ Alleen gewenste kolommen selecteren, maar veilig
benodigde_kolommen = [
    "Rang", "Speler", "Score", "180'ers", "100+ finishes",
    "3-Darts Gemiddelde", "Totaal", "Winnaar"
]
beschikbare_kolommen = [col for col in benodigde_kolommen if col in df.columns]
df = df[beschikbare_kolommen]

# 🔁 Kolomnamen hernoemen voor weergave
kolom_naam_map = {
    "Rang": "Pos",
    "Speler": "Player",
    "Score": "Legs",
    "180'ers": "180s",
    "100+ finishes": "100+ finishes",
    "3-Darts Gemiddelde": "3-Dart Avg",
    "Totaal": "Total",
    "Winnaar": "Tournaments won"
}
df.rename(columns={k: v for k, v in kolom_naam_map.items() if k in df.columns}, inplace=True)

# 📊 Zet index en toon laatste update
if "Pos" in df.columns:
    df.set_index("Pos", inplace=True)

st.caption(f"📅 Laatste update: {last_updated.strftime('%d-%m-%Y %H:%M:%S')} UTC")

# 👀 Debug: laat zien of Sion erin staat
# st.write("Sion aanwezig:", df["Player"].str.contains("Sion", case=False).any())  # optioneel

# 📊 Toon de rankingtabel
st.dataframe(
    df.style.format({"3-Dart Avg": "{:.2f}"}),
    use_container_width=True,
    height=len(df) * 35  # Dynamische hoogte per speler
)
