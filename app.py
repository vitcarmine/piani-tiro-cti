import streamlit as st
import sqlite3
import pandas as pd
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import io
from datetime import date

st.set_page_config(page_title="Piani di Tiro - C.T.I. Srl", page_icon="🏗️", layout="wide")

MACCHINE_INIZIALI = [
    ("Autogru Liebherr LTM 1060-3.1", "GX004XT", "2024/2/00306/PZ", "60.000 Kg", "2024", "Autogrù", "Annuale", ""),
    ("Autogru Gommata LIEBHERR UTM 740 LTM 1080/1", "GF997EL", "MN/200221/02", "80.000 Kg", "2002", "Autogrù", "Annuale/Semestrale", ""),
    ("Autogru Gommata LIEBHERR UTM 743 LTM 1090-4.1", "EL143JL", "2012/200054/PZ", "90.000 Kg", "2012", "Autogrù", "Annuale/Semestrale", ""),
    ("Autogrù Gommata LIEBHERR UTM 847 LTM 1100-4.2", "EH036LF", "11/200020/PZ", "100.000 Kg", "2011", "Autogrù", "Annuale/Semestrale", ""),
    ("Autogrù Gommata LIEBHERR UTM 851 LTM 1130-5.1", "EK090HE", "2011/200161/PZ", "130.000 Kg", "2011", "Autogrù", "Annuale/Semestrale", ""),
    ("Autogrù LIEBHERR LTM 1160-5.2", "GN874ZX", "2023/2/00187/PZ", "160.000 Kg", "2023", "Autogrù", "Annuale", ""),
    ("Autogrù Gommata LIEBHERR UTM 851 LTM 1200-5.1", "FF060VS", "2016/200201/PZ", "200.000 Kg", "2017", "Autogrù", "Annuale/Semestrale", ""),
    ("Autogru Idro Gru 45 TR T", "DB014SN", "PZ616/00", "45.000 Kg", "1996", "Autogrù", "Annuale", ""),
    ("Sollevatore telescopico Pegasus 40.17", "N. Serie: HVL1531767", "11/200108/PZ", "3.800 Kg", "2011", "Sollevatore Telescopico", "Annuale/Semestrale", "Nota 1: I percorsi ed i piazzamenti del mezzo risulteranno concordi in termini di pendenza longitudinale e trasversale rispetto a quanto indicato nel manuale uso e manutenzione."),
    ("Sollevatore telescopico Pegasus 40.25", "N. Serie: BVX1552986", "2020/2/00058/PZ", "3.800 Kg", "2019", "Sollevatore Telescopico", "Annuale/Semestrale", "Nota 1: I percorsi ed i piazzamenti del mezzo risulteranno concordi in termini di pendenza longitudinale e trasversale rispetto a quanto indicato nel manuale uso e manutenzione."),
    ("Sollevatore telescopico Pegasus 45.30", "N. Serie: WVL1602948", "2020/2/00017/PZ", "4.500 Kg", "2019", "Sollevatore Telescopico", "Annuale/Semestrale", "Nota 1: I percorsi ed i piazzamenti del mezzo risulteranno concordi in termini di pendenza longitudinale e trasversale rispetto a quanto indicato nel manuale uso e manutenzione."),
    ("Carrello elevatore a forche controbilanciato Hyundai 50DA-9F", "N. SERIE: HHKHFV36TK0000364", "N.A.", "5.000 Kg", "2020", "Carrello Elevatore", "Annuale", "Modalità di infilaggio forche verificata secondo manuale uso e manutenzione del costruttore.")
]

