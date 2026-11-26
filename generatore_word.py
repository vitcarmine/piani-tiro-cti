from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import io

def crea_documento_word(dati, img_diag_std, img_diag, img_diag_2, img_elem, img_rig):
    doc = DocxTemplate("template_piano_tiro_CTI.docx")
    contesto = {
        "protocollo": dati["protocollo"],
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
        "macchina_modello": dati["macchina_modello"],
        "matricola_inail": dati["matricola_inail"],
        "targa": dati["targa"],
        "portata_max": dati["portata_max"],
        "anno_costruzione": dati["anno_costruzione"],
        "verifica_periodica": dati["verifica_periodica"],
        "note_macchina": dati["note_macchina"],
        "sbraccio_m": dati["sbraccio_m"],
        "lunghezza_braccio_m": dati["lunghezza_braccio_m"],
        "portata_configurazione": dati["portata_configurazione"],
        "carico_max_p": dati["carico_max_p"],
        "coeff_utilizzo": dati["coeff_utilizzo"],
        "testo_compatibilita": dati["testo_compatibilita"],
        "testo_stabilizzatori": dati["testo_stabilizzatori"],
        "nome_elemento": dati["nome_elemento"],
        "descrizione_elemento": dati["descrizione_elemento"],
        "peso_elemento_kg": dati["peso_elemento_kg"],
        "descrizione_imbraco": dati["descrizione_imbraco"],
        "elenco_accessori": dati["elenco_accessori"],
        "num_pic": dati["num_pic"],
        "num_imbracatori": dati["num_imbracatori"],
        "num_segnalatori": dati["num_segnalatori"],
        "num_operatori": dati["num_operatori"],
        "img_diagramma_std": InlineImage(doc, img_diag_std, width=Mm(140)) if img_diag_std else "",
        "img_diagramma_carico": InlineImage(doc, img_diag, width=Mm(140)) if img_diag else "[Diagramma Macchina 1]",
        "img_diagramma_2": InlineImage(doc, img_diag_2, width=Mm(140)) if img_diag_2 else "",
        "img_elemento": InlineImage(doc, img_elem, width=Mm(130)) if img_elem else "[Foto Elemento]",
        "img_rigging": InlineImage(doc, img_rig, width=Mm(130)) if img_rig else "[Rigging 3D]"
    }
    doc.render(contesto)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
