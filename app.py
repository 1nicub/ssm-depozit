import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURARE ---
st.set_page_config(page_title="SSM Depozit Lemn", layout="wide")

# --- DATASETS ---
if 'registru' not in st.session_state:
    st.session_state.registru = pd.DataFrame(columns=['Data', 'Nume', 'Rol', 'Scor', 'EIP_Confirmat', 'Verificat_Manager'])
if 'vizitatori' not in st.session_state:
    st.session_state.vizitatori = pd.DataFrame(columns=['Data/Ora', 'Nume Vizitator', 'Scop', 'EIP_Acordat', 'Sef_Responsabil'])

# --- TEMATICA ANGAJAȚI ---
TEMATICA = {
    "Titlu": "Instruire Tehnică Pinosa/Posch & Reguli SU (Legea 307)",
    "Continut": """
    1. **EIP:** Bocanci bombeu, salopetă, cască, antifoane, vestă.
    2. **SU:** Stivuire max. 2 paleți înălțime. Distanțe libere între stive (Culoare Pompieri).
    3. **UTILAJE:** Pinosa (alimentare încărcător), TVS40 (mâinile departe de cuțit), POSCH (distanță masă rotativă).
    """,
    "Intrebari": [
        {"q": "Înălțimea max. de stivuire?", "a": "2 paleți", "options": ["2 paleți", "4 paleți"]},
        {"q": "Regulă TVS40?", "a": "Nu deblocăm manual în mișcare", "options": ["Nu deblocăm manual în mișcare", "Lucrăm repede"]},
        {"q": "EIP obligatoriu la instalatție?", "a": "Antifoane și cască", "options": ["Doar șapcă", "Antifoane și cască"]}
    ]
}

# --- NAVIGARE ---
st.sidebar.title("🛡️ Depozit Lemn Control")
rol = st.sidebar.radio("Acces:", ["👤 Lucrător (Instruire)", "🔍 Șef Depozit (Manager)", "⚙️ Admin"])

# --- 1. MODUL LUCRĂTOR ---
if rol == "👤 Lucrător (Instruire)":
    st.header(TEMATICA["Titlu"])
    nume_ang = st.selectbox("Nume Angajat:", ["---", "Sef Depozit", "Operator 1", "Operator 2"])
    if nume_ang != "---":
        st.info(TEMATICA["Continut"])
        conf_eip = st.checkbox("Confirm purtarea EIP complet (Bocanci, Cască, Antifoane, Vestă)")
        if conf_eip:
            with st.form("test"):
                scor = 0
                for i, q in enumerate(TEMATICA["Intrebari"]):
                    r = st.radio(q['q'], q['options'], key=f"q_{i}")
                    if r == q['a']: scor += 1
                if st.form_submit_button("Finalizează"):
                    p = (scor/len(TEMATICA["Intrebari"]))*100
                    if p >= 90:
                        nou = {'Data': datetime.now().strftime("%d-%m-%Y"), 'Nume': nume_ang, 'Rol': "Echipă Depozit", 'Scor': f"{p:.0f}%", 'EIP_Confirmat': "DA", 'Verificat_Manager': False}
                        st.session_state.registru = pd.concat([st.session_state.registru, pd.DataFrame([nou])], ignore_index=True)
                        st.success("Test Promovat!")
                    else: st.error("Eșuat. Recitiți regulile.")

# --- 2. MODUL ȘEF DEPOZIT ---
elif rol == "🔍 Șef Depozit (Manager)":
    st.header("🔍 Gestiune Depozit & Vizitatori")
    t1, t2 = st.tabs(["Verificare Angajați", "Registru Vizitatori"])
    
    with t1:
        st.subheader("Instruiri în așteptare")
        st.dataframe(st.session_state.registru[st.session_state.registru['Verificat_Manager'] == False])
        if st.button("Validează Instruiri"):
            st.session_state.registru['Verificat_Manager'] = True
            st.rerun()

    with t2:
        st.subheader("🚩 Acces Cumpărători / Persoane Străine")
        with st.form("vizitator"):
            n_viz = st.text_input("Nume Vizitator")
            scop_v = st.text_input("Scopul vizitei (ex: achiziție lemn)")
            st.warning("OBLIGAȚII ȘEF DEPOZIT:")
            c1 = st.checkbox("I-am prezentat regulile de siguranță (nu se apropie de utilaje).")
            c2 = st.checkbox("I-am predat Vestă Reflectorizantă.")
            c3 = st.checkbox("Persoana va fi însoțită permanent.")
            if st.form_submit_button("Înregistrează Vizitator"):
                if n_viz and c1 and c2 and c3:
                    nv = {'Data/Ora': datetime.now().strftime("%d-%m-%Y %H:%M"), 'Nume Vizitator': n_viz, 'Scop': scop_v, 'EIP_Acordat': "DA (Vesta/Cască)", 'Sef_Responsabil': "Sef Depozit"}
                    st.session_state.vizitatori = pd.concat([st.session_state.vizitatori, pd.DataFrame([nv])], ignore_index=True)
                    st.success("Vizitator înregistrat!")
        st.dataframe(st.session_state.vizitatori)

# --- 3. MODUL ADMIN ---
elif rol == "⚙️ Admin":
    st.header("⚙️ Audit General")
    if not st.session_state.registru.empty or not st.session_state.vizitatori.empty:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            st.session_state.registru.to_excel(w, index=False, sheet_name="Angajati")
            st.session_state.vizitatori.to_excel(w, index=False, sheet_name="Vizitatori")
        st.download_button("📥 Descarcă Raport Complet (SSM + Vizitatori)", data=buf.getvalue(), file_name="audit_depozit.xlsx")
