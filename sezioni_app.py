import streamlit as st
import sqlite3
import pandas as pd

def mostra_db_attrezzature():
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

def mostra_db_macchine():
    st.title("Database Macchine C.T.I. / C.E.C.A.M.")
    conn = sqlite3.connect("database_lifting_cti_v4.db")
    st.dataframe(pd.read_sql_query("SELECT * FROM macchine", conn), use_container_width=True)
    conn.close()
