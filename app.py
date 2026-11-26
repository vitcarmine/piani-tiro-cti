import streamlit as st
import sqlite3
import pandas as pd
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import io
from datetime import date

st.set_page_config(page_title="Piani di Tiro - C.T.I. Srl", page_icon="🏗️", layout="wide")

def init_db():
    conn = sqlite3.connect("database_lifting_cti.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS macchine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modello TEXT,
            targa TEXT,
            matricola_inail TEXT,
            portata_max TEXT,
            anno TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS accessori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descrizione TEXT,
            lunghezza TEXT,
            portata_t REAL
        )
    """)
    c.execute("SELECT COUNT(*) FROM macchine")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO macchine (modello, targa, matricola_inail, portata_max, anno) VALUES (?, ?, ?, ?, ?)",
            [
                ("Autogrù Liebherr LTM 1060-3.1", "GX004XT", "2024/2/00306/PZ", "60.000 Kg", "2024"),
                ("Autogrù Gommata LIEBHERR UTM 847 LTM 1100-4.2", "EH036LF", "11/200020/PZ", "100.000 Kg", "2011"),
            ]
        )
    c.execute("SELECT COUNT(*) FROM accessori")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO accessori (descrizione, lunghezza, portata_t) VALUES (?, ?, ?)",
            [
                ("Brache tessili disposte a strozzo", "6 m", 3.0),
                ("Grilli ad lira zincati", "N.A.", 4.75),
            ]
        )
    conn.commit()
    conn.close()

init_db()

st.sidebar.title("🏗️ C.T.I. Srl - Lifting")
pagina = st.sidebar.radio(
    "Seleziona sezione:",
    ["📝 Genera Piano di Tiro", "🚜 Database Autogrù", "⛓️ Database Accessori"]
)

if pagina == "📝 Genera Piano di Tiro":
    st.title("Generatore Automatico Piano di Tiro")
    st.markdown("Compila i dati dell'attività e scarica il documento Word pronto per la firma.")

    conn = sqlite3.connect("database_lifting_cti.db")
    df_macchine = pd.read_sql_query("SELECT * FROM macchine", conn)
    df_accessori = pd.read_sql_query("SELECT * FROM accessori", conn)
    conn.close()

    with st.expander("1. Dati Generali e Frontespizio", expanded=True):
        col1, col2, col3 = st.columns(3)
        protocollo = col1.text_input("Numero Protocollo", value="310/2026")
        data_emissione = col2.text_input("Data Emissione", value=date.today().strftime("%d.%m.%Y"))
        sito = col3.text_input("Sito / Impianto", value="AREA L COVA")

        oggetto_attivita = st.text_input(
            "Oggetto dell'Attività",
            value="Attività di movimentazione in assistenza per smontaggio / montaggio spool linea pompe V580PA501A-B"
        )
        col4, col5, col6 = st.columns(3)
        preparato_da = col4.text_input("Preparato da", value="Ing. Annamaria Palladino")
        approvato_da = col5.text_input("Approvato da", value="Mario CUOZZO")
        data_sopralluogo = col6.text_input("Data Sopralluogo", value="30/10/2026")

        col7, col8 = st.columns(2)
        quota_partenza = col7.text_input("Quota di partenza (m)", value="+8.00")
        quota_arrivo = col8.text_input("Quota di arrivo (m)", value="+1.20")

        criticita = st.text_area(
            "Criticità rilevate in sopralluogo",
            value="Presenza di parti di impianto in pressione durante i tiri.\nLimitata visibilità del gruista sulle aree di lavoro (tiro cieco o parzialmente cieco)."
        )

    with st.expander("2. Scelta Autogrù e Calcolo Portata", expanded=True):
        macchina_scelta = st.selectbox("Seleziona Autogrù dal Database", df_macchine["modello"].tolist())
        dati_m = df_macchine[df_macchine["modello"] == macchina_scelta].iloc[0]
        st.info(f"**Targa:** {dati_m['targa']} | **Matricola INAIL:** {dati_m['matricola_inail']} | **Portata Max:** {dati_m['portata_max']}")

        col_m1, col_m2 = st.columns(2)
        sbraccio = col_m1.number_input("Raggio / Sbraccio di lavoro (m)", min_value=1.0, value=22.0, step=0.5)
        portata_conf = col_m2.number_input("Portata da tabella nella configurazione (t)", min_value=0.1, value=4.70, step=0.1)

    with st.expander("3. Dati Elemento e Calcolo Automatico Carico p*", expanded=True):
        descrizione_elemento = st.text_area(
            "Descrizione tecnica elemento (forma, materiale, dimensioni, baricentro)",
            value="Il tratto di linea da sollevare si presenta di forma cilindrica, materiale acciaio, diametro 3'' e lunghezza 2 m. Baricentro interno alla sagoma. Non sono presenti golfari."
        )
        col_p1, col_p2, col_p3 = st.columns(3)
        peso_el_kg = col_p1.number_input("Peso stimato elemento (kg)", min_value=1.0, value=150.0, step=10.0)
        peso_acc_kg = col_p2.number_input("Peso bozzello + accessori (kg)", min_value=0.0, value=430.0, step=10.0)
        contingenza_perc = col_p3.number_input("Contingenza + Amplif. Dinamica (%)", min_value=0.0, value=15.5, step=0.5)

        carico_tot_kg = (peso_el_kg + peso_acc_kg) * (1 + contingenza_perc / 100.0)
        carico_max_p = round(carico_tot_kg / 1000.0, 2)
        coeff_utilizzo = round((carico_max_p / portata_conf) * 100.0, 2)

        st.metric("Carico Totale di Progetto p* (t)", f"{carico_max_p} t")
        if coeff_utilizzo < 80:
            st.success(f"✅ Coefficiente di utilizzo macchina: **{coeff_utilizzo}%** (Conforme < 80%)")
        else:
            st.error(f"⚠️ Attenzione! Coefficiente di utilizzo macchina: **{coeff_utilizzo}%** (Supera l'80%)")

    with st.expander("4. Imbraco, Accessori e Team", expanded=True):
        acc_selezionati = st.multiselect(
            "Seleziona accessori dal database",
            df_accessori.apply(lambda r: f"{r['descrizione']} - Lungh. {r['lunghezza']} - Portata {r['portata_t']} t", axis=1).tolist()
        )
        descrizione_imbraco = st.text_area(
            "Configurazione di imbraco e angoli",
            value="L’afferraggio avverrà mediante l’utilizzo di n.2 brache tessili di portata 3 t e lunghezza 6 m collegate a strozzo con doppio avvolgimento a circa 25% dalle estremità. Angolo sulla verticale < 45°."
        )
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        num_pic = col_t1.number_input("N. PIC", min_value=1, value=1)
        num_imbracatori = col_t2.number_input("N. Imbracatori", min_value=1, value=1)
        num_segnalatori = col_t3.number_input("N. Segnalatori", min_value=1, value=1)
        num_operatori = col_t4.number_input("N. Operatori Macchina", min_value=1, value=1)

    with st.expander("5. Caricamento Immagini (Diagramma, Foto Sopralluogo, Rigging 3D)", expanded=True):
        img_diag = st.file_uploader("Diagramma di carico cerchiato (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_elem = st.file_uploader("Foto dell'elemento / sopralluogo (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_rig = st.file_uploader("Schema grafico 3D Rigging Arrangement (PNG/JPG)", type=["png", "jpg", "jpeg"])

    if st.button("🚀 GENERA PIANO DI TIRO (.DOCX)", type="primary"):
        try:
            doc = DocxTemplate("template_piano_tiro_CTI.docx")
            elenco_acc_testo = "\n".join([f"- {a}" for a in acc_selezionati]) if acc_selezionati else "- N. 2 brache tessili lunghezza 6 m portata 3.00 t"

            contesto = {
                "protocollo": protocollo,
                "data_emissione": data_emissione,
                "sito": sito,
                "oggetto_attivita": oggetto_attivita,
                "preparato_da": preparato_da,
                "approvato_da": approvato_da,
                "data_sopralluogo": data_sopralluogo,
                "quota_partenza": quota_partenza,
                "quota_arrivo": quota_arrivo,
                "criticita_sopralluogo": criticita,
                "macchina_modello": dati_m["modello"],
                "matricola_inail": dati_m["matricola_inail"],
                "targa": dati_m["targa"],
                "portata_max": dati_m["portata_max"],
                "anno_costruzione": dati_m["anno"],
                "portata_configurazione": f"{portata_conf:.2f}",
                "carico_max_p": f"{carico_max_p:.2f}",
                "coeff_utilizzo": f"{coeff_utilizzo:.2f}",
                "descrizione_elemento": descrizione_elemento,
                "peso_elemento_kg": f"{int(peso_el_kg)}",
                "descrizione_imbraco": descrizione_imbraco,
                "elenco_accessori": elenco_acc_testo,
                "num_pic": num_pic,
                "num_imbracatori": num_imbracatori,
                "num_segnalatori": num_segnalatori,
                "num_operatori": num_operatori,
                "img_diagramma_carico": InlineImage(doc, img_diag, width=Mm(140)) if img_diag else "[Inserire Diagramma di Carico]",
                "img_elemento": InlineImage(doc, img_elem, width=Mm(130)) if img_elem else "[Inserire Foto Elemento]",
                "img_rigging": InlineImage(doc, img_rig, width=Mm(130)) if img_rig else "[Inserire Schema Rigging 3D]",
            }

            doc.render(contesto)
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.success("✅ Piano di Tiro generato con successo!")
            st.download_button(
                label="📥 Scarica Documento Word Compilato",
                data=buffer,
                file_name=f"Piano_di_Tiro_Prot_{protocollo.replace('/', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Errore durante la generazione: {e}. Verifica che il file 'template_piano_tiro_CTI.docx' sia caricato nella stessa cartella.")

elif pagina == "🚜 Database Autogrù":
    st.title("Database Autogrù C.T.I. Srl")
    conn = sqlite3.connect("database_lifting_cti.db")
    df_m = pd.read_sql_query("SELECT * FROM macchine", conn)
    st.dataframe(df_m, use_container_width=True)

    st.subheader("Aggiungi Nuova Autogrù")
    with st.form("form_macchina"):
        c1, c2 = st.columns(2)
        mod = c1.text_input("Modello Macchina (es. Liebherr LTM 1090)")
        targa = c2.text_input("Targa")
        c3, c4, c5 = st.columns(3)
        inail = c3.text_input("Matricola INAIL")
        p_max = c4.text_input("Portata Max (es. 90.000 Kg)")
        anno = c5.text_input("Anno di costruzione")
        if st.form_submit_button("Salva Macchina nel Database"):
            if mod:
                conn.execute("INSERT INTO macchine (modello, targa, matricola_inail, portata_max, anno) VALUES (?, ?, ?, ?, ?)", (mod, targa, inail, p_max, anno))
                conn.commit()
                st.success("Autogrù aggiunta! Ricarica la pagina per vederla in elenco.")
    conn.close()

elif pagina == "⛓️ Database Accessori":
    st.title("Database Accessori di Sollevamento")
    conn = sqlite3.connect("database_lifting_cti.db")
    df_a = pd.read_sql_query("SELECT * FROM accessori", conn)
    st.dataframe(df_a, use_container_width=True)

    st.subheader("Aggiungi Nuovo Accessorio")
    with st.form("form_accessorio"):
        c1, c2, c3 = st.columns(3)
        desc = c1.text_input("Tipologia / Descrizione (es. Braca a 4 bracci in catena)")
        lungh = c2.text_input("Lunghezza (es. 4 m)")
        port = c3.number_input("Portata Nominale WLL (t)", min_value=0.1, value=2.0, step=0.5)
        if st.form_submit_button("Salva Accessorio nel Database"):
            if desc:
                conn.execute("INSERT INTO accessori (descrizione, lunghezza, portata_t) VALUES (?, ?, ?)", (desc, lungh, port))
                conn.commit()
                st.success("Accessorio aggiunto!")
    conn.close()
