import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import io

def render_pulsante_e_word(dati, lista_macchine_raw, lista_attr_raw, img_rig, img_planimetria):
    if st.button("🚀 GENERA MANUALE / PIANO DI TIRO (.DOCX)", type="primary"):
        try:
            doc = DocxTemplate("template_manuale_CTI.docx")

            lista_macchine_word = []
            for m in lista_macchine_raw:
                lista_macchine_word.append({
                    "modello": m["modello"],
                    "matricola_inail": m["matricola_inail"],
                    "targa": m["targa"],
                    "portata_max": m["portata_max"],
                    "anno": m["anno"],
                    "verifica_periodica": m["verifica_periodica"],
                    "note": m["note"],
                    "sbraccio": m["sbraccio"],
                    "braccio": m["braccio"],
                    "portata_eff": m["portata_eff"],
                    "coeff_utilizzo": m["coeff_utilizzo"],
                    "diagramma_std": InlineImage(doc, m["diag_std"], width=Mm(145)) if m["diag_std"] else "",
                    "diagramma_cerchiato": InlineImage(doc, m["diag_cerc"], width=Mm(145)) if m["diag_cerc"] else ""
                })

            lista_attrezzature_word = []
            for item in lista_attr_raw:
                lista_attrezzature_word.append({
                    "company": item["company"],
                    "nome": item["nome"],
                    "peso_kg": item["peso_kg"],
                    "descrizione": item["descrizione"],
                    "accessori_corredo": item["accessori_corredo"],
                    "accessori_dettaglio": item["accessori_dettaglio"],
                    "foto": InlineImage(doc, item["foto_file"], width=Mm(115)) if item["foto_file"] else ""
                })

            contesto = {
                "protocollo": dati["protocollo"],
                "titolo_documento": dati["titolo_documento"],
                "revisione": dati["revisione"],
                "data_emissione": dati["data_emissione"],
                "sito": dati["sito"],
                "oggetto_attivita": dati["oggetto_attivita"],
                "preparato_da": dati["preparato_da"],
                "approvato_da": dati["approvato_da"],
                "data_sopralluogo": dati["data_sopralluogo"],
                "quota_partenza": dati["quota_partenza"],
                "quota_arrivo": dati["quota_arrivo"],
                "codice_lta": dati["codice_lta"],
                "criticita_sopralluogo": dati["criticita"],
                "lista_macchine": lista_macchine_word,
                "lista_attrezzature": lista_attrezzature_word,
                "carico_max_p": dati["carico_max_p"],
                "testo_compatibilita": dati["testo_compatibilita"],
                "testo_stabilizzatori": dati["testo_stabilizzatori"],
                "num_pic": dati["num_pic"],
                "num_imbracatori": dati["num_imbracatori"],
                "num_segnalatori": dati["num_segnalatori"],
                "num_operatori": dati["num_operatori"],
                "img_rigging": InlineImage(doc, img_rig, width=Mm(140)) if img_rig else "",
                "img_planimetria": InlineImage(doc, img_planimetria, width=Mm(155)) if img_planimetria else ""
            }
            doc.render(contesto)
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            st.success("✅ Documento Word generato con schede singole per macchine e attrezzature!")
            st.download_button(
                label="📥 Scarica Documento Word Compilato",
                data=buffer,
                file_name=f"Manuale_Sollevamento_Prot_{dati['protocollo'].replace('/', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.error(f"Errore durante la generazione: {e}")
