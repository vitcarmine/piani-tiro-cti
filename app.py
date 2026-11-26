import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from dati_cti import MACCHINE_INIZIALI, ATTREZZATURE_INIZIALI
from generatore_word import render_pulsante_e_word

st.set_page_config(page_title="Manuale Sollevamenti - C.T.I. Srl", page_icon="🏗️", layout="wide")

def init_db():
    conn = sqlite3.connect("database_lifting_cti_v4.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS macchine (id INTEGER PRIMARY KEY AUTOINCREMENT, modello TEXT, targa TEXT, matricola_inail TEXT, portata_max TEXT, anno TEXT, categoria TEXT, verifica_periodica TEXT, note_specifiche TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS attrezzature (id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT, nome TEXT, peso_kg REAL, descrizione TEXT, accessori_corredo TEXT, accessori_dettaglio TEXT)")
    if len(c.execute("SELECT id FROM macchine").fetchall()) == 0:
        c.executemany("INSERT INTO macchine (modello, targa, matricola_inail, portata_max, anno, categoria, verifica_periodica, note_specifiche) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", MACCHINE_INIZIALI)
    if len(c.execute("SELECT id FROM attrezzature").fetchall()) == 0:
        c.executemany("INSERT INTO attrezzature (company, nome, peso_kg, descrizione, accessori_corredo, accessori_dettaglio) VALUES (?, ?, ?, ?, ?, ?)", ATTREZZATURE_INIZIALI)
    conn.commit()
    conn.close()

init_db()

st.sidebar.title("🏗️ C.T.I. / C.E.C.A.M.")
pagina = st.sidebar.radio("Seleziona sezione:", ["📝 Genera Manuale / Piano di Tiro", "📦 Database Attrezzature (Company)", "🚜 Database Macchine"])

