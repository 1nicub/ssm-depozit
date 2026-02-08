import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- CONFIGURARE ---
st.set_page_config(page_title="Management Depozit Lemn v4.0", layout="wide")

# --- INITIALIZARE BAZE DE DATE ---
if 'registru' not in st.session_state:
    st.session_state.registru = pd.DataFrame(columns=['Data', 'Nume', 'Scor', 'Incercari_Esuate', 'EIP', 'Status_Sef', 'Data_Semnarii'])
if 'vizitatori' not in st.session_state:
    st.session_state.vizitatori = pd.DataFrame(columns=['Data/Ora', 'Vizitator', 'Scop', 'Instruit', 'Confirmare_Asumata'])
if 'contor_esecuri' not in st.session_state:
    st.session_state.contor_esecuri = {}

# --- INTREBARI TEST (9 INTREBARI) ---
INTREBARI = [
    # SSM & TEHNIC
    {"q": "Care este inaltimea maxima de stivuire a paletilor?", "a": "2 paleti", "opt": ["2 paleti", "3 paleti", "Fara limita"]},
    {"q": "Ce este strict interzis la despicatorul TVS40?", "a": "Deblocarea manuala in timpul miscarii", "opt": ["Curatarea dupa tura", "Deblocarea manuala in timpul miscarii", "Ungerea saptamanala"]},
    {"q": "Ce EIP este obligatoriu la operarea instalatiei Pinosa?", "a": "Bocanci, Casca, Antifoane si Vesta", "opt": ["Doar vesta", "Bocanci si manusi", "Bocanci, Casca, Antifoane si Vesta"]},
    {"q": "Cum se face alimentarea instalatiei Pinosa CPE 1300?", "a": "Doar cu incarcatorul frontal", "opt": ["Manual", "Doar cu incarcatorul frontal", "Cu banda externa"]},
    {"q": "Care este regula principala SU (Legea 307) in depozit?", "a": "Mentinerea culoarelor libere pentru pompieri", "opt": ["Stivuirea cat mai inalta", "Mentinerea culoarelor libere pentru pompieri", "Depozitarea bustenilor la poarta"]},
    # PRIM AJUTOR
    {"q": "In caz de taietura severa cu sangerare abundenta, care este prima masura?", "a": "Aplicarea unui pansament compresiv pe rana", "opt": ["Spalarea ranii cu multa apa", "Aplicarea unui pansament compresiv pe rana", "Administrarea de calmante"]},
    {"q": "Cum procedati in cazul unei arsuri cauzate de o suprafata incinsa a utilajului?", "a": "Racirea zonei cu apa rece minim 10-15 minute", "opt": ["Aplicarea de ulei sau grasime", "Racirea zonei cu apa rece minim 10-15 minute", "Spargerea imediata a veziculelor (basicilor)"]},
    # PROTECTIE CIVILA / DEZASTRE
    {"q": "Ce faceti imediat daca auziti sirena de alarmare 'Alarma la Dezastre' (5 sunete)?", "a": "Intrerupeti lucrul si urmati planul de evacuare", "opt": ["Continuati lucrul pana la noi instructiuni", "Sunati familia", "Intrerupeti lucrul si urmati planul de evacuare"]},
    {"q": "In caz de incendiu major care nu poate fi stapanit, care este prioritatea?", "a": "Evacuarea imediata a personalului", "opt": ["Salvarea bustenilor depozitati", "Evacuarea imediata a personalului", "Mutarea utilajului POSCH"]}
]

# --- NAVIGARE ---
st.sidebar.title("🪓 Control Depozit")
rol = st.sidebar.radio("Acces Secțiune:", ["👤 Lucrător", "🔍 Șef Depozit", "⚙️ Admin"])

