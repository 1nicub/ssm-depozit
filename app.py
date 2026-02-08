import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import io

# --- CONFIGURARE GOOGLE SHEETS ---
# Folosim metoda "Public Editor" pentru simplitate în acest stadiu
SHEET_ID = "1nY6JmrzDB56t1pEEVSr3cwrpYSD64in4oQfmlR7ax3Y"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet="

def load_data(sheet_name):
    try:
        return pd.read_csv(URL + sheet_name)
    except:
        return pd.DataFrame()

# Nota: Pentru scriere (append), Streamlit are nevoie de un fisier de "Secrete". 
# Pana atunci, folosim st.session_state ca buffer, dar afisam datele din Google Sheets.

st.set_page_config(page_title="SSM Depozit PRO", layout="wide")

if 'registru' not in st.session_state:
    st.session_state.registru = load_data("Instruiri")
if 'vizitatori' not in st.session_state:
    st.session_state.vizitatori = load_data("Vizitatori")

# --- DATE TEST ---
INTREBARI = [
    {"q": "Înălțimea max. stivuire?", "a": "2 paleți", "opt": ["2 paleți", "5 paleți"]},
    {"q": "Regulă TVS40?", "a": "Fără deblocare manuală în mișcare", "opt": ["Fără deblocare manuală în mișcare", "Lucru rapid"]},
    {"q": "EIP obligatoriu?", "a": "Bocanci, Cască, Antifoane, Vestă", "opt": ["Doar vestă", "Bocanci, Cască, Antifoane, Vestă"]},
    {"q": "Tăietură severă?", "a": "Pansament compresiv", "opt": ["Pansament compresiv", "Spălare cu apă"]},
    {"q": "Alarmă dezastre (5 sunete)?", "a": "Evacuare imediată", "opt": ["Evacuare imediată", "Continuare lucru"]}
]

# --- NAVIGARE ---
st.sidebar.title("🪓 Control Depozit")
rol = st.sidebar.radio("Acces:", ["👤 Lucrător", "🔍 Șef Depozit", "⚙️ Admin"])
luna_an = datetime.now().strftime("%B %Y")

# --- MODUL LUCRĂTOR ---
if rol == "👤 Lucrător":
    st.header(f"🚀 Instruirea Lunii: {luna_an}")
    nume = st.selectbox("Nume:", ["---", "Operator 1", "Operator 2", "Sef Depozit"])
    
    if nume != "---":
        # Verificare dublură
        if not st.session_state.registru.empty and nume in st.session_state.registru[st.session_state.registru['Luna/An'] == luna_an]['Nume'].values:
            st.success(f"✅ {nume}, instruirea ta pe {luna_an} este deja salvată!")
        else:
            with st.form("test"):
                res = [st.radio(q['q'], q['opt']) for q in INTREBARI]
                if st.form_submit_button("Trimite"):
                    if all(r == INTREBARI[i]['a'] for i, r in enumerate(res)):
                        nou = pd.DataFrame([{'Luna/An': luna_an, 'Data': datetime.now().strftime("%d-%m-%Y"), 'Nume': nume, 'Status': "ADMIS", 'Sef_Semnatura': "Așteaptă"}])
                        st.session_state.registru = pd.concat([st.session_state.registru, nou], ignore_index=True)
                        st.balloons()
                        st.success("Test promovat!")
                    else:
                        st.error("Greșit! Mai încearcă.")

# --- MODUL ȘEF DEPOZIT ---
elif rol == "🔍 Șef Depozit":
    st.header("🔍 Validare și Vizitatori")
    tab1, tab2 = st.tabs(["✍️ Semnare", "🚶 Vizitatori"])
    with tab1:
        st.write("Instruiri de semnat:")
        st.table(st.session_state.registru[st.session_state.registru['Sef_Semnatura'] == "Așteaptă"])
        if st.button("Semnează Toate"):
            st.session_state.registru.loc[st.session_state.registru['Sef_Semnatura'] == "Așteaptă", 'Sef_Semnatura'] = f"VALIDAT {datetime.now().strftime('%H:%M')}"
            st.rerun()
    with tab2:
        v_nume = st.text_input("Nume Vizitator")
        if st.button("Înregistrează"):
            nv = pd.DataFrame([{'Data/Ora': datetime.now().strftime("%d-%m-%Y %H:%M"), 'Vizitator': v_nume}])
            st.session_state.vizitatori = pd.concat([st.session_state.vizitatori, nv], ignore_index=True)
            st.success("Vizitator salvat!")

# --- MODUL ADMIN ---
elif rol == "⚙️ Admin":
    st.header("⚙️ Audit și Istoric Acțiuni")
    st.subheader("📋 Istoric Instruiri Operatori")
    st.table(st.session_state.registru)
    
    st.subheader("📋 Istoric Vizitatori")
    st.table(st.session_state.vizitatori)
    
    if not st.session_state.registru.empty:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            st.session_state.registru.to_excel(w, index=False)
        st.download_button("📥 Descarcă Raport Excel", data=buf.getvalue(), file_name="audit_ssm.xlsx")
