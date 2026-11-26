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
                ("Autogru Liebherr LTM 1060-3.1", "GX004XT", "2024/2/00306/PZ", "60.000 Kg", "2024"),
                ("Autogrù Gommata LIEBHERR UTM 847 LTM 1100-4.2", "EH036LF", "11/200020/PZ", "100.000 Kg", "2011"),
            ]
        )
    c.execute("SELECT COUNT(*) FROM accessori")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO accessori (descrizione, lunghezza, portata_t) VALUES (?, ?, ?)",
            [
                ("Brache tessili disposte a strozzo (doppio avvolgimento)", "6 m", 3.0),
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
    ["📝 Genera Piano di Tiro", "🚜 Database Autogrù", "⛓️ Database Accessori"]
)

if pagina == "📝 Genera Piano di Tiro":
    st.title("Generatore Automatico Piano di Tiro Non Routinario Complesso")
    st.markdown("Compila le sezioni seguenti per generare il documento **C.T.I. Srl** completo di tutti i calcoli e verifiche.")

    conn = sqlite3.connect("database_lifting_cti.db")
    df_macchine = pd.read_sql_query("SELECT * FROM macchine", conn)
    df_accessori = pd.read_sql_query("SELECT * FROM accessori", conn)
    conn.close()

    with st.expander("1. Frontespizio e Dati Generali (Sez. 1)", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        protocollo = c1.text_input("Numero Protocollo", value="310/2026")
        revisione = c2.text_input("Revisione", value="00")
        data_emissione = c3.text_input("Data Emissione", value=date.today().strftime("%d.%m.%Y"))
        sito = c4.text_input("Sito / Impianto", value="AREA L COVA")

        oggetto_attivita = st.text_input(
            "Oggetto dell'Attività",
            value="Attività di movimentazione in assistenza per smontaggio / montaggio spool linea pompe V580PA501A-B"
        )
        c5, c6, c7, c8 = st.columns(4)
        preparato_da = c5.text_input("Preparato da", value="Ing. Annamaria Palladino")
        approvato_da = c6.text_input("Approvato da", value="Mario CUOZZO")
        data_sopralluogo = c7.text_input("Data Sopralluogo", value="30/10/2026")
        personale_sopralluogo = c8.text_input("Presenti al sopralluogo", value="Personale tecnico C.T.I. e committenza ENI")

        descrizione_modalita = st.text_area(
            "A - Modalità e catena delle responsabilità (PIC)",
            value="L'attività di sollevamento descritta nel presente documento fa riferimento alle operazioni in assistenza per la movimentazione dello spool linea pompe V580PA501A-B. Le responsabilità delle operazioni di lifting saranno in capo alla Person in Charge (PIC), a cui è demandato il compito di coordinare le singole fasi nell'uso delle macchine e del team preposto ai sollevamenti."
        )
        c9, c10 = st.columns(2)
        quota_partenza = c9.text_input("Quota di partenza (m)", value="+8.00 m")
        quota_arrivo = c10.text_input("Quota di arrivo (m)", value="+1.20 m")
        descrizione_contesto = st.text_area(
            "C - Contesto operativo e quote",
            value=f"Saranno presenti parti di impianto in pressione in interferenza con le attività di sollevamento in oggetto. La movimentazione avverrà da quota {quota_partenza} (ballatoio) fino a {quota_arrivo} (pianale autocarro)."
        )
        criticita = st.text_area(
            "E - Criticità rilevate in sopralluogo e mitigazioni",
            value="Presenza di parti di impianto in pressione durante i tiri.\nLimitata visibilità del gruista sulle aree di lavoro (tiro cieco o parzialmente cieco).\nPer i rischi e le misure di mitigazione si fa riferimento al Risk Assessment allegato."
        )

    with st.expander("2. Autogrù, Portate, Stabilizzatori e Terreno (Sez. 2 e 7)", expanded=True):
        st.subheader("Macchina Principale")
        macchina_scelta = st.selectbox("Seleziona Autogrù Principale", df_macchine["modello"].tolist())
        dati_m = df_macchine[df_macchine["modello"] == macchina_scelta].iloc[0]
        st.info(f"**Targa:** {dati_m['targa']} | **Matricola INAIL:** {dati_m['matricola_inail']} | **Portata Max:** {dati_m['portata_max']} | **Anno:** {dati_m['anno']}")

        cm1, cm2, cm3, cm4 = st.columns(4)
        sbraccio_1 = cm1.number_input("Raggio / Sbraccio (m)", min_value=1.0, value=22.0, step=0.5)
        lunghezza_braccio_1 = cm2.number_input("Lunghezza Braccio (m)", min_value=5.0, value=38.1, step=0.1)
        contrappeso_1 = cm3.number_input("Zavorra / Contrappeso (t)", min_value=0.0, value=12.8, step=0.1)
        portata_conf = cm4.number_input("Portata da diagramma (t)", min_value=0.1, value=4.70, step=0.1)

        usa_macchina_2 = st.checkbox("Includi Seconda Autogrù (Riserva / Alternativa)", value=True)
        if usa_macchina_2:
            st.subheader("Macchina Alternativa / di Riserva")
            idx_def = 1 if len(df_macchine) > 1 else 0
            macchina_2_scelta = st.selectbox("Seleziona Autogrù Alternativa", df_macchine["modello"].tolist(), index=idx_def)
            dati_m2 = df_macchine[df_macchine["modello"] == macchina_2_scelta].iloc[0]
            cm2_1, cm2_2, cm2_3, cm2_4 = st.columns(4)
            sbraccio_2 = cm2_1.number_input("Raggio / Sbraccio M2 (m)", min_value=1.0, value=22.0, step=0.5)
            lunghezza_braccio_2 = cm2_2.number_input("Lunghezza Braccio M2 (m)", min_value=5.0, value=41.2, step=0.1)
            peso_acc_2_kg = cm2_3.number_input("Peso bozzello + acc. M2 (kg)", min_value=0.0, value=530.0, step=10.0)
            portata_conf_2 = cm2_4.number_input("Portata da diagramma M2 (t)", min_value=0.1, value=7.30, step=0.1)

        checklist_doc = st.text_area(
            "Checklist Documentazione Preliminare (Direttiva 2006/42/CE)",
            value="Marcatura CE; Dichiarazione CE di Conformità del mezzo e degli accessori; Manuale uso e manutenzione; Controllo periodico funi/catene; Verifica periodica annuale INAIL; Libretto circolazione/Assicurazione; Certificazione estintori a bordo."
        )

        st.markdown("---")
        st.subheader("📐 Calcolo Scarico Stabilizzatori e Verifica Portanza Terreno")
        cs1, cs2, cs3, cs4 = st.columns(4)
        tipo_terreno = cs1.text_input("Tipologia terreno", value="ghiaia compattata")
        carico_stab_t = cs2.number_input("Carico max singolo stabilizzatore (t)", min_value=0.5, value=18.5, step=0.5)
        lato_piastra_m = cs3.number_input("Lato piastra ripartizione quadrata (m)", min_value=0.2, value=1.20, step=0.1)
        portanza_terreno = cs4.number_input("Portanza ammissibile terreno (kg/cm²)", min_value=0.1, value=2.50, step=0.1)

        # Calcolo con incremento 100% come da nota tecnica CTI
        carico_stab_maggiorato_t = carico_stab_t * 2.0
        area_piastra_cm2 = (lato_piastra_m * 100.0) ** 2
        pressione_terreno_kg_cm2 = round((carico_stab_maggiorato_t * 1000.0) / area_piastra_cm2, 2)
        rapporto_terreno = round((pressione_terreno_kg_cm2 / portanza_terreno) * 100.0, 1)

        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Carico Stabilizzatore (+100% sic.)", f"{carico_stab_maggiorato_t:.2f} t")
        col_res2.metric("Pressione specifica sul terreno", f"{pressione_terreno_kg_cm2:.2f} kg/cm²")
        if pressione_terreno_kg_cm2 <= portanza_terreno:
            col_res3.success(f"✅ VERIFICA TERRENO OK ({rapporto_terreno}% della portanza)")
            esito_terreno_str = f"VERIFICATO ({pressione_terreno_kg_cm2:.2f} kg/cm² <= {portanza_terreno:.2f} kg/cm²)"
        else:
            col_res3.error(f"⚠️ SUPERATA PORTANZA ({rapporto_terreno}%) - Aumentare area piastre!")
            esito_terreno_str = f"NON VERIFICATO - Aumentare piastre ({pressione_terreno_kg_cm2:.2f} kg/cm² > {portanza_terreno:.2f} kg/cm²)"

    with st.expander("3. Elemento da Sollevare e Calcolo Carico p* (Sez. 3)", expanded=True):
        descrizione_elemento = st.text_area(
            "Descrizione tecnica elemento (forma, materiale, dimensioni, baricentro, golfari)",
            value="Il tratto di linea da sollevare si presenta di forma cilindrica, materiale acciaio, diametro 3'' e lunghezza 2 m. Il peso complessivo stimato è di 150 kg. Baricentro interno alla sagoma dell'elemento. Non sono presenti golfari di sollevamento."
        )
        cp1, cp2, cp3, cp4 = st.columns(4)
        peso_el_kg = cp1.number_input("Peso stimato elemento (kg)", min_value=1.0, value=150.0, step=10.0)
        peso_acc_kg = cp2.number_input("Peso bozzello + accessori M1 (kg)", min_value=0.0, value=430.0, step=10.0)
        contingenza_perc = cp3.number_input("Contingenza peso (%)", min_value=0.0, value=5.0, step=0.5)
        amplif_din_perc = cp4.number_input("Amplificazione dinamica (%)", min_value=0.0, value=10.0, step=0.5)

        fattore_tot = (1 + contingenza_perc / 100.0) * (1 + amplif_din_perc / 100.0)
        carico_max_p = round(((peso_el_kg + peso_acc_kg) * fattore_tot) / 1000.0, 2)
        coeff_utilizzo = round((carico_max_p / portata_conf) * 100.0, 2)

        c_met1, c_met2 = st.columns(2)
        c_met1.metric("Carico Totale di Progetto p* (Macchina 1)", f"{carico_max_p:.2f} t")
        if coeff_utilizzo < 80:
            c_met2.success(f"✅ Utilizzo Macchina 1: **{coeff_utilizzo:.2f}%** (< 80%)")
        else:
            c_met2.error(f"⚠️ Utilizzo Macchina 1: **{coeff_utilizzo:.2f}%** (>= 80%)")

        if usa_macchina_2:
            carico_max_p2 = round(((peso_el_kg + peso_acc_2_kg) * fattore_tot) / 1000.0, 2)
            coeff_utilizzo_2 = round((carico_max_p2 / portata_conf_2) * 100.0, 2)
            nota_m2 = f"La portata della macchina {dati_m2['modello']} (sbraccio {sbraccio_2} m, braccio {lunghezza_braccio_2} m) è di {portata_conf_2:.2f} t compatibile con il carico max da sollevare p* {carico_max_p2:.2f} t. Si evidenzia un coefficiente di utilizzo della macchina pari a {coeff_utilizzo_2:.2f}%."
            st.info(f"ℹ️ **Macchina Alternativa:** p* = **{carico_max_p2:.2f} t** | Utilizzo = **{coeff_utilizzo_2:.2f}%**")
        else:
            nota_m2 = ""

        progettazione_sollevamento = st.text_input(
            "Progettazione sollevamento",
            value="Il sollevamento è stato progettato sulla base delle indicazioni fornite dal costruttore, delle buone prassi e delle risultanze derivanti dalla ingegnerizzazione dell'attività e dal sopralluogo effettuato in impianto."
        )
        note_carrello = st.text_input("Modalità infilaggio forche carrello elevatore", value="N.A.")

    with st.expander("4. Imbraco, Accessori, Team e Fasi Operative (Sez. 4, 5, 6, 8, 9)", expanded=True):
        acc_selezionati = st.multiselect(
            "Seleziona accessori dal database",
            df_accessori.apply(lambda r: f"{r['descrizione']} - Lungh. {r['lunghezza']} - Portata {r['portata_t']} t", axis=1).tolist()
        )
        descrizione_imbraco = st.text_area(
            "Configurazione di imbraco e angoli",
            value="L'afferraggio avverrà mediante l'utilizzo di n.2 brache tessili di portata 3 t e lunghezza 6 m collegate a strozzo con doppio avvolgimento all'item a circa 25% della lunghezza totale della tubazione ed a partire dalle due estremità. L'angolo di inclinazione sulla verticale delle due brache è minore di 45°."
        )
        note_pallettizzato = st.text_input("Note materiale pallettizzato / PLE", value="N.A.")

        st.markdown("**Lifting Operation Team**")
        ct1, ct2, ct3, ct4 = st.columns(4)
        num_pic = ct1.number_input("N. PIC", min_value=1, value=1)
        num_imbracatori = ct2.number_input("N. Imbracatori", min_value=1, value=1)
        num_segnalatori = ct3.number_input("N. Segnalatori", min_value=1, value=1)
        num_operatori = ct4.number_input("N. Operatori Macchina", min_value=1, value=1)

        ca1, ca2 = st.columns(2)
        azienda_team = ca1.text_input("Azienda di appartenenza team", value="C.T.I.")
        comunicazioni = ca2.text_input("Metodi di comunicazione", value="Segnaletico/Gestuale e Radio Ricetrasmittente")

        descrizione_fasi = st.text_area(
            "Sez. 6 - Fasi di Imbraco, Sollevamento e Messa in Sicurezza",
            value="Fase di imbraco: aggancio item, messa in tiro a minima altezza per verifica stabilità ed equilibrio.\nFase di sollevamento: conduzione carico tramite funi guida (angolo max 45°) e hands-free tools / push-pull stick. Divieto assoluto di stazionamento sotto il carico.\nFase di messa in sicurezza: posizionamento sulla verticale dell'area di rilascio, scarico completo accessori e sbraco."
        )
        descrizione_area = st.text_area(
            "Sez. 7 - Descrizione area di piazzamento e percorso mezzi",
            value="L'area di manovra risulta pianeggiante (Area L COVA). Posizionamento stabilizzatori evitando sottoservizi. Segregazione perimetrale con catenella bianco-rossa e cartelli ammonitori. Ingresso e uscita mezzi come da planimetria allegata."
        )
        gestione_emergenze = st.text_area(
            "Sez. 8 - Gestione Emergenze e Meteo",
            value="Applicazione Piano di Emergenza Interno (PEI) COVA. In caso di infortunio/incidente sospendere le attività e contattare immediatamente la Sala Controllo al numero 45415. In caso di condizioni meteo avverse (pioggia intensa, nebbia, fulmini, vento forte) applicare la procedura DIME."
        )
        ce1, ce2, ce3 = st.columns(3)
        elenco_allegati = ce1.text_input("Sez. 9 - Elenco Allegati", value="Allegato C; Layout di cantiere (Ingresso/Uscita e Posizionamento mezzi); Risk Assessment.")
        motivo_revisione = ce2.text_input("Motivo revisione", value="Prima emissione")
        codice_lta = ce3.text_input("Codice Documento LTA", value="")

    with st.expander("5. Caricamento Immagini Tecniche", expanded=True):
        ci1, ci2 = st.columns(2)
        img_diag_std_1 = ci1.file_uploader("Diagramma standard Macchina 1 (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_diag = ci2.file_uploader("Diagramma cerchiato Macchina 1 (PNG/JPG)", type=["png", "jpg", "jpeg"])
        ci3, ci4 = st.columns(2)
        img_diag_std_2 = ci3.file_uploader("Diagramma standard Macchina 2 (opzionale)", type=["png", "jpg", "jpeg"])
        img_diag_2 = ci4.file_uploader("Diagramma cerchiato Macchina 2 (opzionale)", type=["png", "jpg", "jpeg"])
        ci5, ci6, ci7 = st.columns(3)
        img_elem = ci5.file_uploader("Foto elemento / sopralluogo (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_rig = ci6.file_uploader("Schema 3D Rigging Arrangement (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_plan = ci7.file_uploader("Planimetria area di lavoro (PNG/JPG)", type=["png", "jpg", "jpeg"])

    if st.button("🚀 GENERA PIANO DI TIRO COMPLETO (.DOCX)", type="primary"):
        try:
            doc = DocxTemplate("template_piano_tiro_CTI.docx")
            elenco_acc_testo = "\n".join([f"- {a}" for a in acc_selezionati]) if acc_selezionati else "- N. 2 brache tessili della lunghezza di 6 m con una portata di 3.00 t."

            verifica_stab_str = (
                f"Terreno di appoggio: {tipo_terreno} (portanza ammissibile {portanza_terreno:.2f} kg/cm²). "
                f"Carico max singolo stabilizzatore: {carico_stab_t:.2f} t. "
                f"A regime di sicurezza (+100%): {carico_stab_maggiorato_t:.2f} t su piastra {lato_piastra_m:.2f}x{lato_piastra_m:.2f} m. "
                f"Pressione esercitata sul terreno: {pressione_terreno_kg_cm2:.2f} kg/cm² -> Esito: {esito_terreno_str}."
            )

            contesto = {
                "protocollo": protocollo,
                "revisione": revisione,
                "data_emissione": data_emissione,
                "sito": sito,
                "oggetto_attivita": oggetto_attivita,
                "preparato_da": preparato_da,
                "approvato_da": approvato_da,
                "descrizione_modalita_responsabilita": descrizione_modalita,
                "descrizione_contesto_quote": descrizione_contesto,
                "data_sopralluogo": data_sopralluogo,
                "personale_sopralluogo": personale_sopralluogo,
                "criticita_sopralluogo": criticita,
                "tipo_terreno": tipo_terreno,
                "contingenza_perc": f"{contingenza_perc:.0f}",
                "amplificazione_dinamica_perc": f"{amplif_din_perc:.0f}",
                "macchina_modello": dati_m["modello"],
                "matricola_inail": dati_m["matricola_inail"],
                "targa": dati_m["targa"],
                "portata_max": dati_m["portata_max"],
                "anno_costruzione": dati_m["anno"],
                "checklist_documenti": checklist_doc,
                "macchina_2_modello": dati_m2["modello"] if usa_macchina_2 else "N.A.",
                "macchina_2_inail": dati_m2["matricola_inail"] if usa_macchina_2 else "N.A.",
                "macchina_2_targa": dati_m2["targa"] if usa_macchina_2 else "N.A.",
                "macchina_2_portata_max": dati_m2["portata_max"] if usa_macchina_2 else "N.A.",
                "macchina_2_anno": dati_m2["anno"] if usa_macchina_2 else "N.A.",
                "descrizione_sintetica_allestimento": descrizione_contesto,
                "sbraccio_1": f"{sbraccio_1:.1f}",
                "lunghezza_braccio_1": f"{lunghezza_braccio_1:.1f}",
                "contrappeso_1": f"{contrappeso_1:.1f}",
                "portata_configurazione": f"{portata_conf:.2f}",
                "carico_max_p": f"{carico_max_p:.2f}",
                "coeff_utilizzo": f"{coeff_utilizzo:.2f}",
                "nota_macchina_2": nota_m2,
                "descrizione_elemento": descrizione_elemento,
                "progettazione_sollevamento": progettazione_sollevamento,
                "note_carrello_elevatore": note_carrello,
                "descrizione_imbraco": descrizione_imbraco,
                "elenco_accessori": elenco_acc_testo,
                "note_pallettizzato": note_pallettizzato,
                "num_pic": num_pic,
                "azienda_pic": azienda_team,
                "num_imbracatori": num_imbracatori,
                "azienda_imbracatori": azienda_team,
                "num_segnalatori": num_segnalatori,
                "azienda_segnalatori": azienda_team,
                "num_operatori": num_operatori,
                "azienda_operatori": azienda_team,
                "metodo_comunicazione_1": "Segnaletico/Gestuale",
                "metodo_comunicazione_2": "Radio Ricetrasmittente",
                "descrizione_fasi_sollevamento": descrizione_fasi,
                "note_ple": "N.A.",
                "descrizione_area_piazzamento": descrizione_area,
                "verifica_stabilizzatori_testo": verifica_stab_str,
                "rischi_interferenziali_percorso": "Area segregata con catenella bianco-rossa. Ingresso/uscita mezzi secondo planimetria allegata. Riferimento al Risk Assessment allegato.",
                "gestione_emergenze": gestione_emergenze,
                "elenco_allegati": elenco_allegati,
                "motivo_revisione": motivo_revisione,
                "codice_lta": codice_lta,
                "img_diagramma_std_1": InlineImage(doc, img_diag_std_1, width=Mm(140)) if img_diag_std_1 else "[Inserire Diagramma Standard Macchina 1]",
                "img_diagramma_std_2": InlineImage(doc, img_diag_std_2, width=Mm(140)) if img_diag_std_2 else "",
                "img_diagramma_carico": InlineImage(doc, img_diag, width=Mm(140)) if img_diag else "[Inserire Diagramma Cerchiato Macchina 1]",
                "img_diagramma_carico_2": InlineImage(doc, img_diag_2, width=Mm(140)) if img_diag_2 else "",
                "img_rigging_allestimento": InlineImage(doc, img_rig, width=Mm(130)) if img_rig else "[Inserire Schema Rigging 3D]",
                "img_planimetria": InlineImage(doc, img_plan, width=Mm(140)) if img_plan else "[Inserire Planimetria Area di Lavoro]",
                "img_elemento": InlineImage(doc, img_elem, width=Mm(130)) if img_elem else "[Inserire Foto Elemento]",
                "img_rigging": InlineImage(doc, img_rig, width=Mm(130)) if img_rig else "[Inserire Schema Rigging 3D]",
            }

            doc.render(contesto)
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.success("✅ Piano di Tiro completo generato con successo!")
            st.download_button(
                label="📥 Scarica Documento Word Compilato",
                data=buffer,
                file_name=f"Piano_di_Tiro_Prot_{protocollo.replace('/', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Errore durante la generazione: {e}")

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
