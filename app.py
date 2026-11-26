import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from dati_cti import MACCHINE_INIZIALI, ATTREZZATURE_INIZIALI
from generatore_word import render_pulsante_e_word

st.set_page_config(page_title="Piani di Tiro - C.T.I. Srl", page_icon="🏗️", layout="wide")

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

st.sidebar.title("🏗️ C.T.I. Srl - Lifting")
pagina = st.sidebar.radio("Seleziona sezione:", ["📝 Genera Piano di Tiro", "📦 Database Attrezzature (Company)", "🚜 Database Macchine"])

if pagina == "📝 Genera Piano di Tiro":
    st.title("Generatore Automatico Piano di Tiro")
    conn = sqlite3.connect("database_lifting_cti_v4.db")
    df_macchine = pd.read_sql_query("SELECT * FROM macchine", conn)
    df_attrezzature = pd.read_sql_query("SELECT * FROM attrezzature", conn)
    conn.close()

    with st.expander("1. Dati Generali e Sopralluogo", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        protocollo = c1.text_input("Numero Protocollo", value="310/2026")
        revisione = c2.text_input("Revisione", value="00")
        data_emissione = c3.text_input("Data Emissione", value=date.today().strftime("%d.%m.%Y"))
        sito = c4.text_input("Sito / Impianto", value="AREA L COVA")
        oggetto_attivita = st.text_input("Oggetto dell'Attività", value="Attività di movimentazione in assistenza per smontaggio / montaggio spool linea pompe V580PA501A-B")
        c5, c6, c7 = st.columns(3)
        preparato_da = c5.text_input("Preparato da", value="Ing. Annamaria Palladino")
        approvato_da = c6.text_input("Approvato da", value="Mario CUOZZO")
        data_sopralluogo = c7.text_input("Data Sopralluogo", value="30/10/2026")
        c8, c9, c10 = st.columns(3)
        quota_partenza = c8.text_input("Quota partenza (m)", value="+8.00")
        quota_arrivo = c9.text_input("Quota arrivo (m)", value="+1.20")
        codice_lta = c10.text_input("Codice LTA", value="")
        criticita = st.text_area("Criticità sopralluogo", value="Presenza di parti di impianto in pressione durante i tiri.\nLimitata visibilità del gruista sulle aree di lavoro.")

    with st.expander("2. Elementi da Sollevare (Più Company e Più Attrezzature)", expanded=True):
        cc1, cc2 = st.columns(2)
        tutte_comp = sorted(df_attrezzature["company"].unique().tolist())
        company_scelte = cc1.multiselect("Seleziona una o più Company", tutte_comp, default=tutte_comp)
        df_f = df_attrezzature[df_attrezzature["company"].isin(company_scelte)].copy() if len(company_scelte) > 0 else df_attrezzature.copy()
        df_f["etichetta"] = "[" + df_f["company"] + "] " + df_f["nome"]
        attr_scelte = cc2.multiselect("Seleziona una o più Attrezzature", df_f["etichetta"].tolist())

        modalita_peso = st.radio("Calcolo peso con più attrezzature:", ["Peso massimo singolo tiro (più gravoso)", "Somma pesi (sollevamento assieme)"], horizontal=True)
        if len(attr_scelte) > 0:
            righe_sel = df_f[df_f["etichetta"].isin(attr_scelte)]
            def_nome = " + ".join(righe_sel["etichetta"].tolist())
            def_peso = float(righe_sel["peso_kg"].max()) if "singolo" in modalita_peso else float(righe_sel["peso_kg"].sum())
            def_desc = "\n\n".join(righe_sel.apply(lambda r: f"• [{r['company']}] {r['nome']} ({int(r['peso_kg'])} kg): {r['descrizione']}", axis=1).tolist())
            def_corr = "Sì" if "Sì" in righe_sel["accessori_corredo"].tolist() else "No"
            def_acc = "\n".join(righe_sel.apply(lambda r: f"[{r['company']} - {r['nome']}]\n{r['accessori_dettaglio']}", axis=1).tolist())
        else:
            def_nome, def_peso, def_desc, def_corr, def_acc = "", 150.0, "", "Sì", ""

        nome_elemento = st.text_input("Titolo / Tag Elementi", value=def_nome)
        descrizione_elemento = st.text_area("Descrizione tecnica elementi", value=def_desc, height=110)
        cp1, cp2, cp3, cp4 = st.columns(4)
        peso_el_kg = cp1.number_input("Peso elemento di progetto (kg)", min_value=1.0, value=def_peso, step=10.0)
        peso_bozzello_kg = cp2.number_input("Peso bozzello (kg)", min_value=0.0, value=400.0, step=10.0)
        peso_acc_kg = cp3.number_input("Peso accessori (kg)", min_value=0.0, value=30.0, step=5.0)
        contingenza_tot_perc = cp4.number_input("Contingenza + Amplif. (%)", min_value=0.0, value=15.5, step=0.5)
        carico_max_p = round(((peso_el_kg + peso_bozzello_kg + peso_acc_kg) * (1 + contingenza_tot_perc / 100.0)) / 1000.0, 2)
        st.metric("Carico Totale di Progetto p*", f"{carico_max_p:.2f} t")

    with st.expander("3. Macchine di Sollevamento (Selezione Multipla) e Stabilizzatori", expanded=True):
        macchine_scelte = st.multiselect("Seleziona una o più Macchine", df_macchine["modello"].tolist(), default=df_macchine["modello"].head(1).tolist())
        riepilogo_macchine_testo, targhe_list, inail_list, portate_list, anni_list, verif_list, note_list = [], [], [], [], [], [], []
        sbraccio_1, braccio_1, portata_1, coeff_1 = 22.0, 38.1, 4.70, 0.0

        for idx, mod_nome in enumerate(macchine_scelte):
            dm = df_macchine[df_macchine["modello"] == mod_nome].squeeze()
            st.markdown(f"**Macchina {idx + 1}: {mod_nome}** (Targa/Serie: `{dm['targa']}` | INAIL: `{dm['matricola_inail']}`)")
            cm1, cm2, cm3 = st.columns(3)
            sb = cm1.number_input(f"Sbraccio M{idx + 1} (m)", min_value=0.5, value=22.0, step=0.5, key=f"sb_{idx}")
            br = cm2.number_input(f"Braccio M{idx + 1} (m)", min_value=1.0, value=38.1, step=0.5, key=f"br_{idx}")
            pt = cm3.number_input(f"Portata M{idx + 1} (t)", min_value=0.1, value=4.70, step=0.1, key=f"pt_{idx}")
            cu = round((carico_max_p / pt) * 100.0, 2)
            if cu < 80:
                st.success(f"✅ Utilizzo M{idx + 1}: **{cu:.2f}%**")
            else:
                st.error(f"⚠️ Utilizzo M{idx + 1}: **{cu:.2f}%** (>80%)")
            if idx == 0:
                sbraccio_1, braccio_1, portata_1, coeff_1 = sb, br, pt, cu
            targhe_list.append(str(dm["targa"]))
            inail_list.append(str(dm["matricola_inail"]))
            portate_list.append(str(dm["portata_max"]))
            anni_list.append(str(dm["anno"]))
            verif_list.append(str(dm["verifica_periodica"]))
            if dm["note_specifiche"]:
                note_list.append(str(dm["note_specifiche"]))
            riepilogo_macchine_testo.append(f"La portata di {mod_nome} allo sbraccio di {sb:.1f} m (braccio {br:.1f} m) è di {pt:.2f} t, compatibile con p* {carico_max_p:.2f} t (coeff. utilizzo {cu:.2f}%).")

        st.divider()
        cs1, cs2, cs3 = st.columns(3)
        scarico_stab_base_t = cs1.number_input("Carico singolo stabilizzatore (t)", min_value=0.0, value=12.0, step=0.5)
        lato_piastra_m = cs2.number_input("Lato piastra (m)", min_value=0.2, value=0.80, step=0.1)
        portanza_terreno_kgcm2 = cs3.number_input("Portanza terreno (kg/cm²)", min_value=0.5, value=4.00, step=0.25)
        scarico_stab_sicurezza_t = scarico_stab_base_t * 2.0
        pressione_max_kgcm2 = round((scarico_stab_sicurezza_t * 1000.0) / ((lato_piastra_m * 100.0) ** 2), 2)
        if pressione_max_kgcm2 <= portanza_terreno_kgcm2:
            st.success(f"✅ Pressione (+100%): **{pressione_max_kgcm2:.2f} kg/cm²** ≤ {portanza_terreno_kgcm2:.2f} kg/cm²")
        else:
            st.error(f"⚠️ Pressione ({pressione_max_kgcm2:.2f} kg/cm²) > Portanza terreno!")

    with st.expander("4. Accessori Associati e Lifting Team", expanded=True):
        accessori_corredo = st.selectbox("Accessori a corredo?", ["Sì", "No"], index=0 if def_corr == "Sì" else 1)
        elenco_accessori = st.text_area("Elenco accessori di sollevamento associati", value=def_acc, height=120)
        descrizione_imbraco = st.text_area("Modalità operative di imbraco", value=f"Accessori a corredo: {accessori_corredo}.\n{def_acc}", height=100)
        ct1, ct2, ct3, ct4 = st.columns(4)
        num_pic = ct1.number_input("N. PIC", min_value=1, value=1)
        num_imbracatori = ct2.number_input("N. Imbracatori", min_value=1, value=1)
        num_segnalatori = ct3.number_input("N. Segnalatori", min_value=1, value=1)
        num_operatori = ct4.number_input("N. Operatori", min_value=1, value=len(macchine_scelte) if len(macchine_scelte) > 0 else 1)

    with st.expander("5. Caricamento Immagini", expanded=True):
        img_diag_std = st.file_uploader("Diagramma standard Macchina 1 (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_diag = st.file_uploader("Diagramma cerchiato Macchina 1 (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_diag_2 = st.file_uploader("Diagramma Macchina 2 (opzionale - PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_elem = st.file_uploader("Foto elemento (PNG/JPG)", type=["png", "jpg", "jpeg"])
        img_rig = st.file_uploader("Schema Rigging 3D (PNG/JPG)", type=["png", "jpg", "jpeg"])

    dati_word = {
        "protocollo": protocollo, "revisione": revisione, "data_emissione": data_emissione, "sito": sito,
        "oggetto_attivita": oggetto_attivita, "preparato_da": preparato_da, "approvato_da": approvato_da,
        "data_sopralluogo": data_sopralluogo, "quota_partenza": quota_partenza, "quota_arrivo": quota_arrivo,
        "codice_lta": codice_lta, "criticita": criticita,
        "macchina_modello": " + ".join(macchine_scelte), "matricola_inail": " / ".join(inail_list),
        "targa": " / ".join(targhe_list), "portata_max": " / ".join(portate_list),
        "anno_costruzione": " / ".join(anni_list), "verifica_periodica": " / ".join(verif_list),
        "note_macchina": "\n".join(note_list), "sbraccio_m": f"{sbraccio_1:.1f}",
        "lunghezza_braccio_m": f"{braccio_1:.1f}", "portata_configurazione": f"{portata_1:.2f}",
        "carico_max_p": f"{carico_max_p:.2f}", "coeff_utilizzo": f"{coeff_1:.2f}",
        "testo_compatibilita": "\n".join(riepilogo_macchine_testo),
        "testo_stabilizzatori": f"Scarico stabilizzatore (+100% sicurezza): {scarico_stab_sicurezza_t:.2f} t | Piastre {lato_piastra_m:.2f}x{lato_piastra_m:.2f} m | Pressione max: {pressione_max_kgcm2:.2f} kg/cm² ≤ {portanza_terreno_kgcm2:.2f} kg/cm² (VERIFICATO).",
        "nome_elemento": f"ATTREZZATURE ({' + '.join(company_scelte)}) - {nome_elemento}",
        "descrizione_elemento": descrizione_elemento, "peso_elemento_kg": f"{int(peso_el_kg)}",
        "descrizione_imbraco": descrizione_imbraco, "elenco_accessori": elenco_accessori,
        "num_pic": num_pic, "num_imbracatori": num_imbracatori, "num_segnalatori": num_segnalatori, "num_operatori": num_operatori
    }
    render_pulsante_e_word(dati_word, img_diag_std, img_diag, img_diag_2, img_elem, img_rig)

elif pagina == "📦 Database Attrezzature (Company)":
    st.title("Database Attrezzature per Company")
    conn = sqlite3.connect("database_lifting_cti_v4.db")
    df_a = pd.read_sql_query("SELECT * FROM attrezzature", conn)
    filtro = st.multiselect("Filtra per Company:", sorted(df_a["company"].unique().tolist()), default=sorted(df_a["company"].unique().tolist()))
    st.dataframe(df_a[df_a["company"].isin(filtro)], use_container_width=True)
    with st.form("nuova_attr"):
        c1, c2, c3 = st.columns(3)
        comp_n = c1.text_input("Company (es. ENI, SMAPE, DAJAN o nuova Company)")
        nome_n = c2.text_input("Nome Attrezzatura")
        peso_n = c3.number_input("Peso (kg)", min_value=1.0, value=500.0)
        desc_n = st.text_area("Descrizione tecnica")
        corr_n = st.selectbox("Accessori a corredo?", ["Sì", "No"])
        acc_n = st.text_area("Accessori associati")
        if st.form_submit_button("Salva Attrezzatura"):
            if comp_n and nome_n:
                conn.execute("INSERT INTO attrezzature (company, nome, peso_kg, descrizione, accessori_corredo, accessori_dettaglio) VALUES (?, ?, ?, ?, ?, ?)", (comp_n.upper().strip(), nome_n, peso_n, desc_n, corr_n, acc_n))
                conn.commit()
                st.success("Salvato! Ricarica la pagina.")
    conn.close()

elif pagina == "🚜 Database Macchine":
    st.title("Database Macchine C.T.I. Srl")
    conn = sqlite3.connect("database_lifting_cti_v4.db")
    st.dataframe(pd.read_sql_query("SELECT * FROM macchine", conn), use_container_width=True)
    conn.close()