# --- 1. MODUL LUCRĂTOR ---
if rol == "👤 Lucrător":
    st.header("📋 Test Complet: SSM, SU, Prim Ajutor & Protectie Civila")
    nume = st.selectbox("Selectează numele tău:", ["---", "Operator 1", "Operator 2", "Sef Depozit"])
    
    if nume != "---":
        if nume not in st.session_state.contor_esecuri:
            st.session_state.contor_esecuri[nume] = 0
            
        st.warning(f"⚠️ Tentative esuate pana in prezent: {st.session_state.contor_esecuri[nume]}")
        eip_ok = st.checkbox("Confirm purtarea EIP complet (Bocanci, Casca, Antifoane, Vesta)")
        
        with st.form("test_complet"):
            raspunsuri_utilizator = []
            for i, item in enumerate(INTREBARI):
                r = st.radio(f"{i+1}. {item['q']}", item['opt'], key=f"q_{i}")
                raspunsuri_utilizator.append(r)
            
            if st.form_submit_button("Trimite Testul"):
                scor_total = sum(1 for i, r in enumerate(raspunsuri_utilizator) if r == INTREBARI[i]['a'])
                
                if scor_total == len(INTREBARI) and eip_ok:
                    nou = {
                        'Data': datetime.now().strftime("%d-%m-%Y"),
                        'Nume': nume, 'Scor': f"{scor_total}/{len(INTREBARI)}", 
                        'Incercari_Esuate': st.session_state.contor_esecuri[nume],
                        'EIP': "DA", 'Status_Sef': "Așteaptă...", 'Data_Semnarii': "-"
                    }
                    st.session_state.registru = pd.concat([st.session_state.registru, pd.DataFrame([nou])], ignore_index=True)
                    st.balloons()
                    st.success(f"✅ Admis! Ai raspuns corect la toate cele {len(INTREBARI)} intrebari.")
                    st.session_state.contor_esecuri[nume] = 0 
                else:
                    st.session_state.contor_esecuri[nume] += 1
                    st.error(f"❌ Respins! Scor: {scor_total}/{len(INTREBARI)}. Trebuie sa raspunzi corect la TOATE intrebarile.")

# --- 2. MODUL ȘEF DEPOZIT ---
elif rol == "🔍 Șef Depozit":
    st.header("🔍 Control Operativ")
    tab1, tab2 = st.tabs(["✍️ Semnare Instruiri", "🚶 Vizitatori"])
    
    with tab1:
        st.subheader("Instruiri noi spre validare")
        neconfirmate = st.session_state.registru[st.session_state.registru['Status_Sef'] == "Așteaptă..."]
        if not neconfirmate.empty:
            st.dataframe(neconfirmate)
            if st.button("✍️ Valideaza si Semneaza digital"):
                st.session_state.registru.loc[st.session_state.registru['Status_Sef'] == "Așteaptă...", 'Data_Semnarii'] = datetime.now().strftime("%d-%m-%Y %H:%M")
                st.session_state.registru.loc[st.session_state.registru['Status_Sef'] == "Așteaptă...", 'Status_Sef'] = "VALIDAT: Sef Depozit"
                st.rerun()
        else:
            st.info("Nicio instruire noua.")

    with tab2:
        st.subheader("🚶 Gestiune Vizitatori")
        with st.form("viz"):
            v_nume = st.text_input("Nume Vizitator")
            scop = st.text_input("Scop vizita")
            st.markdown("---")
            st.write("**Instruire Vizitator:** Confirm ca am luat la cunostinta pericolele din depozit si voi respecta intocmai indicatiile insotitorului.")
            conf_v = st.checkbox("CONFIRMARE VIZITATOR")
            
            if st.form_submit_button("Inregistreaza"):
                if v_nume and conf_v:
                    nv = {'Data/Ora': datetime.now().strftime("%d-%m-%Y %H:%M"), 'Vizitator': v_nume, 'Scop': scop, 'Instruit': "Sef Depozit", 'Confirmare_Asumata': "DA"}
                    st.session_state.vizitatori = pd.concat([st.session_state.vizitatori, pd.DataFrame([nv])], ignore_index=True)
                    st.success("Vizitator salvat.")
        st.dataframe(st.session_state.vizitatori)

# --- 3. MODUL ADMIN ---
elif rol == "⚙️ Admin":
    st.header("⚙️ Export Audit")
    st.dataframe(st.session_state.registru)
    if not st.session_state.registru.empty:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='openpyxl') as writer:
            st.session_state.registru.to_excel(writer, index=False, sheet_name='Instruiri')
            st.session_state.vizitatori.to_excel(writer, index=False, sheet_name='Vizitatori')
        st.download_button("📥 Descarca Raport Complet", data=buf.getvalue(), file_name="audit_ssm_su_depozit.xlsx")
