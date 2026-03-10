import streamlit as st
import pandas as pd
from datetime import date

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Můj Poker Tracker", page_icon="🃏", layout="wide")
st.title("🃏 Můj Pokerový Deník (Cloud)")

# Odkaz na tvou tabulku (pro čtení)
SHEET_ID = "1knsM2lAvBLyf6yy7SChXP2Xl5nISrKngS4MBP4HPTeA"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def nacti_data():
    try:
        return pd.read_csv(SHEET_URL)
    except:
        return pd.DataFrame(columns=["Datum", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"])

df = nacti_data()

# --- BOČNÍ PANEL ---
st.sidebar.header("1. Zadat novou hru")

typ_hry = st.sidebar.selectbox("Typ hry", ["Casino", "Online"])
datum_hry = st.sidebar.date_input("Kdy jsi hrál?", date.today())
vklad = st.sidebar.number_input("Prvotní vklad (CZK)", min_value=0, step=100)
dokup = st.sidebar.number_input("Dokupy / Re-buy (CZK)", min_value=0, step=100)
vyhra = st.sidebar.number_input("Celková výhra (CZK)", min_value=0, step=100)

if st.sidebar.button("Připravit zápis"):
    zisk = vyhra - (vklad + dokup)
    # Vytvoříme odkaz, který po kliknutí předvyplní data v Google Formuláři nebo Tabulce
    # Pro teď to uděláme tak, že ti to vypíše potvrzení
    st.sidebar.success(f"Super! Hra za {zisk} Kč připravena.")
    st.sidebar.info("Tip: Zatímco ladíme automatický zápis, dopiš tuhle hru do Google Tabulky ručně. V aplikaci se hned objeví!")

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
    # Převod na čísla, kdyby se v tabulce něco popletlo
    for col in ["Vklad", "Dokup", "Výhra", "Zisk"]:
        zobrazena_data[col] = pd.to_numeric(zobrazena_data[col], errors='coerce').fillna(0)

    aktualni_zisk = zobrazena_data["Zisk"].sum()
    pocet_her = len(zobrazena_data)
    
    col1, col2 = st.columns(2)
    col1.metric(f"CELKOVÝ PROFIT ({filtr})", f"{int(aktualni_zisk)} Kč")
    col2.metric("Odehrané hry", pocet_her)

    st.divider()
    st.subheader(f"Historie her (z Google Tabulky)")
    st.dataframe(zobrazena_data, use_container_width=True)
    
    if len(zobrazena_data) > 1:
        st.subheader("Graf vývoje konta")
        graf_data = zobrazena_data.copy()
        graf_data['Bilance'] = graf_data['Zisk'].cumsum()
        st.line_chart(graf_data['Bilance'])
else:
    st.info("Tabulka je prázdná nebo se načítá...")


