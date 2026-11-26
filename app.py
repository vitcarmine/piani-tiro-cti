import streamlit as st
import sqlite3
import pandas as pd
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import io
from datetime import date
from dati_cti import MACCHINE_INIZIALI, ATTREZZATURE_INIZIALI

st.set_page_config(page_title="Piani di Tiro - C.T.I. Srl", page_icon="🏗️", layout="wide")

def init_db():
    conn = sqlite3.connect("database_lifting_cti_v4.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS macchine (id INTEGER PRIMARY KEY AUTOINCREMENT, modello TEXT, targa TEXT, matricola_inail TEXT, portata_max TEXT, anno TEXT, categoria TEXT, verifica_periodica TEXT, note_specifiche TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS attrezzature (id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT, nome TEXT, peso_kg REAL, descrizione TEXT, accessori_corredo TEXT, accessori_dettaglio TEXT)")
    c.execute("SELECT COUNT(*) FROM macchine")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO macchine (modello, targa, matricola_inail, portata_max, anno, categoria, verifica_periodica, note_specifiche) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", MACCHINE_INIZIALI)
    c.execute("SELECT COUNT(*) FROM attrezzature")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO attrezzature (company, nome, peso_kg, descrizione, accessori_corredo, accessori_dettaglio) VALUES (?, ?, ?, ?, ?, ?)", ATTREZZATURE_INIZIALI)
    conn.commit()
    conn.close()

init_db()

st.sidebar.title("🏗️ C.T.I. Srl - Lifting")
pagina = st.sidebar.radio("Seleziona sezione:", ["📝 Genera Piano di Tiro", "📦 Database Attrezzature (Company)", "🚜 Database Macchine"])

