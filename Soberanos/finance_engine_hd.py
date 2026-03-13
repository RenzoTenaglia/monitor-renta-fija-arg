# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 10:54:21 2026

@author: renzo
"""
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import newton
from datetime import datetime
from pandas.tseries.offsets import BusinessDay
# IMPORTAMOS TUS DATOS MODULARIZADOS
from bonos_data import CASH_FLOWS, TICKERS_SOBERANOS, TICKERS_BOPREAL, COUPON_RATES,LAST_PAYMENT_DATE
class BonoHD:
    def __init__(self, ticker, flows, precio_market, u_pago, plazo=1):
        self.ticker = ticker
        self.flows = flows
        self.precio_market = precio_market
        self.u_pago = u_pago  # <--- RECIBE LA FECHA ESPECÍFICA AQUÍ
        
        # Automatización de Liquidación: T+1 (24hs)
        self.fecha_liq = (datetime.now() + BusinessDay(n=plazo)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        # Ejecutamos los cálculos al instanciar
        self.tir, self.md, self.vr, self.ai = self._procesar_metricas()

    def _procesar_metricas(self):
        ff = [f for f in self.flows if f[0] > self.fecha_liq]
        if not ff or self.precio_market <= 0: 
            return 0, 0, 0, 0

        # Valor Residual Actual (Suma de amortizaciones restantes)
        vr = sum([f[2] for f in ff])
        
        # INTERÉS CORRIDO (AI) - Calculado desde el u_pago recibido
        dias_trans = (self.fecha_liq - self.u_pago).days
        # Usamos la renta del próximo cupón (ff[0][1]) prorrateada
        ai = ff[0][1] * (dias_trans / 180) 

        # Motor de TIR (NPV)
        def npv(rate):
            total_v = -self.precio_market
            for f in ff:
                t = (f[0] - self.fecha_liq).days / 360 # Base 360
                total_v += f[3] / (1 + rate)**t 
            return total_v

        try:
            tir_val = newton(npv, 0.15)
            v_p, dur_mac = 0, 0
            for f in ff:
                t = (f[0] - self.fecha_liq).days / 360
                pv_f = f[3] / (1 + tir_val)**t
                v_p += pv_f
                dur_mac += pv_f * t
            md_val = (dur_mac / v_p) / (1 + tir_val)
            return tir_val * 100, md_val, vr, ai
        except Exception as e:
            print(f"Error calculando TIR para {self.ticker}: {e}") 
            return 0, 0, 0, 0

    @property
    def paridad(self):
        vt = self.vr + self.ai
        return (self.precio_market / vt) * 100 if vt > 0 else 0
    
    
class MonitorHD:
    def __init__(self, plazo=1):
        self.plazo = plazo
        self.ccl = 0
        self.df = None
        # Diccionario de referencia para fechas de último pago
        self.FECHAS_PAGO = {
            'SOBERANOS': datetime(2026, 1, 9),
            'BOPREAL_S1': datetime(2025, 10, 31),
            'BOPREAL_S2': datetime(2025, 11, 30),
            'BOPREAL_S3': datetime(2025, 10, 31),
            'AO27_REF': datetime(2026, 2, 28)
        }

    def actualizar_datos(self):
        """Conecta con la API, calcula CCL y crea la base de datos de bonos."""
        try:
            r = requests.get("https://data912.com/live/arg_bonds").json()
            df_api = pd.DataFrame(r)
        except Exception as e:
            return print(f"❌ Error de conexión: {e}")

        # 1. Cálculo del CCL (AL30 ARS / AL30D USD)
        try:
            p_ars = float(df_api[df_api['symbol'] == 'AL30']['c'].values[0])
            p_usd = float(df_api[df_api['symbol'] == 'AL30D']['c'].values[0])
            self.ccl = p_ars / p_usd
        except:
            self.ccl = 1420.0  # Fallback manual si falla la API
            print(f"⚠️ ERROR DE API: Imposible calcular CCL. Usando valor de fallback manual: ${self.ccl}")
        resultados = []
        for ticker, flows in CASH_FLOWS.items():
            try:
                # 2. Obtener precio y dolarizar si es necesario
                row = df_api[df_api['symbol'].str.contains(ticker)].iloc[0]
                p_raw = float(row['c'])
                precio_usd = p_raw / self.ccl if p_raw > 500 else p_raw
                
                # 3. Mapeo de u_pago según el grupo
                if ticker == 'AO27':
                    u_pago = self.FECHAS_PAGO['AO27_REF']
                elif ticker in TICKERS_SOBERANOS:
                    u_pago = self.FECHAS_PAGO['SOBERANOS']
                elif ticker in ['BPOA7', 'BPOB7', 'BPOC7', 'BPOD7']:
                    u_pago = self.FECHAS_PAGO['BOPREAL_S1']
                elif ticker == 'BPY26':
                    u_pago = self.FECHAS_PAGO['BOPREAL_S2']
                else:
                    u_pago = self.FECHAS_PAGO['BOPREAL_S3']

                # 4. INSTANCIACIÓN DE LA CLASE BONO (Usa la clase que ya definiste)
                # Pasamos u_pago para que el cálculo de AI sea exacto
                bono = BonoHD(ticker, flows, precio_usd, u_pago, self.plazo)
                
                if bono.tir != 0:
                    resultados.append({
                        'ticker': bono.ticker,
                        'tir': bono.tir,
                        'dur': bono.md,
                        'paridad': bono.paridad,
                        'vr': bono.vr,
                        'ai': bono.ai,
                        'precio_usd': bono.precio_market
                    })
            except:
                continue

        # Guardamos en un DataFrame ordenado por Duration
        self.df = pd.DataFrame(resultados).sort_values('dur').reset_index(drop=True)

    def imprimir_tabla(self):
        """Muestra el monitor de paridades en consola con formato limpio."""
        if self.df is None: return print("⚠️ No hay datos. Corré actualizar_datos() primero.")
        
        print("\n" + "="*85)
        print(f"📈 MONITOR DE PARIDADES - PLAZO T+{self.plazo} (MEP: ${self.ccl:.2f})")
        print("="*85)
        
        df_show = self.df.copy()
        df_show['TIR'] = df_show['tir'].map("{:.2f}%".format)
        df_show['Paridad'] = df_show['paridad'].map("{:.2f}%".format)
        df_show['MD'] = df_show['dur'].map("{:.2f}".format)
        df_show['Precio'] = df_show['precio_usd'].map("${:.2f}".format)
        
        print(df_show[['ticker', 'TIR', 'MD', 'Paridad', 'Precio']].to_string(index=False))
        print("="*85)

    def graficar_curvas(self):
        if self.df is None: return
        
        sns.set_style("whitegrid")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

        # --- GRÁFICO 1: CURVA DE RENDIMIENTOS (TIR) ---
        # 1. Filtramos outliers para la curva (evitamos que el BPY26 negativo la rompa)
        df_curva = self.df[self.df['tir'] > 0].copy()
        x_pos = np.arange(len(self.df))
        
        # 2. Cálculo de la línea de tendencia (Polinomio grado 3)
        if len(df_curva) > 3:
            # Usamos el índice de los bonos con TIR positiva para el ajuste
            z = np.polyfit(df_curva.index, df_curva['tir'], 3)
            p = np.poly1d(z)
            x_smooth = np.linspace(0, len(self.df)-1, 150)
            ax1.plot(x_smooth, p(x_smooth), color='blue', alpha=0.3, linewidth=3, label='Curva Teórica')

        # 3. Dibujar puntos
        for i, row in self.df.iterrows():
            color = '#e63946' if 'BP' in row['ticker'] or 'AN' in row['ticker'] else '#003049'
            ax1.scatter(i, row['tir'], color=color, s=100, zorder=5)
            ax1.annotate(f"{row['tir']:.1f}%", (i, row['tir']), xytext=(0, 10), 
                         textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(self.df['ticker'], fontweight='bold')
        ax1.set_title(f"Estructura Temporal de Tasas (TIR %) - MEP: ${self.ccl:.2f}", fontsize=14, fontweight='bold')
        ax1.set_ylabel("TIR (%)")
        ax1.set_ylim(min(self.df['tir']) - 2, max(self.df['tir']) + 5)
        ax1.legend()

        # --- GRÁFICO 2: PARIDAD VS DURATION (Se mantiene igual, está flama) ---
        for _, row in self.df.iterrows():
            color = '#e63946' if 'BP' in row['ticker'] or 'AN' in row['ticker'] else '#003049'
            ax2.scatter(row['dur'], row['paridad'], color=color, s=110, zorder=5, alpha=0.8)
            ax2.annotate(row['ticker'], (row['dur'], row['paridad']), xytext=(0, 8), 
                         textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

        ax2.axhline(100, color='red', linestyle='--', alpha=0.5, label="Par (100%)")
        ax2.set_title("Relación Paridad vs. Modified Duration", fontsize=14, fontweight='bold')
        ax2.set_xlabel("Modified Duration (Años)")
        ax2.set_ylabel("Paridad (%)")
        ax2.set_ylim(min(self.df['paridad']) - 5, 110)
        ax2.legend()

        plt.tight_layout()
        plt.show()
