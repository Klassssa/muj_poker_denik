import streamlit as st
import pandas as pd
from datetime import date

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="Můj Poker Tracker", page_icon="🃏", layout="wide")
st.title("🃏 Můj Pokerový Deník")

# Odkaz na tvou Google Tabulku
SHEET_ID = "1knsM2lAvBLyf6yy7SChXP2Xl5nISrKngS4MBP4HPTeA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- FUNKCE PRO NAČTENÍ DAT ---
def nacti_data():
    try:
        data = pd.read_csv(SHEET_URL)
        data = data.dropna(subset=['Datum'])
        
        # Převedeme datum na formát DD.MM.YY (např. 10.03.26)
        # Nejdřív zajistíme, že to Python chápe jako datum
        data['Datum'] = pd.to_datetime(data['Datum'], errors='coerce')
        # Pak to zformátujeme na ten tvůj krátký zápis
        data['Datum_Short'] = data['Datum'].dt.strftime('%d.%m.%y')
        
        # Převedeme číselné sloupce
        for col in ["Vklad", "Dokup", "Výhra", "Zisk"]:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
        
        return data
    except Exception as e:
        return pd.DataFrame(columns=["Datum_Short", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"])

df = nacti_data()

# --- BOČNÍ PANEL (Zadávání) ---
st.sidebar.header("📝 Nová hra")
typ_hry = st.sidebar.selectbox("Typ", ["Casino", "Online"])
datum_hry = st.sidebar.date_input("Datum", date.today())
vklad = st.sidebar.number_input("Vklad (CZK)", min_value=0, step=100)
dokup = st.sidebar.number_input("Dokupy (CZK)", min_value=0, step=100)
vyhra = st.sidebar.number_input("Výhra (CZK)", min_value=0, step=100)

if st.sidebar.button("💾 ULOŽIT HRU"):
    st.sidebar.warning("Skoro hotovo! Teď to dopiš do Google Tabulky.")

# --- HLAVNÍ PLOCHA (Zobrazení) ---
if not df.empty:
    zisk_celkem = int(df["Zisk"].sum())
    if zisk_celkem >= 0:
        st.success(f"### CELKOVÝ PROFIT: {zisk_celkem} Kč 📈")
    else:
        st.error(f"### CELKOVÝ PROFIT: {zisk_celkem} Kč 📉")

    # 2. TABULKA - ZÚŽENÁ VERZE
    st.subheader("Historie")
    # Přejmenujeme sloupce, aby byly krátké a šetřily místo
    tabulka_fin = df[["Datum_Short", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"]]
    tabulka_fin.columns = ["Datum", "Typ", "In", "Re", "Out", "Zisk"]
    
    # Zobrazení s nastavením šířky sloupců
    st.dataframe(
        tabulka_fin, 
        use_container_width=True, 
        hide_index=True
    )
    
    # 3. GRAF VÝVOJE
    st.subheader("Graf vývoje")
    df['Bilance'] = df['Zisk'].cumsum()
    graf_df = df.copy()
    graf_df = graf_df.set_index('Datum_Short')
    st.line_chart(graf_df['Bilance'])
    
else:
    st.info("Tabulka je prázdná. Zkus něco zapsat do Google Tabulky!")
 





