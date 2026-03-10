import streamlit as st
import pandas as pd
import os
from datetime import date

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Můj Poker Tracker", page_icon="🃏", layout="wide")
st.title("🃏 Můj Pokerový Deník")

SOUBOR_DATA = "moje_poker_hry.csv"

# Načtení dat a zajištění, že máme všechny sloupce
def nacti_data():
    if os.path.exists(SOUBOR_DATA):
        data = pd.read_csv(SOUBOR_DATA)
        # Pokud by v souboru chyběl sloupec Dokup (ze starších verzí), přidáme ho
        if "Dokup" not in data.columns:
            data["Dokup"] = 0
        return data
    else:
        return pd.DataFrame(columns=["Datum", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"])

df = nacti_data()

# --- BOČNÍ PANEL ---
st.sidebar.header("1. Zadat novou hru")
typ_hry = st.sidebar.selectbox("Typ hry", ["Casino", "Online"], key="add_type")
datum_hry = st.sidebar.date_input("Kdy jsi hrál?", date.today())
vklad = st.sidebar.number_input("Prvotní vklad (CZK)", min_value=0, step=100)
dokup = st.sidebar.number_input("Dokupy / Re-buy (CZK)", min_value=0, step=100)
vyhra = st.sidebar.number_input("Celková výhra (CZK)", min_value=0, step=100)

if st.sidebar.button("Uložit výsledek"):
    # Zisk počítáme jako Výhra minus (Vklad + Dokup)
    zisk = vyhra - (vklad + dokup)
    nova_rada = pd.DataFrame([[str(datum_hry), typ_hry, vklad, dokup, vyhra, zisk]], 
                             columns=["Datum", "Typ", "Vklad", "Dokup", "Výhra", "Zisk"])
    df = pd.concat([df, nova_rada], ignore_index=True)
    df.to_csv(SOUBOR_DATA, index=False)
    st.sidebar.success(f"Zapsáno!")
    st.rerun()

st.sidebar.divider()

# --- FILTROVÁNÍ ---
st.sidebar.header("2. Filtrovat zobrazení")
filtr = st.sidebar.radio("Zobrazit:", ["Vše", "Casino", "Online"])

if filtr == "Vše":
    zobrazena_data = df
else:
    zobrazena_data = df[df["Typ"] == filtr]

# --- HLAVNÍ PLOCHA ---
if not df.empty:
    # Statistiky z vyfiltrovaných dat
    aktualni_zisk = zobrazena_data["Zisk"].sum()
    pocet_her = len(zobrazena_data)
    
    col1, col2 = st.columns(2)
    col1.metric(f"PROFIT ({filtr})", f"{aktualni_zisk} Kč")
    col2.metric("Počet odehraných her", pocet_her)

    st.divider()

    st.subheader(f"Historie: {filtr}")
    # Editor pro úpravy
    edited_df = st.data_editor(zobrazena_data, use_container_width=True, num_rows="dynamic")
    
    if st.button("Uložit změny v tabulce"):
        if filtr == "Vše":
            final_df = edited_df
        else:
            ostatni_data = df[df["Typ"] != filtr]
            final_df = pd.concat([ostatni_data, edited_df], ignore_index=True)
        
        # Přepočítáme zisk u upravených řádků, kdybys v tabulce změnil vklad nebo výhru
        final_df["Zisk"] = final_df["Výhra"] - (final_df["Vklad"] + final_df["Dokup"])
        final_df.to_csv(SOUBOR_DATA, index=False)
        st.success("Změny uloženy!")
        st.rerun()

    if not zobrazena_data.empty:
        st.subheader("Graf vývoje konta")
        zobrazena_data = zobrazena_data.copy()
        zobrazena_data['Bilance'] = zobrazena_data['Zisk'].astype(float).cumsum()
        st.line_chart(zobrazena_data['Bilance'])
else:
    st.info("Zatím jsi nezadal žádnou hru.")
