import streamlit as st
import pandas as pd
from datetime import date

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="Můj Poker Tracker", page_icon="🃏", layout="wide")
st.title("🃏 Můj Pokerový Deník")

# Odkaz na tvou Google Tabulku (export do CSV)
SHEET_ID = "1knsM2lAvBLyf6yy7SChXP2Xl5nISrKngS4MBP4HPTeA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- FUNKCE PRO NAČTENÍ DAT ---
def nacti_data():
    try:
        # Načteme data z odkazu
        data = pd.read_csv(SHEET_URL)
        
        # Vyčistíme řádky, kde není vyplněné datum (odstraní None/prázdné řádky)
        data = data.dropna(subset=['Datum'])
        
        # Převedeme číselné sloupce, aby s nimi šlo počítat
        for col in ["Vklad", "Dokup", "Výhra", "Zisk"]:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
        
        return data
    except Exception as e:
        # Pokud se něco nepovede, vytvoříme prázdnou tabulku se správnými sloupci
        return pd.DataFrame(columns=["Datum", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"])

# Načteme data do proměnné df
df = nacti_data()

# --- BOČNÍ PANEL (Zadávání) ---
st.sidebar.header("📝 Nová hra")
typ_hry = st.sidebar.selectbox("Typ", ["Casino", "Online"])
datum_hry = st.sidebar.date_input("Datum", date.today())
vklad = st.sidebar.number_input("Vklad (CZK)", min_value=0, step=100)
dokup = st.sidebar.number_input("Dokupy (CZK)", min_value=0, step=100)
vyhra = st.sidebar.number_input("Výhra (CZK)", min_value=0, step=100)

if st.sidebar.button("💾 ULOŽIT HRU"):
    st.sidebar.warning("Skoro hotovo! Teď to dopiš do Google Tabulky, než propojíme automatiku.")

# --- HLAVNÍ PLOCHA (Zobrazení) ---
if not df.empty:
    # 1. Celkový profit nahoře
    zisk_celkem = int(df["Zisk"].sum())
    if zisk_celkem >= 0:
        st.success(f"### CELKOVÝ PROFIT: {zisk_celkem} Kč 📈")
    else:
        st.error(f"### CELKOVÝ PROFIT: {zisk_celkem} Kč 📉")

    # 2. Tabulka historie (Bez indexů, Zisk na konci)
    st.subheader("Historie her")
    # Vybereme a seřadíme sloupce, aby to na mobilu sedělo
    tabulka_zobrazeni = df[["Datum", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"]]
    st.dataframe(tabulka_zobrazeni, use_container_width=True, hide_index=True)
    
    # 3. Graf vývoje (Místo indexu uvidíš Datum)
    st.subheader("Graf vývoje")
    df['Bilance'] = df['Zisk'].cumsum()
    # Uděláme kopii pro graf a nastavíme Datum jako popisek
    graf_df = df.copy()
    graf_df = graf_df.set_index('Datum')
    st.line_chart(graf_df['Bilance'])
    
else:
    st.info("Zatím nemám co zobrazit. Zkus napsat první hru do své Google Tabulky!")
 




