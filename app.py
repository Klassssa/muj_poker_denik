import streamlit as st
import pandas as pd
from datetime import date

# --- KONFIGURACE ---
st.set_page_config(page_title="Můj Poker Tracker", page_icon="🃏", layout="wide")
st.title("🃏 Můj Pokerový Deník")

# Odkaz na tvou tabulku
SHEET_ID = "1knsM2lAvBLyf6yy7SChXP2Xl5nISrKngS4MBP4HPTeA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def nacti_data():
    try:
        data = pd.read_csv(SHEET_URL)
        data = data.dropna(subset=['Datum'])
        for col in ["Vklad", "Dokup", "Výhra", "Zisk"]:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
        return data
    except:
        return pd.DataFrame(columns=["Datum", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"])

df = nacti_data()

# --- BOČNÍ PANEL ---
st.sidebar.header("📝 Nová hra")
typ_hry = st.sidebar.selectbox("Typ", ["Casino", "Online"])
datum_hry = st.sidebar.date_input("Datum", date.today())
vklad = st.sidebar.number_input("Vklad (CZK)", min_value=0, step=100)
dokup = st.sidebar.number_input("Dokupy (CZK)", min_value=0, step=100)
vyhra = st.sidebar.number_input("Výhra (CZK)", min_value=0, step=100)

if st.sidebar.button("💾 ULOŽIT HRU"):
    st.sidebar.warning("Zatím dopiš hru do Google Tabulky.")

# --- HLAVNÍ PLOCHA ---
if not df.empty:
    zisk_celkem = int(df["Zisk"].sum())
    
    # Velký přehled nahoře - Tady uvidíš zisk hned, i bez tabulky!
    if zisk_celkem >= 0:
        st.success(f"### CELKOVÝ PROFIT: {zisk_celkem} Kč 📈")
    else:
        st.error(f"### CELKOVÝ PROFIT: {zisk_celkem} Kč 📉")

    # TABULKA - ZISK JE ZPĚT NA KONCI A BEZ ČÍSEL 0, 1, 2...
    st.subheader("Historie")
    st.dataframe(
        df[["Datum", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"]], 
        use_container_width=True, 
        hide_index=True
    )
    
    # GRAF
    
st.subheader("Graf vývoje")
    df['Bilance'] = df['Zisk'].cumsum()
    # Nastavíme Datum jako index jen pro graf, aby se zobrazovalo v tom vyskakovacím okýnku
    graf_data = df.set_index('Datum')
    st.line_chart(graf_data['Bilance'])



