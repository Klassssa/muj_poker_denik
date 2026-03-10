import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials

# --- KONFIGURACE ---
st.set_page_config(page_title="Můj Poker Tracker", page_icon="🃏", layout="wide")

# Funkce, která použije tvé "Secrets" k přihlášení do Google Tabulky
def pripoj_tabulku():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    # Tady je ID tvé tabulky
   sh = client.open_by_key("1knsM2lAvBLyf6yy7SChXP2Xl5nISrKngS4MBP4HPTeA")
    sheet = sh.get_worksheet(0)

# --- NAČTENÍ DAT ---
def nacti_data():
    try:
        sheet = pripoj_tabulku()
        data = pd.DataFrame(sheet.get_all_records())
        if data.empty:
            return pd.DataFrame(columns=["Datum", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"])
        
        # Převedeme datum na hezký formát (den.měsíc.rok)
        data['Datum_Obj'] = pd.to_datetime(data['Datum'], errors='coerce')
        data['Datum_Display'] = data['Datum_Obj'].dt.strftime('%d.%m.%y')
        
        for col in ["Vklad", "Dokup", "Výhra", "Zisk"]:
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
        return data
    except Exception as e:
        return pd.DataFrame()

df = nacti_data()

# --- BOČNÍ PANEL (Zadávání dat) ---
st.sidebar.header("📝 Nová hra")
typ_hry = st.sidebar.selectbox("Typ", ["Casino", "Online"])
datum_hry = st.sidebar.date_input("Datum", date.today())
vklad = st.sidebar.number_input("Vklad (CZK)", min_value=0, step=100)
dokup = st.sidebar.number_input("Dokupy (CZK)", min_value=0, step=100)
vyhra = st.sidebar.number_input("Výhra (CZK)", min_value=0, step=100)

if st.sidebar.button("💾 ULOŽIT HRU"):
    try:
        zisk = vyhra - (vklad + dokup)
        # Formátování řádku pro Google Tabulku
        nova_rada = [datum_hry.strftime("%Y-%m-%d"), typ_hry, vklad, dokup, vyhra, zisk]
        
        sheet = pripoj_tabulku()
        sheet.append_row(nova_rada)
        
        st.sidebar.success("✅ Hra uložena do tabulky!")
        st.rerun() # Aplikace se znovu načte i s novou hrou
    except Exception as e:
        st.sidebar.error(f"Chyba při ukládání: {e}")

# --- HLAVNÍ PLOCHA (Zobrazení výsledků) ---
st.title("🃏 Můj Pokerový Deník")

if not df.empty:
    zisk_celkem = int(df["Zisk"].sum())
    if zisk_celkem >= 0:
        st.success(f"### CELKOVÝ PROFIT: {zisk_celkem} Kč 📈")
    else:
        st.error(f"### CELKOVÝ PROFIT: {zisk_celkem} Kč 📉")

    st.subheader("Historie")
    tabulka_fin = df[["Datum_Display", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"]]
    tabulka_fin.columns = ["Datum", "Typ", "In", "Re", "Out", "Zisk"]
    st.dataframe(tabulka_fin, use_container_width=True, hide_index=True)
    
    st.subheader("Graf vývoje")
    df['Bilance'] = df['Zisk'].cumsum()
    graf_df = df.copy().set_index('Datum_Display')
    st.line_chart(graf_df['Bilance'])
else:
    st.info("Zatím žádná data. Zadej první hru vlevo!")
 








