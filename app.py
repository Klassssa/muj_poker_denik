import streamlit as st
import pandas as pd
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Můj Poker Tracker", page_icon="🃏", layout="wide")
st.title("🃏 Můj Pokerový Deník (Cloud)")

# --- PROPOJENÍ S GOOGLE SHEETS ---
# Tvůj odkaz na tabulku
SHEET_URL = "https://docs.google.com/spreadsheets/d/1knsM2lAvBLyf6yy7SChXP2Xl5nISrKngS4MBP4HPTeA/edit#gid=0"

def nacti_data_z_google():
    try:
        # Tady používáme veřejné čtení přes pandas, protože je to nejjednodušší pro začátek
        csv_url = SHEET_URL.replace('/edit#gid=0', '/export?format=csv')
        data = pd.read_csv(csv_url)
        return data
    except:
        return pd.DataFrame(columns=["Datum", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"])

df = nacti_data_z_google()

# --- BOČNÍ PANEL PRO ZADÁVÁNÍ ---
st.sidebar.header("1. Zadat novou hru")
st.sidebar.info("Data se ukládají přímo do tvé Google Tabulky.")

typ_hry = st.sidebar.selectbox("Typ hry", ["Casino", "Online"])
datum_hry = st.sidebar.date_input("Kdy jsi hrál?", date.today())
vklad = st.sidebar.number_input("Prvotní vklad (CZK)", min_value=0, step=100)
dokup = st.sidebar.number_input("Dokupy / Re-buy (CZK)", min_value=0, step=100)
vyhra = st.sidebar.number_input("Celková výhra (CZK)", min_value=0, step=100)

if st.sidebar.button("Uložit do tabulky"):
    zisk = vyhra - (vklad + dokup)
    # Tady se ti otevře návod, jak zprovoznit i zápis, ale pro začátek 
    # si zkusíme, jestli vidíš data z tabulky v aplikaci.
    st.sidebar.warning("Pro automatický zápis z aplikace musíme ještě nastavit 'Klíč', ale nejdřív zkusme, jestli vidíš v aplikaci to, co napíšeš ručně do té Google tabulky!")

# --- FILTROVÁNÍ ---
st.sidebar.divider()
st.sidebar.header("2. Filtrovat zobrazení")
filtr = st.sidebar.radio("Zobrazit:", ["Vše", "Casino", "Online"])

if filtr == "Vše":
    zobrazena_data = df
else:
    zobrazena_data = df[df["Typ"] == filtr]

# --- HLAVNÍ PLOCHA ---
if not zobrazena_data.empty:
    aktualni_zisk = zobrazena_data["Zisk"].sum()
    pocet_her = len(zobrazena_data)
    
    col1, col2 = st.columns(2)
    col1.metric(f"PROFIT ({filtr})", f"{aktualni_zisk} Kč")
    col2.metric("Počet odehraných her", pocet_her)

    st.divider()
    st.subheader(f"Historie z Google Tabulky")
    st.dataframe(zobrazena_data, use_container_width=True)
    
    st.subheader("Graf vývoje")
    zobrazena_data['Bilance'] = zobrazena_data['Zisk'].cumsum()
    st.line_chart(zobrazena_data['Bilance'])
else:
    st.info("Tabulka je zatím prázdná. Zkus do ní v počítači napsat jeden testovací řádek!")

