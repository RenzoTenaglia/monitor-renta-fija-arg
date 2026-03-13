# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 10:46:41 2026

@author: renzo
"""

from datetime import datetime

# Diccionario maestro con la configuración de cada letra
LETRAS_DATA = {
    # LETRAS TASA FIJA
    'S17A6': {'vto': datetime(2026, 4, 17), 'tipo': 'FIJA', 'nominal': 110.13},
    'S30A6': {'vto': datetime(2026, 4, 30), 'tipo': 'FIJA', 'nominal': 127.49},
    'T30J6': {'vto': datetime(2026, 6, 30), 'tipo': 'FIJA', 'nominal': 144.90},
    'S31L6': {'vto': datetime(2026, 7, 31), 'tipo': 'FIJA', 'nominal': 117.78},
    'S31G6': {'vto': datetime(2026, 8, 31), 'tipo': 'FIJA', 'nominal': 126.96},
    'S30O6': {'vto': datetime(2026, 10, 30), 'tipo': 'FIJA', 'nominal': 135.28},
    'T15E7': {'vto': datetime(2027, 1, 15), 'tipo': 'FIJA', 'nominal': 161.1},
    'T31Y7': {'vto': datetime(2027, 5, 31), 'tipo': 'FIJA', 'nominal': 151.57},
    'T30J7': {'vto': datetime(2027, 6, 30), 'tipo': 'FIJA', 'nominal': 156.18},
    # LETRAS TASA TAMAR (Variable con Spread)
    'TTJ26': {'vto': datetime(2026, 6, 30), 'tipo': 'TAMAR', 'nominal': 164.02, 'spread': 0.0,'piso_tem': 0.0219},
    'S29Y6': {'vto': datetime(2026, 5, 29), 'tipo': 'TAMAR', 'nominal': 131.97,'spread': 2.0},
    'TTS26': {'vto': datetime(2026, 9, 15), 'tipo': 'TAMAR', 'nominal': 175.03, 'spread': 5.,'piso_tem': 0.0217},
    
    # LETRAS DUALES (Pagan el MAX entre Fija o TAMAR)
    'M31G6': {'vto': datetime(2026, 8, 31), 'tipo': 'DUAL', 'nominal': 134.17, 'tasa_ref': 'TAMAR'},
    'TTD26': {'vto': datetime(2026, 12, 15), 'tipo': 'DUAL', 'nominal': 188.99, 'tasa_ref': 'TAMAR','piso_tem': 0.0214},
    'S30N6': {'vto': datetime(2026, 11, 30), 'tipo': 'DUAL', 'nominal': 129.99, 'tasa_ref': 'TAMAR'},
    'T30A7': {'vto': datetime(2026, 12, 15), 'tipo': 'DUAL', 'nominal': 157.34, 'tasa_ref': 'TAMAR'},

}