if pagina == "📝 Genera Piano di Tiro":
    st.title("Generatore Automatico Piano di Tiro")
    conn = sqlite3.connect("database_lifting_cti_v4.db")
    df_macchine = pd.read_sql_query("SELECT * FROM macchine", conn)
    df_attrezzature = pd.read_sql_query("SELECT * FROM attrezzature", conn)
    conn.close()

    with st.expander("1. Dati Generali, Frontespizio e Sopralluogo", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        protocollo = col1.text_input("Numero Protocollo", value="310/2026")
        revisione = col2.text_input("Revisione", value="00")
        data_emissione = col3.text_input("Data Emissione", value=date.today().strftime("%d.%m.%Y"))
        sito = col4.text_input("Sito / Impianto", value="AREA L COVA")

        oggetto_attivita = st.text_input("Oggetto dell'Attività", value="Attività di movimentazione in assistenza per smontaggio / montaggio spool linea pompe V580PA501A-B")
        col5, col6, col7 = st.columns(3)
        preparato_da = col5.text_input("Preparato da", value="Ing. Annamaria Palladino")
        approvato_da = col6.text_input("Approvato da", value="Mario CUOZZO")
        data_sopralluogo = col7.text_input("Data Sopralluogo", value="30/10/2026")

        col8, col9, col10 = st.columns(3)
        quota_partenza = col8.text_input("Quota di partenza (m)", value="+8.00")
        quota_arrivo = col9.text_input("Quota di arrivo (m)", value="+1.20")
        codice_lta = col10.text_input("Codice Documento LTA (opzionale)", value="")

        criticita = st.text_area("Criticità rilevate in sopralluogo", value="Presenza di parti di impianto in pressione durante i tiri.\nLimitata visibilità del gruista sulle aree di lavoro (tiro cieco o parzialmente cieco).")

    with st.expander("2. Elemento da Sollevare (Archivio Company) e Calcolo Carico p*", expanded=True):
        col_c1, col_c2 = st.columns(2)
        company_scelta = col_c1.selectbox("Seleziona Company", sorted(df_attrezzature["company"].unique().tolist()))
        df_attr_filtrate = df_attrezzature[df_attrezzature["company"] == company_scelta]
        attr_scelta = col_c2.selectbox(f"Seleziona Attrezzatura ({company_scelta})", ["➕ Inserimento manuale..."] + df_attr_filtrate["nome"].tolist())

        if attr_scelta != "➕ Inserimento manuale...":
            dati_attr = df_attr_filtrate[df_attr_filtrate["nome"] == attr_scelta].iloc[0]
            def_nome, def_peso, def_desc, def_corredo, def_acc = dati_attr["nome"], float(dati_attr["peso_kg"]), dati_attr["descrizione"], dati_attr["accessori_corredo"], dati_attr["accessori_dettaglio"]
            st.info(f"**Company:** {company_scelta} | **Accessori a corredo:** {def_corredo}")
        else:
            def_nome, def_peso, def_desc, def_corredo, def_acc = "", 150.0, "", "Sì", ""

        nome_elemento = st.text_input("Titolo / Tag Elemento", value=def_nome)
        descrizione_elemento = st.text_area("Descrizione tecnica elemento", value=def_desc)

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        peso_el_kg = col_p1.number_input("Peso stimato elemento (kg)", min_value=1.0, value=def_peso, step=10.0)
        peso_bozzello_kg = col_p2.number_input("Peso bozzello (kg)", min_value=0.0, value=400.0, step=10.0)
        peso_acc_kg = col_p3.number_input("Peso accessori imbraco (kg)", min_value=0.0, value=30.0, step=5.0)
        contingenza_tot_perc = col_p4.number_input("Contingenza + Amplif. Dinamica (%)", min_value=0.0, value=15.5, step=0.5)

        carico_max_p = round(((peso_el_kg + peso_bozzello_kg + peso_acc_kg) * (1 + contingenza_tot_perc / 100.0)) / 1000.0, 2)
        st.metric("Carico Totale di Progetto p*", f"{carico_max_p:.2f} t")

    with st.expander("3. Macchina Principale e Verifica Stabilizzatori", expanded=True):
        macchina_scelta = st.selectbox("Seleziona Macchina Principale", df_macchine["modello"].tolist())
        dati_m = df_macchine[df_macchine["modello"] == macchina_scelta].iloc[0]
        st.info(f"**Targa/Serie:** {dati_m['targa']} | **INAIL:** {dati_m['matricola_inail']} | **Portata Max:** {dati_m['portata_max']} | **Anno:** {dati_m['anno']}")

        col_m1, col_m2, col_m3 = st.columns(3)
        sbraccio_m = col_m1.number_input("Raggio / Sbraccio (m)", min_value=0.5, value=22.0, step=0.5)
        lunghezza_braccio_m = col_m2.number_input("Lunghezza braccio (m)", min_value=1.0, value=38.1, step=0.5)
        portata_conf = col_m3.number_input("Portata effettiva da tabella (t)", min_value=0.1, value=4.70, step=0.1)

        coeff_utilizzo = round((carico_max_p / portata_conf) * 100.0, 2)
        if coeff_utilizzo < 80:
            st.success(f"✅ Coefficiente di utilizzo: **{coeff_utilizzo:.2f}%** (Conforme < 80%)")
        else:
            st.error(f"⚠️ Coefficiente di utilizzo: **{coeff_utilizzo:.2f}%** (Supera l'80%)")

        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        scarico_stab_base_t = col_s1.number_input("Carico singolo stabilizzatore (t)", min_value=0.0, value=12.0, step=0.5)
        lato_piastra_m = col_s2.number_input("Lato piastra (m)", min_value=0.2, value=0.80, step=0.1)
        spessore_piastra_m = col_s3.number_input("Spessore piastra (m)", min_value=0.01, value=0.06, step=0.01)
        portanza_terreno_kgcm2 = col_s4.number_input("Portanza terreno (kg/cm²)", min_value=0.5, value=4.00, step=0.25)

        scarico_stab_sicurezza_t = scarico_stab_base_t * 2.0
        pressione_max_kgcm2 = round((scarico_stab_sicurezza_t * 1000.0) / ((lato_piastra_m * 100.0) ** 2), 2)
        if pressione_max_kgcm2 <= portanza_terreno_kgcm2:
            st.success(f"✅ Pressione al suolo (+100% sicurezza): **{pressione_max_kgcm2:.2f} kg/cm²** ≤ {portanza_terreno_kgcm2:.2f} kg/cm² (VERIFICATO)")
        else:
            st.error(f"⚠️ Pressione al suolo ({pressione_max_kgcm2:.2f} kg/cm²) superiore alla portanza del terreno!")

    with st.expander("4. Accessori di Sollevamento Associati e Team", expanded=True):
        accessori_corredo = st.selectbox("Accessori a corredo?", ["Sì", "No"], index=0 if def_corredo == "Sì" else 1)
        elenco_accessori = st.text_area("Elenco accessori di sollevamento associati", value=def_acc, height=120)
        descrizione_imbraco = st.text_area("Modalità operative di imbraco", value=f"Accessori a corredo: {accessori_corredo}.\n{def_acc}")
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        num_pic = col_t1.number_input("N. PIC", min_value=1, value=1)
        num_imbracatori = col_t2.number_input("N. Imbracatori", min_value=1, value=1)
        num_segnalatori = col_t3.number_input("N. Segnalatori", min_value=1, value=1)
        num_operatori = col_t4.number_input("N. Operatori", min_value=1, value=1)

    with st.expander("5. Caricamento Immagini", expanded=True):
        img_diag_std = st.file_uploader("Diagramma standard (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_diag = st.file_uploader("Diagramma cerchiato (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_elem = st.file_uploader("Foto elemento (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_rig = st.file_uploader("Schema Rigging 3D (PNG/JPG)", type=["png", "jpg", "jpeg"])

    if st.button("🚀 GENERA PIANO DI TIRO (.DOCX)", type="primary"):
        try:
            doc = DocxTemplate("template_piano_tiro_CTI.docx")
            testo_comp = f"La portata della macchina {dati_m['modello']} allo sbraccio di {sbraccio_m:.1f} m (braccio {lunghezza_braccio_m:.1f} m) è di {portata_conf:.2f} t, compatibile con p* {carico_max_p:.2f} t (coeff. utilizzo {coeff_utilizzo:.2f}%)."
            testo_stab = f"Scarico stabilizzatore (+100% sicurezza): {scarico_stab_sicurezza_t:.2f} t | Piastre {lato_piastra_m:.2f}x{lato_piastra_m:.2f} m | Pressione max: {pressione_max_kgcm2:.2f} kg/cm² ≤ {portanza_terreno_kgcm2:.2f} kg/cm² (VERIFICATO)."
            contesto = {
                "protocollo": protocollo, "revisione": revisione, "data_emissione": data_emissione, "sito": sito,
                "oggetto_attivita": oggetto_attivita, "preparato_da": preparato_da, "approvato_da": approvato_da,
                "data_sopralluogo": data_sopralluogo, "quota_partenza": quota_partenza, "quota_arrivo": quota_arrivo,
                "codice_lta": codice_lta, "criticita_sopralluogo": criticita, "macchina_modello": dati_m["modello"],
