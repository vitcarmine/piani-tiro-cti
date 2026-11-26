from db_macchine import MACCHINE_INIZIALI
from db_smape_1 import SMAPE_1
from db_smape_2 import SMAPE_2
from db_dajan import ATTREZZATURE_DAJAN

ATTREZZATURE_ENI = [
    ("ENI", "SPOOL LINEA POMPE V580PA501A-B", 150.0, "Forma cilindrica, acciaio, diametro 3'', lunghezza 2 m. Baricentro interno. Non presenti golfari.", "No", "N.2 brache tessili portata 3 t e lunghezza 6 m collegate a strozzo con doppio avvolgimento a circa 25% dalle estremità. Angolo sulla verticale < 45°.")
]

ATTREZZATURE_INIZIALI = ATTREZZATURE_ENI + SMAPE_1 + SMAPE_2 + ATTREZZATURE_DAJAN
