# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Módulo de Monitor de Letras y Boncaps - Arquitectura POO
Calcula TNA, TEA, TEM, Modified Duration, Paridad y Dólar Breakeven.
Genera dashboards visuales para la mesa de operaciones.
"""

import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pandas.tseries.offsets import BusinessDay

# Suprimir advertencias de certificados (útil para la API del BCRA)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MonitorLetras:
    def __init__(self, data_dict, token_bcra):
        """
        Inicializa el motor del monitor.
        :param data_dict: Diccionario estático con los datos maestros de las Letras (vencimiento, tipo, nominal).
        :param token_bcra: Token de autenticación para la API del BCRA.
        """
        self.data_dict = data_dict
        self.token = token_bcra
        self.df_cuadro = None
        # Lista estricta para identificar los instrumentos indexados a tasa variable
        self.tickers_tamar = [ 'TTJ26', 'S29Y6', 'M31G6', 'TTS26', 'TTD26']

    def get_tasa_descuento(self, caucion_manual=None):
        """
        Obtiene la tasa de caución para calcular el Precio Contado Arbitrado (PCA).
        Si no se pasa una manual, va a buscar la proxy a la API del BCRA.
        """
        if caucion_manual is not None:
            return caucion_manual
            
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        url = "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/150"
        try:
            r = requests.get(url, headers=headers, verify=False).json()
            # Toma el último valor de la serie y lo pasa a formato decimal
            return float(r['results'][0]['detalle'][-1]['valor']) / 100
        except Exception as e:
            print(f"⚠️ Error BCRA caución: {e}. Imposible descontar T+1 con precisión.")
            return 0.0 

    def get_precios_mercado_api(self):
        """
        Consume la API de data912 barriendo bonos soberanos y letras (notes).
        Devuelve un diccionario unificado {ticker: precio_ultimo}.
        """
        urls = [
            "https://data912.com/live/arg_bonds",
            "https://data912.com/live/arg_notes"
        ]
        precios = {}
        for url in urls:
            try:
                r = requests.get(url, verify=False)
                if r.status_code == 200:
                    for item in r.json():
                        if 'symbol' in item and 'c' in item:
                            precios[item['symbol']] = float(item['c'])
            except Exception as e:
                print(f"❌ Error conectando a {url}: {e}")
        return precios

    @staticmethod
    def calcular_tasas(precio, vn, dias):
        """
        Motor matemático para Zero Coupons. Devuelve TNA, TEA, TEM y Modified Duration.
        """
        if dias <= 0 or precio <= 0: return 0.0, 0.0, 0.0, 0.0
        rendimiento = (vn / precio)
        tna = (rendimiento - 1) * (365 / dias) * 100
        tea = ((rendimiento) ** (365 / dias) - 1) * 100
        tem = ((rendimiento) ** (30 / dias) - 1) * 100
        md = (dias / 365) / (1 + (tea / 100))
        return tna, tea, tem, md

    def armar_cuadro(self, precios_api, mep_actual, tasa_desc):
        """
        Cruza los datos maestros con los precios en vivo, descuenta el T+1 y genera el DataFrame analítico.
        """
        fecha_liq = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + BusinessDay(n=1)
        filas = []
        
        # Corrección interna de metadata
        if 'T30A7' in self.data_dict:
            self.data_dict['T30A7']['vto'] = datetime(2027, 4, 30)
            
        for ticker, info in self.data_dict.items():
            if ticker not in precios_api: continue
                
            p_24hs = precios_api[ticker]
            vn = info['nominal']
            dias = (info['vto'] - fecha_liq).days
            tipo = info['tipo']
            
            # Cálculo del Precio Contado Arbitrado (PCA) descontando 1 día con la caución
            p_pca = p_24hs / (1 + (tasa_desc * 1 / 365))
            
            # Cálculo de rendimientos sobre el PCA
            tna, tea, tem, md = self.calcular_tasas(p_pca, vn, dias)
            
            # Clasificación de tasas según prospecto
            tna_fija = tna if tipo in ['FIJA', 'DUAL'] else np.nan
            tna_tamar = tna if tipo in ['TAMAR', 'DUAL'] else np.nan
            
            # Dólar implícito y Paridad
            dolar_eq = vn / (p_pca / mep_actual)
            paridad = (p_pca / vn) * 100
            
            filas.append({
                'Especie': ticker, 'Ultimo': p_24hs, 'PCA': p_pca, 
                'TNA_Fija_Num': tna_fija, 'TNA_Tamar_Num': tna_tamar,
                'TEA_Num': tea, 'TEM_Num': tem, 'Vencimiento': info['vto'].strftime('%d/%m/%Y'),
                'Dias': dias, 'MD': md, 'VN': vn, 'Paridad': paridad, 
                'Dolar_Eq': dolar_eq, 'Obs': tipo
            })
            
        self.df_cuadro = pd.DataFrame(filas).sort_values('MD').reset_index(drop=True)
        # Unificamos TNA para el motor de gráficos (evita doble ploteo en los Duales)
        self.df_cuadro['TNA_Plot'] = self.df_cuadro['TNA_Fija_Num'].fillna(self.df_cuadro['TNA_Tamar_Num'])
        return self.df_cuadro

    def imprimir_tablero(self):
        """
        Aplica formato financiero a las columnas y printea el DataFrame en consola.
        """
        if self.df_cuadro is None: return
        df_print = self.df_cuadro.copy()
        
        df_print['Ultimo'] = df_print['Ultimo'].apply(lambda x: f"${x:.3f}")
        df_print['PCA'] = df_print['PCA'].apply(lambda x: f"${x:.3f}")
        df_print['Paridad'] = df_print['Paridad'].apply(lambda x: f"{x:.2f}%")
        df_print['TNA_Fija'] = df_print['TNA_Fija_Num'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "-")
        df_print['TNA_Tamar'] = df_print['TNA_Tamar_Num'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "-")
        df_print['TEA'] = df_print['TEA_Num'].apply(lambda x: f"{x:.2f}%")
        df_print['TEM'] = df_print['TEM_Num'].apply(lambda x: f"{x:.2f}%")
        df_print['MD'] = df_print['MD'].apply(lambda x: f"{x:.2f}")
        df_print['Dolar_Eq'] = df_print['Dolar_Eq'].apply(lambda x: f"${x:.2f}")

        print("\n" + "="*140)
        print(" 📊 TABLERO EN VIVO DE LETRAS Y BONCAPS (CON PCA Y CCL DINÁMICO) ".center(140))
        print("="*140)
        cols = ['Especie', 'Ultimo', 'TNA_Fija', 'TNA_Tamar', 'TEA', 'TEM', 'Vencimiento', 'Dias', 'PCA', 'Paridad', 'MD', 'Dolar_Eq', 'Obs']
        print(df_print[cols].to_string(index=False))

    def _dibujar_curva_tasa(self, ax, col_data, titulo, pre_label, margen_y):
        """
        Helper function: Procesa las regresiones logarítmicas y dibuja los puntos.
        """
        x_pos = np.arange(len(self.df_cuadro))
        
        # 1. Trazado de Curvas Teóricas (Regresiones Logarítmicas)
        for is_tamar, color_line in [(False, '#ffb3b3'), (True, '#a8c8fc')]:
            df_sub = self.df_cuadro[self.df_cuadro['Especie'].isin(self.tickers_tamar)].copy() if is_tamar else self.df_cuadro[~self.df_cuadro['Especie'].isin(self.tickers_tamar)].copy()
            
            if len(df_sub) >= 2:
                # Regresión logarítmica para achatar el tramo largo
                x_fit = np.log(df_sub.index + 1)
                a, b = np.polyfit(x_fit, df_sub[col_data], 1)
                x_smooth = np.linspace(df_sub.index.min() if is_tamar else 0, len(self.df_cuadro)-1, 150)
                ax.plot(x_smooth, (a * np.log(x_smooth + 1)) + b, color=color_line, alpha=0.8, linewidth=3, zorder=1)

        # 2. Dibujo de Scatters (Puntos Exactos)
        label_tamar_add, label_fija_add = False, False
        for i, row in self.df_cuadro.iterrows():
            val = row[col_data]
            if pd.isna(val): continue 
            
            es_tamar = row['Especie'] in self.tickers_tamar
            color_pt, marker_pt = ('#4361ee', '^') if es_tamar else ('#e63946', 'o')
            
            lbl = f"{pre_label} Tamar" if es_tamar and not label_tamar_add else (f"{pre_label} Fija" if not es_tamar and not label_fija_add else "")
            if es_tamar: label_tamar_add = True 
            else: label_fija_add = True

            ax.scatter(i, val, color=color_pt, marker=marker_pt, s=100, zorder=5, label=lbl)
            ax.annotate(f"{val:.2f}%", (i, val), xytext=(0, 12), textcoords='offset points', ha='center', fontsize=9, fontweight='bold', color=color_pt)

        # 3. Formato del Subplot
        ax.set_xticks(x_pos)
        ax.set_xticklabels(self.df_cuadro['Especie'], fontweight='bold', color='dimgray', fontsize=10)
        ax.axhline(0, color='black', linewidth=1, alpha=0.8)
        
        if not self.df_cuadro[col_data].isna().all():
            ax.set_ylim(self.df_cuadro[col_data].min() - margen_y[0], self.df_cuadro[col_data].max() + margen_y[1])
            
        ax.set_title(titulo, fontsize=14, fontweight='bold', color='dimgray', pad=15)
        
        from matplotlib.ticker import PercentFormatter
        ax.yaxis.set_major_formatter(PercentFormatter(decimals=2))
        ax.legend(loc='lower right', frameon=True, fontsize=10)

    def graficar_dashboard_tasas(self):
        """Abre dos ventanas separadas de Curvas de Rendimiento (Una para TNA y otra para TEM)"""
        if self.df_cuadro is None or self.df_cuadro.empty: return
        import seaborn as sns
        import matplotlib.pyplot as plt
        sns.set_style("whitegrid")
        
        # --- CUADRO 1: TNA ---
        fig1, ax1 = plt.subplots(figsize=(16, 9))
        self._dibujar_curva_tasa(ax1, 'TNA_Plot', "TNA LETRAS / BONCAPS - 24hs", "TNA", (5, 10))
        fig1.subplots_adjust(left=0.04, right=0.98, top=0.93, bottom=0.08)
        
        # --- CUADRO 2: TEM ---
        fig2, ax2 = plt.subplots(figsize=(16, 9))
        self._dibujar_curva_tasa(ax2, 'TEM_Num', "TEM (Tasa Efectiva Mensual)", "TEM", (1, 1.5))
        fig2.subplots_adjust(left=0.04, right=0.98, top=0.93, bottom=0.08)
        
        # Muestra ambas ventanas al mismo tiempo
        plt.show()

    def graficar_dashboard_trading(self):
        """Abre la ventana analítica con FX Breakeven y Tasas Forward Implícitas."""
        if self.df_cuadro is None or self.df_cuadro.empty: return
        sns.set_style("whitegrid")
        
        # FIX: Formato panorámico 16:9
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9))

        # --- SUBPLOT 1: DÓLAR IMPLÍCITO (FX Breakeven) ---
        df_dol = self.df_cuadro.sort_values('Dias').reset_index(drop=True)
        x_pos_dol = np.arange(len(df_dol))
        
        if len(df_dol) >= 2:
            z = np.polyfit(df_dol.index, df_dol['Dolar_Eq'], 1) 
            x_sm = np.linspace(0, len(df_dol)-1, 100)
            ax1.plot(x_sm, np.poly1d(z)(x_sm), color='#2a9d8f', alpha=0.5, linewidth=3, linestyle='--', zorder=1)

        for i, row in df_dol.iterrows():
            tc_val = row['Dolar_Eq']
            color_pt = '#4361ee' if row['Obs'] in ['TAMAR', 'DUAL'] else '#e63946'
            ax1.scatter(i, tc_val, color=color_pt, marker='D', s=100, zorder=5)
            ax1.annotate(f"${tc_val:.0f}", (i, tc_val), xytext=(0, 12), textcoords='offset points', ha='center', fontsize=9, fontweight='bold', color=color_pt)

        ax1.set_xticks(x_pos_dol)
        ax1.set_xticklabels(df_dol['Especie'], fontweight='bold', color='dimgray', fontsize=10)
        ax1.set_ylim(df_dol['Dolar_Eq'].min() - 50, df_dol['Dolar_Eq'].max() + 100)
        ax1.set_title("CURVA DE DÓLAR IMPLÍCITO (FX BREAKEVEN MEP)", fontsize=14, fontweight='bold', color='dimgray', pad=15)

        # --- SUBPLOT 2: TASAS FORWARD (Tramo Fijo) ---
        df_fija = self.df_cuadro[~self.df_cuadro['Especie'].isin(self.tickers_tamar)].dropna(subset=['TNA_Fija_Num']).sort_values('Dias').reset_index(drop=True)
        
        if len(df_fija) >= 2:
            df_fija['Yield_Acum'] = 1 + (df_fija['TNA_Fija_Num'] / 100) * (df_fija['Dias'] / 365)
            fwd_rates, labels_fwd = [], []
            
            for i in range(len(df_fija) - 1):
                r1, r2 = df_fija.iloc[i], df_fija.iloc[i+1]
                delta = r2['Dias'] - r1['Dias']
                if delta > 0:
                    tna_fwd = ((r2['Yield_Acum'] / r1['Yield_Acum']) - 1) * (365 / delta) * 100
                    fwd_rates.append(tna_fwd)
                    labels_fwd.append(f"{r1['Especie']}\n➔\n{r2['Especie']}")

            x_pos_fwd = np.arange(len(fwd_rates))
            barras = ax2.bar(x_pos_fwd, fwd_rates, color='#f4a261', alpha=0.8, edgecolor='black', linewidth=1)
            
            for bar, tasa in zip(barras, fwd_rates):
                ax2.annotate(f"{tasa:.2f}%", (bar.get_x() + bar.get_width() / 2, bar.get_height()), xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')

            ax2.set_xticks(x_pos_fwd)
            ax2.set_xticklabels(labels_fwd, fontweight='bold', color='dimgray', fontsize=10)
            ax2.axhline(0, color='black', linewidth=1, alpha=0.8)
            
            from matplotlib.ticker import PercentFormatter
            ax2.yaxis.set_major_formatter(PercentFormatter(decimals=2))
            ax2.set_title("TASAS FORWARD IMPLÍCITAS (ENTRE NODOS TASA FIJA)", fontsize=14, fontweight='bold', color='dimgray', pad=15)

        # FIX CLAVE: Empujamos a los bordes y damos espacio (hspace) para las etiquetas
        fig.subplots_adjust(left=0.04, right=0.98, top=0.93, bottom=0.10, hspace=0.35)
        plt.show()