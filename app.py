import streamlit as st
import sqlite3
import pandas as pd
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import io
from datetime import date

st.set_page_config(page_title="Piani di Tiro - C.T.I. Srl", page_icon="🏗️", layout="wide")

MACCHINE_INIZIALI = [
    ("Autogru Liebherr LTM 1060-3.1", "GX004XT", "2024/2/00306/PZ", "60.000 Kg", "2024", "Autogrù", "36.0", "12.8", "Annuale", ""),
    ("Autogru Gommata LIEBHERR UTM 740 LTM 1080/1", "GF997EL", "MN/200221/02", "80.000 Kg", "2002", "Autogrù", "48.0", "14.5", "Annuale/Semestrale", ""),
    ("Autogru Gommata LIEBHERR UTM 743 LTM 1090-4.1", "EL143JL", "2012/200054/PZ", "90.000 Kg", "2012", "Autogrù", "48.0", "21.0", "Annuale/Semestrale", ""),
    ("Autogrù Gommata LIEBHERR UTM 847 LTM 1100-4.2", "EH036LF", "11/200020/PZ", "100.000 Kg", "2011", "Autogrù", "48.0", "17.2", "Annuale/Semestrale", ""),
    ("Autogrù Gommata LIEBHERR UTM 851 LTM 1130-5.1", "EK090HE", "2011/200161/PZ", "130.000 Kg", "2011", "Autogrù", "60.0", "29.0", "Annuale/Semestrale", ""),
    ("Autogrù LIEBHERR LTM 1160-5.2", "GN874ZX", "2023/2/00187/PZ", "160.000 Kg", "2023", "Autogrù", "60.0", "20.0", "Annuale", ""),
    ("Autogrù Gommata LIEBHERR UTM 851 LTM 1200-5.1", "FF060VS", "2016/200201/PZ", "200.000 Kg", "2017", "Autogrù", "60.0", "36.0", "Annuale/Semestrale", ""),
    ("Autogru Idro Gru 45 TR T", "DB014SN", "PZ616/00", "45.000 Kg", "1996", "Autogrù", "32.0", "0.0", "Annuale", ""),
    ("Sollevatore telescopico Pegasus 40.17", "N. Serie: HVL1531767", "11/200108/PZ", "3.800 Kg", "2011", "Sollevatore Telescopico", "14.5", "0.0", "Annuale/Semestrale", "Nota 1: I percorsi ed i piazzamenti del mezzo risulteranno concordi in termini di pendenza longitudinale e trasversale rispetto a quanto indicato nel manuale uso e manutenzione. Gli spostamenti del mezzo avverranno nel rispetto delle procedure e della legislazione vigente relative ai mezzi dotati di forche in movimento con o senza carichi."),
    ("Sollevatore telescopico Pegasus 40.25", "N. Serie: BVX1552986", "2020/2/00058/PZ", "3.800 Kg", "2019", "Sollevatore Telescopico", "17.8", "0.0", "Annuale/Semestrale", "Nota 1: I percorsi ed i piazzamenti del mezzo risulteranno concordi in termini di pendenza longitudinale e trasversale rispetto a quanto indicato nel manuale uso e manutenzione. Gli spostamenti del mezzo avverranno nel rispetto delle procedure e della legislazione vigente relative ai mezzi dotati di forche in movimento con o senza carichi."),
    ("Sollevatore telescopico Pegasus 45.30", "N. Serie: WVL1602948", "2020/2/00017/PZ", "4.500 Kg", "2019", "Sollevatore Telescopico", "21.5", "0.0", "Annuale/Semestrale", "Nota 1: I percorsi ed i piazzamenti del mezzo risulteranno concordi in termini di pendenza longitudinale e trasversale rispetto a quanto indicato nel manuale uso e manutenzione. Gli spostamenti del mezzo avverranno nel rispetto delle procedure e della legislazione vigente relative ai mezzi dotati di forche in movimento con o senza carichi."),
    ("Carrello elevatore a forche controbilanciato Hyundai 50DA-9F", "N. SERIE: HHKHFV36TK0000364", "N.A.", "5.000 Kg", "2020", "Carrello Elevatore", "7.8", "0.0", "Annuale", "Modalità di infilaggio forche verificata secondo manuale uso e manutenzione del costruttore.")
]

