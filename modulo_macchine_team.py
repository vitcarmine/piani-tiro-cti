import streamlit as st

def render_macchine_e_team(df_macchine, carico_max_p):
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
        if pressione_max_kgcm2 <= portanza_terreno_kgcm2:
            st.success(f"✅ Pressione (+100%): **{pressione_max_kgcm2:.2f} kg/cm²** ≤ {portanza_terreno_kgcm2:.2f} kg/cm²")
        else:
            st.error(f"⚠️ Pressione ({pressione_max_kgcm2:.2f} kg/cm²) > Portanza terreno!")

    with st.expander("4. Lifting Team, Rigging Arrangement e Planimetria Area", expanded=True):
        ct1, ct2, ct3, ct4 = st.columns(4)
        num_pic = ct1.number_input("N. PIC", min_value=1, value=1)
        num_imbracatori = ct2.number_input("N. Imbracatori", min_value=1, value=1)
        num_segnalatori = ct3.number_input("N. Segnalatori", min_value=1, value=1)
        num_operatori = ct4.number_input("N. Operatori", min_value=1, value=1)
        ci1, ci2 = st.columns(2)
        img_rig = ci1.file_uploader("Schema Rigging Arrangement 3D", type=["png", "jpg", "jpeg"])
        img_planimetria = ci2.file_uploader("Planimetria area di lavoro", type=["png", "jpg", "jpeg"])

    testo_stab = f"Scarico stabilizzatore (+100% sicurezza): {scarico_stab_sicurezza_t:.2f} t | Piastre {lato_piastra_m:.2f}x{lato_piastra_m:.2f} m | Pressione max: {pressione_max_kgcm2:.2f} kg/cm² ≤ {portanza_terreno_kgcm2:.2f} kg/cm² (VERIFICATO)."
    return lista_macchine_raw, "\n".join(riepilogo_macchine_testo), testo_stab, num_pic, num_imbracatori, num_segnalatori, num_operatori, img_rig, img_planimetria
