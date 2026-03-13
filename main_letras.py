# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 12:03:54 2026

@author: renzo
"""

# -*- coding: utf-8 -*-
from finance_engine_letras import MonitorLetras
from letras_data import LETRAS_DATA
import sys

TOKEN_BCRA = "token acceso api BCRA"

if __name__ == "__main__":
    print("Iniciando Monitor Quant de Renta Fija (AR)...")
    monitor = MonitorLetras(data_dict=LETRAS_DATA, token_bcra=TOKEN_BCRA)
    
    print("Obteniendo precios en vivo de data912...")
    precios_live = monitor.get_precios_mercado_api()
    
    if precios_live:
        # 🚀 CÁLCULO DINÁMICO DEL TIPO DE CAMBIO (Vía AL30/AL30D)
        try:
            p_ars = precios_live['AL30']
            p_usd = precios_live['AL30D']
            mep_market = p_ars / p_usd
            print(f"✅ CCL (AL30/AL30D) calculado: ${mep_market:.2f}")
        except KeyError:
            print("❌ Error crítico: La API no trajo datos de AL30/AL30D. Freno de ejecución.")
            sys.exit()

        # Obtenemos caución y procesamos
        caucion = monitor.get_tasa_descuento()
        print(f"✅ Tasa de Caución aplicada para PCA: {caucion*100:.2f}%\n")
        
        monitor.armar_cuadro(precios_live, mep_actual=mep_market, tasa_desc=caucion)
        monitor.imprimir_tablero()
        
        print("\nLevantando tableros de visualización...")
        monitor.graficar_dashboard_tasas()
        monitor.graficar_dashboard_trading()
        
    else:
        print("❌ Falla general de conexión a la API de precios.")