import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- 1. CONFIGURARE DATE ȘI ECHIPĂ ---
ECHIPA = {
    "Sef Depozit": ["Fasonator mecanic", "Stivuitorist"],
    "Operator 1": ["Operator Pinosa", "Stivuitorist", "Fasonator"],
    "Operator 2": ["Operator Pinosa", "Stivuitorist", "Fasonator"]
}

# --- 2. CELE 9 ÎNTREBĂRI ESENȚIALE ---
INTREBARI_9 = [
    # GRUPA 1: UTILAJE (Pinosa, TVS40, Posch)
    {"q": "Cum se alimentează corect procesorul Pinosa CPE 1300?", "a": "Exclusiv cu încărcătorul frontal", "options": ["Manual", "Exclusiv cu încărcătorul frontal", "Cu stivuitorul"]},
    {"q": "Ce faci dacă despicătorul TVS40 se blochează cu o așchie?", "a": "Opresc utilajul complet înainte de intervenție", "options": ["Scot așchia rapid cu mâna", "Opresc utilajul complet înainte de intervenție", "Folosesc o mănușă groasă în mers"]},
    {"q": "Care este principala regulă la ambalatorul POSCH?", "a": "Păstrarea distanței față de masa rotativă", "options": ["Păstrarea distanței față de masa rotativă", "Alimentarea manuală din mers", "Verificarea plasei fără a opri rotația"]},
    
    # GRUPA 2: SU ȘI STIVUIRE (Legea 307)
    {"q": "Care este înălțimea maximă permisă pentru stivuirea paleților în curte?", "a": "2 niveluri (paleți)", "options": ["3 niveluri", "2 niveluri (paleți)", "Oricât permite spațiul"]},
    {"q": "Conform Legii 307/2006, ce trebuie menținut liber permanent?", "a": "Căile de acces pentru pompieri între stive", "options": ["Căile de acces pentru pompieri între stive", "Doar poarta principală", "Spațiul de lângă birou"]},
    {"q": "Unde sunt depozitați buștenii neprocesați?", "a": "În zona exterioară dedicată, respectând distanțele de siguranță", "options": ["Lângă clădirea administrativă", "În zona exterioară dedicată, respectând distanțele de siguranță", "Sub liniile de tensiune"]},

    # GRUPA 3: EIP (Echipament Protecție)
    {"q": "Ce EIP este obligatoriu la operarea instalațiilor de tăiere (Pinosa)?", "a": "Antifoane, cască, bocanci cu bombeu și salopetă", "options": ["Doar vestă", "Antifoane, cască, bocanci cu bombeu și salopetă", "Ochelari de soare"]},
    {"q": "De ce sunt obligatorii bocancii cu bombeu metalic?", "a": "Pentru protecție la strivire de către bușteni/paleți", "options": ["Pentru confort", "Pentru protecție la strivire de către bușteni/paleți", "Pentru a nu aluneca pe gheață"]},
    {"q": "Când trebuie purtată vesta reflectorizantă?", "a": "Permanent în incinta depozitului", "options": ["Doar noaptea", "Permanent în incinta depozitului", "Doar când vine șeful"]}
]

# --- 3. INIȚIALIZARE BAZE DE DATE ---
if 'registru' not in st.session_state:
    st.session_state.registru = pd.DataFrame(columns=['Data', 'Nume', 'Rol', 'Scor', 'Verificat_Manager'])
if 'registru_vizitatori' not in st.session_state:
    st.session_state.registru_vizitatori = pd.DataFrame(columns=['Data/Ora', 'Nume Vizitator', 'Scop', 'EIP_Acordat', 'Instruit_de'])

# --- 4. INTERFAȚĂ ---
st.sidebar.title("🪓 SSM & SU Depozit Lemn")
rol = st.sidebar.radio("Navigare:", ["👤 Angajați", "🔍 Manager (Șef Depozit)", "⚙️ Admin"])

# --- MODUL ANGAJAȚI ---
if rol == "👤 Angajați":
    st.header("📋 Instruirea Periodică SSM/SU")
    nume = st.selectbox("Alege numele tău:", ["---"] + list(ECHIPA.keys()))
    
    if nume != "---":
        st.write(f"**Calificări:** {', '.join(ECHIPA[nume])}")
        st.checkbox("Confirm că port EIP complet (Bocanci, Salopetă, Cască, Antifoane, Vestă).", key="eip_check")
        
        if st.session_state.eip_check:
            with st.form("test_9"):
                scor = 0
                for i, q in enumerate(INTREBARI_9):
                    r = st.radio(q['q'], q['options'], key=f"q_{i}")
                    if r == q['a']: scor += 1
                
                if st.form_submit_button("Trimite Testul"):
                    procent = (scor / len(INTREBARI_9)) * 100
                    if procent >= 90:
                        nou = {'Data': datetime.now().strftime("%d-%m-%Y"), 'Nume': nume, 'Rol': ", ".join(ECHIPA[nume]), 'Scor': f"{procent:.0f}%", 'Verificat_Manager': False}
                        st.session_state.registru = pd.concat([st.session_state.registru, pd.DataFrame([nou])], ignore_index=True)
                        st.success("✅ Test promovat!")
                    else:
                        st.error(f"❌ Scor: {procent:.0f}%. Trebuie minim 90% (8 din 9 corecte). Recitește normele!")

# --- MODUL MANAGER (ȘEF DEPOZIT) ---
elif rol == "🔍 Manager (Șef Depozit)":
    st.header("🔍 Gestiune Vizitatori și Validare Echpă")
    t1, t2 = st.tabs(["🚶 Registru Vizitatori", "✅ Validare Angajați"])
    
    with t1:
        with st.form("vizitator_nou"):
            nv = st.text_input("Nume Vizitator/Cumpărător")
            scop = st.text_input("Scop vizită (ex: Cumpărare lemn)")
            st.warning("⚠️ OBLIGAȚII: Instruire verbală + Acordare Vestă + Însoțire")
            confirm = st.checkbox("Confirm că am instruit vizitatorul și i-am oferit vesta reflectorizantă.")
            if st.form_submit_button("Înregistrează Vizitator") and nv and confirm:
                st.session_state.registru_vizitatori = pd.concat([st.session_state.registru_vizitatori, pd.DataFrame([{
                    'Data/Ora': datetime.now().strftime("%d-%m-%Y %H:%M"), 'Nume Vizitator': nv, 'Scop': scop, 'EIP_Acordat': "DA", 'Instruit_de': "Sef Depozit"
                }])], ignore_index=True)
                st.success("Vizitator înregistrat.")
        st.dataframe(st.session_state.registru_vizitatori)

    with t2:
        st.dataframe(st.session_state.registru[st.session_state.registru['Verificat_Manager'] == False])
        if st.button("Semnează Verificarea pentru toți"):
            st.session_state.registru['Verificat_Manager'] = True
            st.rerun()

# --- MODUL ADMIN ---
elif rol == "⚙️ Admin":
    st.header("⚙️ Export Rapoarte Audit")
    if st.button("Generează Excel"):
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as w:
            st.session_state.registru.to_excel(w, sheet_name='Angajati', index=False)
            st.session_state.registru_vizitatori.to_excel(w, sheet_name='Vizitatori', index=False)
        st.download_button("📥 Descarcă Raportul", data=buf.getvalue(), file_name="audit_depozit_lemn.xlsx")