if pagina == "📝 Genera Manuale / Piano di Tiro":
    st.title("Generatore Manuale / Piano di Sollevamento")
    conn = sqlite3.connect("database_lifting_cti_v4.db")
    df_macchine = pd.read_sql_query("SELECT * FROM macchine", conn)
    df_attrezzature = pd.read_sql_query("SELECT * FROM attrezzature", conn)
    conn.close()

    with st.expander("1. Frontespizio, Sito e Dati Generali", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        protocollo = c1.text_input("Numero Protocollo", value="201/2025")
        revisione = c2.text_input("Revisione", value="00")
        data_emissione = c3.text_input("Data Emissione", value=date.today().strftime("%d.%m.%Y"))
        sito = c4.text_input("Sito / Impianto", value="AREA POZZO MA6")
        titolo_doc = st.selectbox("Tipologia Documento", ["MANUALE DEI SOLLEVAMENTI ROUTINARI", "PIANO DI TIRO NON ROUTINARIO COMPLESSO"])
        oggetto_attivita = st.text_input("Oggetto dell'Attività", value="Attività di Solvent Job")
        c5, c6, c7 = st.columns(3)
        preparato_da = c5.text_input("Preparato da", value="Ing. Mastroberti Antonio")
        approvato_da = c6.text_input("Approvato da", value="Mario CUOZZO")
        data_sopralluogo = c7.text_input("Data Sopralluogo", value="01/08/2025")
        c8, c9, c10 = st.columns(3)
        quota_partenza = c8.text_input("Quota partenza (m)", value="Piano campagna")
        quota_arrivo = c9.text_input("Quota arrivo (m)", value="Pianale autocarro / Stokes")
        codice_lta = c10.text_input("Codice LTA", value="")
        criticita = st.text_area("Criticità rilevate in sopralluogo", value="Durante il sopralluogo effettuato, non sono emerse particolari criticità. Si è rilevato un suolo in ghiaia compattata.")

    with st.expander("2. Schede Attrezzature da Sollevare (Selezione Multipla per Company)", expanded=True):
        cc1, cc2 = st.columns(2)
        tutte_comp = sorted(df_attrezzature["company"].unique().tolist())
        company_scelte = cc1.multiselect("Seleziona una o più Company", tutte_comp, default=tutte_comp)
        df_f = df_attrezzature[df_attrezzature["company"].isin(company_scelte)].copy() if len(company_scelte) > 0 else df_attrezzature.copy()
        df_f["etichetta"] = "[" + df_f["company"] + "] " + df_f["nome"]
        attr_scelte = cc2.multiselect("Seleziona le Attrezzature (genera 1 scheda per ciascuna)", df_f["etichetta"].tolist())

        lista_attr_raw = []
        if len(attr_scelte) > 0:
            for i, et in enumerate(attr_scelte):
                riga = df_f[df_f["etichetta"] == et].squeeze()
                st.markdown(f"**Scheda Attrezzatura {i + 1}: `{et}`**")
                ca1, ca2, ca3 = st.columns(3)
                p_singolo = ca1.number_input("Peso (kg)", min_value=1.0, value=float(riga["peso_kg"]), step=10.0, key=f"pa_{i}")
                corr_singolo = ca2.selectbox("Accessori a corredo?", ["Sì", "No"], index=0 if riga["accessori_corredo"] == "Sì" else 1, key=f"ca_{i}")
                foto_singola = ca3.file_uploader("Foto/Disegno dettaglio", type=["png", "jpg", "jpeg"], key=f"fa_{i}")
                desc_singola = st.text_area("Descrizione tecnica (dimensioni, forma, golfari)", value=riga["descrizione"], height=70, key=f"da_{i}")
                acc_singolo = st.text_area("Evidenza numerica accessori e WLL", value=riga["accessori_dettaglio"], height=70, key=f"aa_{i}")
                lista_attr_raw.append({
                    "company": riga["company"], "nome": riga["nome"], "peso_kg": int(p_singolo),
                    "descrizione": desc_singola, "accessori_corredo": corr_singolo,
                    "accessori_dettaglio": acc_singolo, "foto_file": foto_singola
                })
                st.divider()
        else:
            st.info("Seleziona una o più attrezzature dal menu a tendina sopra, oppure compila un elemento manuale:")
            m_comp = st.text_input("Company", value="SMAPE")
            m_nome = st.text_input("Nome Elemento", value="")
            m_peso = st.number_input("Peso (kg)", min_value=1.0, value=500.0, step=10.0)
            m_corr = st.selectbox("Accessori a corredo?", ["Sì", "No"])
            m_desc = st.text_area("Descrizione tecnica", value="")
            m_acc = st.text_area("Accessori associati", value="")
            m_foto = st.file_uploader("Foto/Disegno elemento", type=["png", "jpg", "jpeg"])
            lista_attr_raw.append({
                "company": m_comp, "nome": m_nome, "peso_kg": int(m_peso),
                "descrizione": m_desc, "accessori_corredo": m_corr,
                "accessori_dettaglio": m_acc, "foto_file": m_foto
            })

        modalita_peso = st.radio("Riferimento peso per verifica mezzi:", ["Peso massimo singolo tiro (più gravoso)", "Somma pesi (sollevamento assieme)"], horizontal=True)
        pesi_list = [x["peso_kg"] for x in lista_attr_raw]
        peso_el_kg = max(pesi_list) if "singolo" in modalita_peso else sum(pesi_list)
        cp1, cp2, cp3 = st.columns(3)
        peso_bozzello_kg = cp1.number_input("Peso bozzello (kg)", min_value=0.0, value=400.0, step=10.0)
        peso_acc_kg = cp2.number_input("Peso accessori aggiuntivi (kg)", min_value=0.0, value=50.0, step=5.0)
        contingenza_tot_perc = cp3.number_input("Contingenza (5%) + DAF (10%) [%]", min_value=0.0, value=15.5, step=0.5)
        carico_max_p = round(((peso_el_kg + peso_bozzello_kg + peso_acc_kg) * (1 + contingenza_tot_perc / 100.0)) / 1000.0, 2)
        st.metric("Carico Totale di Progetto p*", f"{carico_max_p:.2f} t")

    with st.expander("3. Schede Macchine di Sollevamento (1 Scheda per Macchina) e Stabilizzatori", expanded=True):
        macchine_scelte = st.multiselect("Seleziona le Macchine di riferimento", df_macchine["modello"].tolist(), default=df_macchine["modello"].head(1).tolist())
        lista_macchine_raw = []
        riepilogo_macchine_testo = []

        for idx, mod_nome in enumerate(macchine_scelte):
            dm = df_macchine[df_macchine["modello"] == mod_nome].squeeze()
            st.markdown(f"**Scheda Macchina 2.{idx + 1}: {mod_nome}** (`{dm['targa']}` | INAIL `{dm['matricola_inail']}`)")
            cm1, cm2, cm3 = st.columns(3)
            sb = cm1.number_input("Sbraccio / Raggio (m)", min_value=0.5, value=8.0, step=0.5, key=f"sb_{idx}")
            br = cm2.number_input("Lunghezza braccio (m)", min_value=1.0, value=24.2, step=0.5, key=f"br_{idx}")
            pt = cm3.number_input("Portata effettiva da tabella (t)", min_value=0.1, value=20.9, step=0.1, key=f"pt_{idx}")
            cu = round((carico_max_p / pt) * 100.0, 2)
            if cu <= 80:
                st.success(f"✅ Coefficiente di utilizzo M{idx + 1}: **{cu:.2f}%** (Conforme ≤ 80%)")
            else:
                st.error(f"⚠️ Coefficiente di utilizzo M{idx + 1}: **{cu:.2f}%** (Supera l'80%)")

            cd1, cd2 = st.columns(2)
            diag_std = cd1.file_uploader("Diagramma di carico standard", type=["png", "jpg", "jpeg"], key=f"ds_{idx}")
            diag_cerc = cd2.file_uploader("Diagramma sbraccio/raggio cerchiato", type=["png", "jpg", "jpeg"], key=f"dc_{idx}")

            lista_macchine_raw.append({
                "modello": dm["modello"], "matricola_inail": dm["matricola_inail"], "targa": dm["targa"],
                "portata_max": dm["portata_max"], "anno": dm["anno"], "verifica_periodica": dm["verifica_periodica"],
                "note": dm["note_specifiche"], "sbraccio": f"{sb:.1f}", "braccio": f"{br:.1f}",
                "portata_eff": f"{pt:.2f}", "coeff_utilizzo": f"{cu:.2f}",
                "diag_std": diag_std, "diag_cerc": diag_cerc
            })
            riepilogo_macchine_testo.append(f"- {mod_nome}: sbraccio {sb:.1f} m, braccio {br:.1f} m, portata {pt:.2f} t, carico p* {carico_max_p:.2f} t (Cu = {cu:.2f}%).")
            st.divider()

        cs1, cs2, cs3 = st.columns(3)
        scarico_stab_base_t = cs1.number_input("Carico singolo stabilizzatore (t)", min_value=0.0, value=12.0, step=0.5)
        lato_piastra_m = cs2.number_input("Lato piastra (m)", min_value=0.2, value=0.80, step=0.1)
        portanza_terreno_kgcm2 = cs3.number_input("Portanza terreno (kg/cm²)", min_value=0.5, value=4.00, step=0.25)
        scarico_stab_sicurezza_t = scarico_stab_base_t * 2.0
        pressione_max_kgcm2 = round((scarico_stab_sicurezza_t * 1000.0) / ((lato_piastra_m * 100.0) ** 2), 2)
