# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 11:02:04 2026

@author: renzo
"""

from finance_engine_hd import MonitorHD

# 1. Instanciamos el monitor (Plazo 1 = 24hs estándar actual)
monitor = MonitorHD(plazo=1)

# 2. Corremos el proceso automático
monitor.actualizar_datos()

# 3. Resultados finales
monitor.imprimir_tabla()
monitor.graficar_curvas()