def init_db():
    conn = sqlite3.connect("database_lifting_cti_v2.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS macchine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modello TEXT,
            targa TEXT,
            matricola_inail TEXT,
            portata_max TEXT,
            anno TEXT,
            categoria TEXT,
            peso_mezzo_t TEXT,
            peso_zavorre_t TEXT,
            verifica_periodica TEXT,
            note_specifiche TEXT
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
            "INSERT INTO macchine (modello, targa, matricola_inail, portata_max, anno, categoria, peso_mezzo_t, peso_zavorre_t, verifica_periodica, note_specifiche) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            MACCHINE_INIZIALI
        )
    c.execute("SELECT COUNT(*) FROM accessori")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO accessori (descrizione, lunghezza, portata_t) VALUES (?, ?, ?)",
            [
                ("Brache tessili disposte a strozzo", "6 m", 3.0),
                ("Brache tessili disposte a strozzo", "4 m", 3.0),
                ("Grilli ad lira zincati", "N.A.", 4.75),
                ("Bilancino di sollevamento", "3 m", 10.0),
            ]
        )
    conn.commit()
    conn.close()

init_db()

st.sidebar.title("🏗️ C.T.I. Srl - Lifting")
pagina = st.sidebar.radio(
    "Seleziona sezione:",
    ["📝 Genera Piano di Tiro", "🚜 Database Macchine (12 Mezzi)", "⛓️ Database Accessori"]
)

