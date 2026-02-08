import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURARE ---
# ID-ul extras din link-ul tau de Google Sheets
SHEET_ID = "1nY6JmrzDB56t1pEEVSr3cwrpYSD64in4oQfmlR7ax3Y"
# Cream link-ul de citire directa pentru tab-ul "Instruiri" (gid=0)
URL_CITIRE = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"

def load_data():
    try:
        df = pd.read_csv(URL_CITIRE)
        # Ne asiguram ca numele coloanelor sunt curate (fara spatii)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        # Daca tabelul e gol sau are erori, returnam structura de baza
        return pd.DataFrame(columns=['Luna/An', 'Data', 'Nume', 'Status', 'Sef_Semnatura'])

st.set_page_config(page_title="Monitorizare Depozit v7.0", layout="wide")

# Initializam datele
if 'registru' not in st.session_state:
    st.session_state.registru = load_data()
if 'vizitatori' not in st.session_state:
    st.session_state.vizitatori = pd.DataFrame(columns=['Data/Ora', 'Vizitator'])

# --- TESTARE ---
INTREBARI = [
    {"q": "Înălțimea max. stivuire?", "a": "2 paleți", "opt": ["2 paleți", "5 paleți"]},
    {"q": "Regulă TVS40?", "a": "Fără deblocare manuală în mișcare", "opt": ["Fără deblocare manuală în mișcare", "Lucru rapid"]}
]

# --- NAVIGARE ---
st.sidebar.title("🪓 Control Depozit")
rol = st.sidebar.radio("Acces:", ["👤 Lucrător", "🔍 Șef Depozit", "⚙️ Admin"])
luna_an = datetime.now().strftime("%B %Y")

# --- 1. MODUL LUCRĂTOR ---
if rol == "👤 Lucrător":
    st.header(f"🚀 Instruirea: {luna_an}")
    nume = st.selectbox("Nume:", ["---", "Operator 1", "Operator 2", "Sef Depozit"])
    
    if nume != "---":
        # Verificam daca a facut deja testul luna aceasta
        if not st.session_state.registru.empty:
            deja_făcut = st.session_state.registru[
                (st.session_state.registru['Nume'] == nume) & 
                (st.session_state.registru['Luna/An'] == luna_an)
            ]
            if not deja_făcut.empty:
                st.success(f"✅ {nume}, instruirea pe {luna_an} este deja salvată!")
                st.stop()

        with st.form("test_ssm"):
            res = [st.radio(q['q'], q['opt']) for q in INTREBARI]
            if st.form_submit_button("Trimite"):
                if all(r == INTREBARI[i]['a'] for i, r in enumerate(res)):
                    nou = pd.DataFrame([{'Luna/An': luna_an, 'Data': datetime.now().strftime("%d-%m-%Y"), 'Nume': nume, 'Status': "ADMIS", 'Sef_Semnatura': "Așteaptă"}])
                    st.session_state.registru = pd.concat([st.session_state.registru, nou], ignore_index=True)
                    st.success("Test Promovat!")
                    st.rerun()
                else:
                    st.error("Răspunsuri incorecte!")

# --- 2. MODUL ȘEF DEPOZIT ---
elif rol == "🔍 Șef Depozit":
    st.header("🔍 Validare")
    if not st.session_state.registru.empty:
        # Cautam doar cele care au exact statusul "Asteapta"
        de_semnat = st.session_state.registru[st.session_state.registru['Sef_Semnatura'] == "Așteaptă"]
        if not de_semnat.empty:
            st.table(de_semnat)
            if st.button("Semnează și Validează Toate"):
                st.session_state.registru.loc[st.session_state.registru['Sef_Semnatura'] == "Așteaptă", 'Sef_Semnatura'] = f"SEMNEAZĂ {datetime.now().strftime('%H:%M')}"
                st.rerun()
        else:
            st.info("Nu sunt instruiri noi de semnat.")

# --- 3. MODUL ADMIN ---
elif rol == "⚙️ Admin":
    st.header("⚙️ Audit Complet")
    st.subheader("Istoric Operatori")
    st.dataframe(st.session_state.registru)
    
    if not st.session_state.registru.empty:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            st.session_state.registru.to_excel(w, index=False)
        st.download_button("📥 Descarcă Raport Excel", data=buf.getvalue(), file_name="audit_depozit.xlsx")
