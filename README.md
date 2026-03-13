# 📈 Monitor de Renta Fija Argentina 🇦🇷

Monitor y screener automatizado de activos del mercado de capitales argentino, desarrollado íntegramente en Python. Este proyecto extrae datos en vivo de mercado, calcula métricas financieras avanzadas y genera visualizaciones clave para el análisis y la toma de decisiones.

## 🚀 Características (Módulo Soberanos & Bopreales)

* **Arquitectura Orientada a Objetos (OOP):** Diseño modular utilizando clases (`BonoHD` y `MonitorHD`) para facilitar la escalabilidad a otros instrumentos (Letras, Corporativos).
* **Cálculo Avanzado de TIR:** Implementación del método de Newton-Raphson (`scipy.optimize.newton`) para el cálculo iterativo y preciso de la Tasa Interna de Retorno (IRR).
* **Manejo de Liquidación Real (T+n):** Uso de `BusinessDay` de Pandas para el cálculo exacto de fechas de liquidación, excluyendo fines de semana y ajustando el devengamiento del interés corrido (Accrued Interest).
* **Dolarización Dinámica:** Cálculo en vivo del tipo de cambio implícito (CCL) mediante las cotizaciones AL30/AL30D.
* **Visualización de la Estructura Temporal:** Ploteo de la curva de rendimientos (TIR vs. Modified Duration) con ajuste polinómico para la curva teórica, y mapa de Paridades para identificar desarbitrajes relativos.

## 🚀 Características (Módulo Lecaps & Boncaps)

* **Cálculo del Precio Contado Arbitrado (PCA):** Descuento del plazo de liquidación (T+1) sobre los precios en vivo utilizando la tasa de caución real del mercado.
* **Integración API BCRA (Proxy de Caución):** Ante la falta de tasa de caución en la API de precios, el script consume la "Tasa de interés por operaciones de pases entre terceros a 1 día" del BCRA como proxy dinámico (requiere Token propio).
* **Métricas de Rendimiento Zero Coupon:** Cálculo automatizado de TNA, TEA, TEM y Modified Duration, segmentando los instrumentos a Tasa Fija de los vinculados a tasa variable (TAMAR).
* **Trading Implícito (Forward & FX Breakeven):** Derivación matemática de las Tasas Forward Implícitas nodo a nodo (tramo fijo) y cálculo de la Curva de Dólar Implícito cruzando la paridad en pesos contra el tipo de cambio MEP dinámico.
* **Curvas de Tendencia Logarítmicas:** Aplicación de regresiones logarítmicas (`np.polyfit`) para trazar las curvas teóricas de rendimiento (TNA y TEM), facilitando la rápida identificación de desarbitrajes.

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.x
* **Análisis de Datos y Matemáticas:** Pandas, NumPy, SciPy
* **Visualización:** Matplotlib, Seaborn
* **Integración de Datos:** Requests (Consumo de API REST en vivo)

## 📂 Estructura del Proyecto

El proyecto se divide en módulos según la familia de activos:

📁 `/soberanos`
  * `bonos_data.py`: Base de datos estática con cronograma de flujos de fondos (Cash Flows) y tasas de cupón.
  * `finanzas_engine.py`: Motor financiero y clases principales para el procesamiento de métricas (VR, AI, TIR, Paridad).
  * `main.py`: Script de ejecución principal y visualización.

📁 `/letras_y_pesos`
  * `letras_data.py`: Diccionario  con la metadata de las Letras (vencimiento, tipo, valor nominal).
  * `finance_engine_letras.py`: Clase principal con el motor matemático y los dashboards operativos.
  * `main_letras.py`: Script de ejecución principal y visualización del tablero de pesos.

## 📊 Visualizaciones Generadas

### Curva Soberana (Hard Dollar)
<img width="1707" height="847" alt="Curva_soberanos_hd" src="https://github.com/user-attachments/assets/7358d9e2-4591-4f3c-9f83-a4787825f78a" />

### Estructura de Tasas en Pesos (TNA y TEM)
<img width="1707" height="847" alt="TNA lecaps" src="https://github.com/user-attachments/assets/b6221638-3c78-4002-a539-1b941989a692" />
<img width="1707" height="847" alt="Tem lecaps" src="https://github.com/user-attachments/assets/003f53ba-143d-41a4-9f2c-c3553468d3f1" />

### Curvas implicitas (Dólar MEP & Tasas Forward)
<img width="1707" height="847" alt="Dolar - tasas implicitas lecaps" src="https://github.com/user-attachments/assets/223062b9-904f-466a-9ecd-5a2e6b30b529" />
