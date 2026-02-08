import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="SSM Depozit Lemn", layout="wide")

# --- DATE INITIALE ---
if 'registru' not in st.session_state:
    st.session_state.registru = pd.DataFrame(columns=['Data', 'Nume', 'Scor', 'EIP_Confirmat', 'Verificat_Manager'])
if 'vizitatori' not in st.session_state:
    st.session_state.vizitatori = pd.DataFrame(columns=['Data/Ora', 'Vizitator', 'Scop', 'Sef_Responsabil'])

# --- NAVIGARE ---
st.sidebar.title("🪓 Control Depozit")
rol = st.sidebar.radio("Acces Secțiune:", ["👤 Lucrător", "🔍 Șef Depozit", "⚙️ Admin"])

# --- 1. MODUL LUCRĂTOR ---
if rol == "👤 Lucrător":
    st.header("📋 Instruirea: Pinosa, POSCH & SU")
    nume = st.selectbox("Selectează numele tău:", ["---", "Sef Depozit", "Operator 1", "Operator 2"])
    
    if nume != "---":
        st.info("Reguli: Max 2 paleți înălțime. Interzis mâna în TVS40. EIP obligatoriu.")
        eip_ok = st.checkbox("Confirm că port EIP complet (Bocanci, Cască, Antifoane, Vestă)")
        
        with st.form("test_ssm"):
            q1 = st.radio("Înălțimea max. stivuire?", ["2 paleți", "5 paleți"])
            q2 = st.radio("Regulă TVS40?", ["Nu deblocăm manual în mișcare", "Lucrăm rapid"])
            
            if st.form_submit_button("Trimite Instruirea"):
                if eip_ok and q1 == "2 paleți" and q2 == "Nu deblocăm manual în mișcare":
                    nou = {'Data': datetime.now().strftime("%d-%m-%Y"), 'Nume': nume, 'Scor': "100%", 'EIP_Confirmat': "DA", 'Verificat_Manager': False}
                    st.session_state.registru = pd.concat([st.session_state.registru, pd.DataFrame([nou])], ignore_index=True)
                    st.success("✅ Instruire înregistrată!")
                else:
                    st.error("❌ Verifică răspunsurile sau bifa EIP!")

# --- 2. MODUL ȘEF DEPOZIT ---
elif rol == "🔍 Șef Depozit":
    st.header("🔍 Gestiune Vizitatori")
    with st.form("viz"):
        v_nume = st.text_input("Nume Vizitator")
        scop = st.text_input("Scop vizită")
        st.warning("EIP Vizitator: Vestă obligatorie!")
        if st.form_submit_button("Înregistrează"):
            if v_nume:
                nv = {'Data/Ora': datetime.now().strftime("%d-%m-%Y %H:%M"), 'Vizitator': v_nume, 'Scop': scop, 'Sef_Responsabil': "Sef Depozit"}
                st.session_state.vizitatori = pd.concat([st.session_state.vizitatori, pd.DataFrame([nv])], ignore_index=True)
                st.success("Vizitator salvat!")
    st.subheader("Registru Vizitatori Azi")
    st.dataframe(st.session_state.vizitatori)

# --- 3. MODUL ADMIN ---
elif rol == "⚙️ Admin":
    st.header("⚙️ Audit și Raportare")
    st.write("Toate instruirile efectuate:")
    st.dataframe(st.session_state.registru)
