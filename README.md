# 📈 Monitor de Renta Fija Argentina 🇦🇷

Monitor y screener automatizado de activos del mercado de capitales argentino, desarrollado íntegramente en Python. Este proyecto extrae datos en vivo de mercado, calcula métricas financieras avanzadas y genera visualizaciones clave para el análisis y la toma de decisiones.

## 🚀 Características (Módulo Soberanos & Bopreales)

* **Arquitectura Orientada a Objetos (OOP):** Diseño modular utilizando clases (`BonoHD` y `MonitorHD`) para facilitar la escalabilidad a otros instrumentos (Letras, Corporativos).
* **Cálculo Avanzado de TIR:** Implementación del método de Newton-Raphson (`scipy.optimize.newton`) para el cálculo iterativo y preciso de la Tasa Interna de Retorno (IRR).
* **Manejo de Liquidación Real (T+n):** Uso de `BusinessDay` de Pandas para el cálculo exacto de fechas de liquidación, excluyendo fines de semana y ajustando el devengamiento del interés corrido (Accrued Interest).
* **Dolarización Dinámica:** Cálculo en vivo del tipo de cambio implícito (CCL) mediante las cotizaciones AL30/AL30D.
* **Visualización de la Estructura Temporal:** Ploteo de la curva de rendimientos (TIR vs. Modified Duration) con ajuste polinómico para la curva teórica, y mapa de Paridades para identificar desarbitrajes relativos.

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

## 📊 Visualizaciones Generadas

<img width="1707" height="847" alt="Curva_soberanos_hd" src="https://github.com/user-attachments/assets/7358d9e2-4591-4f3c-9f83-a4787825f78a" />

*Proyecto en desarrollo continuo. Próxima iteración: Monitor de curva de pesos (Letras y Bonos CER).*