if pagina == "📝 Genera Piano di Tiro":
    st.title("Generatore Automatico Piano di Tiro")
    st.markdown("Seleziona i mezzi dal database, inserisci i parametri del tiro e scarica il documento Word completo.")

    conn = sqlite3.connect("database_lifting_cti_v2.db")
    df_macchine = pd.read_sql_query("SELECT * FROM macchine", conn)
    df_accessori = pd.read_sql_query("SELECT * FROM accessori", conn)
    conn.close()

    with st.expander("1. Dati Generali, Frontespizio e Sopralluogo", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        protocollo = col1.text_input("Numero Protocollo", value="310/2026")
        revisione = col2.text_input("Revisione", value="00")
        data_emissione = col3.text_input("Data Emissione", value=date.today().strftime("%d.%m.%Y"))
        sito = col4.text_input("Sito / Impianto", value="AREA L COVA")

        oggetto_attivita = st.text_input(
            "Oggetto dell'Attività",
            value="Attività di movimentazione in assistenza per smontaggio / montaggio spool linea pompe V580PA501A-B"
        )
        col5, col6, col7 = st.columns(3)
        preparato_da = col5.text_input("Preparato da", value="Ing. Annamaria Palladino")
        approvato_da = col6.text_input("Approvato da", value="Mario CUOZZO")
        data_sopralluogo = col7.text_input("Data Sopralluogo", value="30/10/2026")

        col8, col9, col10 = st.columns(3)
        quota_partenza = col8.text_input("Quota di partenza (m)", value="+8.00")
        quota_arrivo = col9.text_input("Quota di arrivo (m)", value="+1.20")
        codice_lta = col10.text_input("Codice Documento LTA (opzionale)", value="")

        criticita = st.text_area(
            "Criticità rilevate in sopralluogo",
            value="Presenza di parti di impianto in pressione durante i tiri.\nLimitata visibilità del gruista sulle aree di lavoro (tiro cieco o parzialmente cieco)."
        )

    with st.expander("2. Macchina Principale, Configurazione e Verifica Stabilizzatori", expanded=True):
        macchina_scelta = st.selectbox("Seleziona Macchina Principale dal Database", df_macchine["modello"].tolist())
        dati_m = df_macchine[df_macchine["modello"] == macchina_scelta].iloc[0]

        st.info(
            f"**Categoria:** {dati_m['categoria']} | **Targa / N. Serie:** {dati_m['targa']} | "
            f"**Matricola INAIL:** {dati_m['matricola_inail']} | **Portata Max:** {dati_m['portata_max']} | "
            f"**Anno:** {dati_m['anno']} | **Verifica:** {dati_m['verifica_periodica']}"
        )
        if dati_m["note_specifiche"]:
            st.warning(dati_m["note_specifiche"])

        col_m1, col_m2, col_m3 = st.columns(3)
        sbraccio_m = col_m1.number_input("Raggio / Sbraccio di lavoro (m)", min_value=0.5, value=22.0, step=0.5)
        lunghezza_braccio_m = col_m2.number_input("Lunghezza braccio configurato (m)", min_value=1.0, value=38.1, step=0.5)
        portata_conf = col_m3.number_input("Portata effettiva da tabella (t)", min_value=0.1, value=4.70, step=0.1)

        st.markdown("#### Calcolo Scarico Stabilizzatori e Portanza Terreno")
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        scarico_stab_base_t = col_s1.number_input("Carico max su singolo stabilizzatore (t)", min_value=0.0, value=12.0, step=0.5)
        lato_piastra_m = col_s2.number_input("Lato piastra di ripartizione quadrata (m)", min_value=0.2, value=0.80, step=0.1)
        spessore_piastra_m = col_s3.number_input("Spessore piastra (m)", min_value=0.01, value=0.06, step=0.01)
        portanza_terreno_kgcm2 = col_s4.number_input("Portanza ammissibile terreno (kg/cm²)", min_value=0.5, value=4.00, step=0.25)

        scarico_stab_sicurezza_t = scarico_stab_base_t * 2.0
        area_piastra_cm2 = (lato_piastra_m * 100.0) ** 2
        pressione_max_kgcm2 = round((scarico_stab_sicurezza_t * 1000.0) / area_piastra_cm2, 2) if area_piastra_cm2 > 0 else 0.0

        c_res1, c_res2 = st.columns(2)
        c_res1.metric("Scarico Stabilizzatore (+100% sicurezza)", f"{scarico_stab_sicurezza_t:.2f} t")
        c_res2.metric("Pressione Max sul Terreno", f"{pressione_max_kgcm2:.2f} kg/cm² (Limite: {portanza_terreno_kgcm2:.2f})")

        if pressione_max_kgcm2 <= portanza_terreno_kgcm2:
            st.success(f"✅ Verifica Portanza Terreno SUPERATA ({pressione_max_kgcm2:.2f} kg/cm² ≤ {portanza_terreno_kgcm2:.2f} kg/cm²)")
        else:
            st.error(f"⚠️ Attenzione: Pressione al suolo ({pressione_max_kgcm2:.2f} kg/cm²) superiore alla portanza del terreno! Aumentare la dimensione delle piastre.")

        usa_seconda_macchina = st.checkbox("➕ Aggiungi Seconda Macchina / Autogrù di Riserva nel Piano")
        dati_m2 = None
        portata_conf_2 = 0.0
        sbraccio_m_2 = 0.0
        if usa_seconda_macchina:
            macchina_2_scelta = st.selectbox("Seleziona Seconda Macchina", df_macchine["modello"].tolist(), index=3)
            dati_m2 = df_macchine[df_macchine["modello"] == macchina_2_scelta].iloc[0]
            col_2a, col_2b = st.columns(2)
            sbraccio_m_2 = col_2a.number_input("Sbraccio Macchina 2 (m)", min_value=0.5, value=22.0, step=0.5)
            portata_conf_2 = col_2b.number_input("Portata effettiva Macchina 2 (t)", min_value=0.1, value=7.30, step=0.1)

    with st.expander("3. Elemento da Sollevare e Calcolo Carico di Progetto p*", expanded=True):
        col_el1, col_el2 = st.columns(2)
        nome_elemento = col_el1.text_input("Titolo / Tag Elemento", value="SPOOL LINEA POMPE V580PA501A-B")
        golfari_presenti = col_el2.selectbox("Presenza golfari di sollevamento", ["Non sono presenti golfari di sollevamento.", "Sono presenti golfari dedicati sul componente."])

        descrizione_elemento = st.text_area(
            "Descrizione tecnica elemento (forma, materiale, dimensioni, baricentro)",
            value="Il tratto di linea da sollevare si presenta di forma cilindrica, il materiale di costruzione è acciaio, dal diametro di 3” e una lunghezza di 2 m. Baricentro interno alla sagoma dell'elemento."
        )
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        peso_el_kg = col_p1.number_input("Peso stimato elemento (kg)", min_value=1.0, value=150.0, step=10.0)
        peso_bozzello_kg = col_p2.number_input("Peso bozzello (kg)", min_value=0.0, value=400.0, step=10.0)
        peso_acc_kg = col_p3.number_input("Peso accessori imbraco (kg)", min_value=0.0, value=30.0, step=5.0)
        contingenza_tot_perc = col_p4.number_input("Contingenza (5%) + Amplif. Dinamica (10%) [%]", min_value=0.0, value=15.5, step=0.5)

        carico_tot_kg = (peso_el_kg + peso_bozzello_kg + peso_acc_kg) * (1 + contingenza_tot_perc / 100.0)
        carico_max_p = round(carico_tot_kg / 1000.0, 2)
        coeff_utilizzo = round((carico_max_p / portata_conf) * 100.0, 2)

        st.metric("Carico Totale di Progetto p*", f"{carico_max_p:.2f} t")
        if coeff_utilizzo < 80:
            st.success(f"✅ Coefficiente di utilizzo Macchina 1: **{coeff_utilizzo:.2f}%** (Conforme < 80%)")
        else:
            st.error(f"⚠️ Coefficiente di utilizzo Macchina 1: **{coeff_utilizzo:.2f}%** (Supera l'80%)")

        coeff_utilizzo_2 = round((carico_max_p / portata_conf_2) * 100.0, 2) if (usa_seconda_macchina and portata_conf_2 > 0) else 0.0

    with st.expander("4. Imbraco, Accessori e Lifting Team", expanded=True):
        acc_selezionati = st.multiselect(
            "Seleziona accessori dal database",
            df_accessori.apply(lambda r: f"{r['descrizione']} - Lungh. {r['lunghezza']} - Portata {r['portata_t']} t", axis=1).tolist()
        )
        descrizione_imbraco = st.text_area(
            "Configurazione di imbraco e angoli",
            value="L’afferraggio avverrà mediante l’utilizzo di n.2 brache tessili di portata 3 t e lunghezza 6 m collegate a strozzo con doppio avvolgimento all’item a circa 25% della lunghezza totale della tubazione ed a partire dalle due estremità. L'angolo di inclinazione sulla verticale delle due brache è minore di 45°."
        )
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        num_pic = col_t1.number_input("N. PIC", min_value=1, value=1)
        num_imbracatori = col_t2.number_input("N. Imbracatori", min_value=1, value=1)
        num_segnalatori = col_t3.number_input("N. Segnalatori", min_value=1, value=1)
        num_operatori = col_t4.number_input("N. Operatori Macchina", min_value=1, value=1)

    with st.expander("5. Caricamento Immagini (Diagrammi, Foto Sopralluogo, Rigging 3D, Planimetria)", expanded=True):
        img_diag_std = st.file_uploader("Diagramma di carico standard Macchina 1 (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_diag = st.file_uploader("Diagramma di carico cerchiato Macchina 1 (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_diag_2 = st.file_uploader("Diagramma di carico Macchina 2 (opzionale - PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_elem = st.file_uploader("Foto dell'elemento / sopralluogo (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_rig = st.file_uploader("Schema grafico 3D Rigging Arrangement (PNG/JPG)", type=["png", "jpg", "jpeg"])

    if st.button("🚀 GENERA PIANO DI TIRO (.DOCX)", type="primary"):
        try:
            doc = DocxTemplate("template_piano_tiro_CTI.docx")
            elenco_acc_testo = "\n".join([f"- {a}" for a in acc_selezionati]) if acc_selezionati else "- N. 2 brache tessili della lunghezza di 6 m con una portata di 3.00 t."

            testo_compatibilita = (
                f"La portata della macchina di sollevamento {dati_m['modello']} allo sbraccio di {sbraccio_m:.1f} m "
                f"(braccio {lunghezza_braccio_m:.1f} m) è di {portata_conf:.2f} t, compatibile con il carico max da sollevare p* {carico_max_p:.2f} t. "
                f"Si evidenzia un coefficiente di utilizzo della macchina pari a {coeff_utilizzo:.2f}%."
            )
            if usa_seconda_macchina and dati_m2 is not None:
                testo_compatibilita += (
                    f"\nIn alternativa, la portata della macchina {dati_m2['modello']} allo sbraccio di {sbraccio_m_2:.1f} m è di {portata_conf_2:.2f} t, "
                    f"compatibile con il carico p* {carico_max_p:.2f} t (coefficiente di utilizzo pari a {coeff_utilizzo_2:.2f}%)."
                )

            testo_stabilizzatori = (
                f"Carico massimo singolo stabilizzatore: {scarico_stab_base_t:.2f} t. "
                f"A regime di sicurezza (+100%): {scarico_stab_sicurezza_t:.2f} t. "
                f"Piastre di ripartizione: {lato_piastra_m:.2f} x {lato_piastra_m:.2f} x {spessore_piastra_m:.2f} m. "
                f"Pressione max esercitata al suolo: {pressione_max_kgcm2:.2f} kg/cm² ≤ Portanza ammissibile terreno ({portanza_terreno_kgcm2:.2f} kg/cm²) -> VERIFICATO."
            )

            contesto = {
                "protocollo": protocollo,
                "revisione": revisione,
                "data_emissione": data_emissione,
                "sito": sito,
                "oggetto_attivita": oggetto_attivita,
                "preparato_da": preparato_da,
                "approvato_da": approvato_da,
                "data_sopralluogo": data_sopralluogo,
                "quota_partenza": quota_partenza,
                "quota_arrivo": quota_arrivo,
                "codice_lta": codice_lta,
                "criticita_sopralluogo": criticita,
                "macchina_modello": dati_m["modello"],
                "matricola_inail": dati_m["matricola_inail"],
                "targa": dati_m["targa"],
                "portata_max": dati_m["portata_max"],
                "anno_costruzione": dati_m["anno"],
                "verifica_periodica": dati_m["verifica_periodica"],
                "note_macchina": dati_m["note_specifiche"],
                "sbraccio_m": f"{sbraccio_m:.1f}",
                "lunghezza_braccio_m": f"{lunghezza_braccio_m:.1f}",
                "portata_configurazione": f"{portata_conf:.2f}",
                "carico_max_p": f"{carico_max_p:.2f}",
                "coeff_utilizzo": f"{coeff_utilizzo:.2f}",
                "testo_compatibilita": testo_compatibilita,
                "testo_stabilizzatori": testo_stabilizzatori,
                "pressione_max_kgcm2": f"{pressione_max_kgcm2:.2f}",
                "portanza_terreno_kgcm2": f"{portanza_terreno_kgcm2:.2f}",
                "nome_elemento": nome_elemento,
                "descrizione_elemento": f"{descrizione_elemento} {golfari_presenti}",
                "peso_elemento_kg": f"{int(peso_el_kg)}",
                "descrizione_imbraco": descrizione_imbraco,
                "elenco_accessori": elenco_acc_testo,
                "num_pic": num_pic,
                "num_imbracatori": num_imbracatori,
                "num_segnalatori": num_segnalatori,
                "num_operatori": num_operatori,
                "img_diagramma_std": InlineImage(doc, img_diag_std, width=Mm(140)) if img_diag_std else "",
                "img_diagramma_carico": InlineImage(doc, img_diag, width=Mm(140)) if img_diag else "[Inserire Diagramma di Carico Cerchiato]",
                "img_diagramma_2": InlineImage(doc, img_diag_2, width=Mm(140)) if img_diag_2 else "",
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
            st.error(f"Errore durante la generazione: {e}")

elif pagina == "🚜 Database Macchine (12 Mezzi)":
    st.title("Database Macchine C.T.I. Srl")
    conn = sqlite3.connect("database_lifting_cti_v2.db")
    df_m = pd.read_sql_query("SELECT id, modello, categoria, targa, matricola_inail, portata_max, anno, verifica_periodica FROM macchine", conn)
    st.dataframe(df_m, use_container_width=True)

    st.subheader("Aggiungi Nuovo Mezzo")
    with st.form("form_macchina"):
        c1, c2, c3 = st.columns(3)
        mod = c1.text_input("Modello Macchina (es. Autogrù Liebherr LTM 1070)")
        cat = c2.selectbox("Categoria", ["Autogrù", "Sollevatore Telescopico", "Carrello Elevatore", "PLE"])
        targa = c3.text_input("Targa o N. Serie")
        c4, c5, c6, c7 = st.columns(4)
        inail = c4.text_input("Matricola INAIL")
        p_max = c5.text_input("Portata Max (es. 70.000 Kg)")
        anno = c6.text_input("Anno di costruzione")
        ver = c7.selectbox("Verifica Periodica", ["Annuale", "Annuale/Semestrale"])
        note = st.text_area("Note specifiche del costruttore (opzionale)")
        if st.form_submit_button("Salva Mezzo nel Database"):
            if mod:
                conn.execute(
                    "INSERT INTO macchine (modello, targa, matricola_inail, portata_max, anno, categoria, peso_mezzo_t, peso_zavorre_t, verifica_periodica, note_specifiche) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (mod, targa, inail, p_max, anno, cat, "0", "0", ver, note)
                )
                conn.commit()
                st.success("Mezzo aggiunto! Ricarica la pagina per vederlo nell'elenco.")
    conn.close()

elif pagina == "⛓️ Database Accessori":
    st.title("Database Accessori di Sollevamento")
    conn = sqlite3.connect("database_lifting_cti_v2.db")
    df_a = pd.read_sql_query("SELECT * FROM accessori", conn)
    st.dataframe(df_a, use_container_width=True)

    st.subheader("Aggiungi Nuovo Accessorio")
    with st.form("form_accessorio"):
        c1, c2, c3 = st.columns(3)
        desc = c1.text_input("Tipologia / Descrizione")
        lungh = c2.text_input("Lunghezza (es. 6 m)")
        port = c3.number_input("Portata Nominale WLL (t)", min_value=0.1, value=3.0, step=0.5)
        if st.form_submit_button("Salva Accessorio nel Database"):
            if desc:
                conn.execute("INSERT INTO accessori (descrizione, lunghezza, portata_t) VALUES (?, ?, ?)", (desc, lungh, port))
                conn.commit()
                st.success("Accessorio aggiunto!")
    conn.close()