# DATABASE ATTREZZATURE SUDDIVISO PER COMPANY CON ACCESSORI ASSOCIATI
ATTREZZATURE_INIZIALI = [
    # ENI
    ("ENI", "SPOOL LINEA POMPE V580PA501A-B", 150.0, "Forma cilindrica, acciaio, diametro 3'', lunghezza 2 m. Baricentro interno. Non presenti golfari.", "No", "N.2 brache tessili portata 3 t e lunghezza 6 m collegate a strozzo con doppio avvolgimento a circa 25% dalle estremità. Angolo sulla verticale < 45°."),
    # SMAPE
    ("SMAPE", "STUFFING BOX 3-1/16'' 10Kpsi (Standard/Side-Door)", 360.0, "Forma cilindrica, ferro, dimensioni max 97x60x130 cm, peso max 360 kg. Baricentro centrale ed interno. Non presenti golfari.", "Sì", "- 1 cappellotto di sollevamento con grillo da 8.5 t;\n- 1 braca tessile lunghezza 4 m portata 3 t."),
    ("SMAPE", "STUFFING BOX 3-1/16'' 10Kpsi SIDE-DOOR TANDEM", 300.0, "Forma cilindrica, ferro, dimensioni 40x40x118 cm, peso max 300 kg. Baricentro centrale ed interno. Non presenti golfari.", "Sì", "- 1 cappellotto di sollevamento con grillo da 8.5 t;\n- 1 braca tessile lunghezza 4 m portata 3 t."),
    ("SMAPE", "STUFFING BOX 4-1/16'' 10Kpsi SIDE-DOOR", 500.0, "Forma cilindrica, ferro, dimensioni 45x45x120 cm, peso 500 kg. Baricentro centrale ed interno. Non presenti golfari.", "Sì", "- 1 cappellotto di sollevamento con grillo da 8.5 t;\n- 1 braca tessile lunghezza 4 m portata 3 t."),
    ("SMAPE", "STUFFING BOX 4-1/16'' 10K/15K SIDE-DOOR TANDEM", 500.0, "Forma cilindrica, ferro, dimensioni 42x42x154 cm, peso 500 kg. Baricentro centrale ed interno. Non presenti golfari.", "Sì", "- 1 cappellotto di sollevamento con grillo da 8.5 t;\n- 1 braca tessile lunghezza 4 m portata 3 t."),
    ("SMAPE", "GATE VALVE 2-1/16'' 10Kpsi (Manuale/Pneumatica/Desmac)", 166.0, "Forma cilindrica, metallo, dimensioni max 52,1x45x92,6 cm, peso max 166 kg. Baricentro centrale ed interno. Presenti n. 2 golfari nella parte inferiore.", "No", "- 2 brache tessili lunghezza 4 m portata 3 t;\n- 2 grilli portata 4,75 t."),
    ("SMAPE", "WCSE RISER QUICK UNION CONNECTION 3.06'' e 4.06'' 10K PSI", 1000.0, "Forma cilindrica, ferro, dimensioni assemblato 2000x42x42 cm, peso 1000 kg. Baricentro centrale ed interno. Non presenti golfari.", "Sì", "- 1 cappellotto di sollevamento con grillo da 8.5 t;\n- 1 braca tessile lunghezza 4 m portata 3 t."),
    ("SMAPE", "LFS0001009 Mod.10", 4500.0, "Forma parallelepipeda, ferro, dimensioni 300x245x304 cm, peso 4500 kg. Baricentro interno. Presenti n. 4 golfari nella parte superiore.", "Sì", "- 1 campanella Din WSM1613 Ton 12;\n- 1 tirante fune acciaio diam. 20 mm L 4 m;\n- Complessivo Speciale S8-8 Ton 6,6;\n- Tirante 4 bracci fune acciaio diam. 16 mm L 1,30 m WLL 5,10 t (0-45°);\n- 4 grilli ad omega SWL 6,5 t."),
    ("SMAPE", "QUAD BOP 4-1/16''", 1800.0, "Forma parallelepipeda, ferro, dimensioni 215x50x190 cm, peso max 1800 kg. Baricentro interno. Non presenti golfari.", "Sì", "- 1 cappellotto di sollevamento con grillo da 8.5 t;\n- 1 braca tessile lunghezza 4 m portata 3 t."),
    ("SMAPE", "COMBI BOP 4-1/16''", 1100.0, "Forma parallelepipeda, ferro, peso da 950 a 1100 kg (240x55x185 cm). Baricentro centrale ed interno. Non presenti golfari.", "Sì", "- 1 cappellotto di sollevamento con grillo da 8.5 t;\n- 1 braca tessile lunghezza 4 m portata 3 t."),
    ("SMAPE", "ADAPTER FLANGIA-FLANGIA / QUICK UNION 3.06''-4.06''", 50.0, "Forma cilindrica, ferro, dimensioni 32x32x30 cm, peso 50 kg. Baricentro centrale ed interno. Non presenti golfari.", "Sì", "- 1 cappellotto di sollevamento con grillo da 8.5 t;\n- 1 braca tessile lunghezza 4 m portata 3 t."),
    ("SMAPE", "CT TOWER BASEFRAME (1/2 Base Frame / Con scale e torre)", 16500.0, "Forma parallelepipeda, ferro, fino a 1050x470x775 cm, peso fino a 16500 kg. Baricentro interno. Presenti n. 4 golfari superiori (interasse 3.5x2.0 m).", "Sì", "Doppio sistema identico composto ciascuno da:\n- N.1 anello sospensione CN-2220-8;\n- N.2 tiranti fune acciaio diam 36 mm L 3,4 m WLL 23,50 t (0-90°);\n- N.2 grilli omega WLL 8,5 t."),
    ("SMAPE", "SERBATOIO GASOLIO - ORLANDO 142", 1130.0, "Forma parallelepipeda, acciaio, dimensioni 170x120x135 cm, peso lordo 1130 kg (tara 230 kg). Presenti n. 2 golfari.", "Sì", "- N.1 Campanella DIN 1310-8 5.3 t;\n- N.2 Sling diam 10 mm L 1.5 m WLL 1.81 t (0-90°);\n- N.2 Grilli omega WLL 1.5 t."),
    ("SMAPE", "CISTERNA AZOTO SSA2030834", 11745.0, "Forma parallelepipeda, ferro, dimensioni 472x239x256 cm, peso pieno carico 11745 kg. Presenti n. 4 golfari superiori.", "Sì", "- N.1 Master Link M-18T-10 + Fore Runner diam 36 mm L 2 m + Master Link MT-18T-10-OS;\n- N.4 Sling diam 26 mm L 3.5 m WLL 16,6 t (0-45°);\n- N.4 Grilli omega WLL 8.5 t."),
    ("SMAPE", "POMPA AZOTO UPATSC5194", 14900.0, "Forma parallelepipeda, ferro, dimensioni 524x244x267 cm, peso 14900 kg. Presenti n. 4 golfari superiori.", "No", "- N.1 Quad Assembly HA36QA;\n- N.4 Sling diam 28 mm L 4.1 m WLL 14,90 t DNVGL-2.7.1 (0-45°);\n- N.4 Grilli omega WLL 9.5 t."),
    ("SMAPE", "POMPA AZOTO UPATSO5179", 14900.0, "Forma parallelepipeda, ferro, dimensioni 524x244x257 cm, peso lordo 14900 kg. Presenti n. 4 golfari superiori.", "No", "- N.1 Anello M 2016 10 + tirante diam 34 mm L 1.80 m WLL 15 t + Green Pin G5263 15 t;\n- N.1 Quad Assembly HA36QA + N.4 Sling diam 28 mm L 4 m WLL 14.9 t (0-45°);\n- N.4 Grilli omega WLL 9.5 t."),
    ("SMAPE", "CESTONE RISER CSRM342468", 2000.0, "Forma parallelepipeda, ferro, dimensioni 243x100x240 cm, peso 2000 kg. Presenti n. 2 golfari superiori.", "Sì", "- N.1 Master Link 5,3 t;\n- N.2 Sling diam 12 mm L 2 m Portata 2,56 t (0-45°);\n- N.4 Grilli omega portata 4,75 t."),
    ("SMAPE", "CESTONE AZOTO CSSM251258 / CSSM251232", 2000.0, "Forma parallelepipeda, ferro, dimensioni 241x120x230 cm, peso fino a 2000 kg. Presenti n. 4 golfari superiori.", "Sì", "- N.1 Master Link M-7T-10.OS + Fore Runner diam 24 mm L 1 m + Master Link MT-7T-10.OS;\n- N.4 Sling diam 18 mm L 2 m WLL 2.5 t (0-45°);\n- N.4 Grilli omega WLL 4.75 t."),
    ("SMAPE", "MASSI 7 TON (TCP01 - TCP24)", 7700.0, "Forma parallelepipeda, cemento, dimensioni 200x170x100 cm, peso 7700 kg. Presente n. 1 golfare superiore.", "No", "- N.1 set catene a 2 bracci regolabili con ganci self-locking L 8 m portata 9.5 t."),
    ("SMAPE", "SCALE PER EXTENSION FRAME (Upper/Lower Stair Mod. ODIM)", 500.0, "Forma parallelepipeda, ferro, 600x117x125 cm (500 kg) o 530x117x125 cm (450 kg). Presenti n. 4 golfari interni.", "Sì", "- Anello di sospensione + 2 tiranti acciaio L 2.55 m CNC10 9,4 t + 2 tiranti acciaio L 2.60 m WLL 26.67 kN (0-90°) + 4 grilli SWL 3.25 t."),
    ("SMAPE", "SIDE PLATFORM (JF001/B - JF025/B)", 800.0, "Forma parallelepipeda, ferro, dimensioni 515x174x129 cm, peso 800 kg. Presenti n. 4 golfari interni.", "Sì", "- N.1 master link CNC101B 9.4 t;\n- N.4 funi diam 10 mm (2x2.55m + 2x2.60m) WLL 26.67 kN (0-90°);\n- 4 grilli omega WLL 3.25 t."),
    ("SMAPE", "CISTERNA AZOTO SSA2030830 / SSA2030833", 11745.0, "Forma parallelepipeda, ferro, dimensioni 472x232x256 cm, peso lordo 11745 kg (tara 5262 kg). Presenti 4 golfari superiori.", "Sì", "- Master Link P-6810 19 t + Fore Runner 38 mm L 2 m + Master Link P-6820 19 t;\n- N.4 Sling diam 26 mm L 3 m WLL 16.60 t (0-45°);\n- N.4 Grilli omega WLL 8.5 t."),
