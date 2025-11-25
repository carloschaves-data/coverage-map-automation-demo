 # Coverage Map Automation – Versión Intermedia

Proyecto diseñado para simular, procesar y visualizar mapas de cobertura móvil utilizando datos sintéticos de celdas 4G y 5G.
Incluye generación de geometrías, cálculos KPI, visualización y un pipeline orquestado.

📌 Objetivo del Proyecto

Construir una herramienta modular capaz de:
Procesar una base de datos sintética de celdas 4G/5G.
Generar polígonos de cobertura basados en potencia, azimut y ancho de haz.
Calcular KPIs por celda y por área.
Visualizar mapas de cobertura de forma automatizada.
Preparar un pipeline listo para escalar a análisis más avanzados.
Este proyecto simula tareas comunes en áreas como RF Engineering, Planning, Drive Test Automation y Data Analytics.

📁 Estructura del Proyecto
coverage-map-automation-demo/
│
├── data/
│   └── cells.csv
│
├── output/
│   └── coverage_map.png
│
├── src/
│   ├── generator.py         # Orquestador principal
│   ├── geometry.py          # Módulo de geocálculos
│   ├── kpi.py               # Módulo de generación de KPIs
│   ├── visualizer.py        # Módulo de visualización
│
├── README.md
└── requirements.txt

⚙️ Instalación del entorno
1. Crear entorno virtual
python -m venv venv

2. Activarlo

Windows:
venv\Scripts\activate


Mac/Linux:
source venv/bin/activate

3. Instalar dependencias
pip install -r requirements.txt

📊 Datos de Entrada

El archivo cells.csv debe contener las siguientes columnas:

Columna 	            Descripción
cell_id	                ID único de sector
site_id	                ID del sitio
sector_id	            Sector (1-3)
latitude / longitude	Coordenadas de la celda
azimuth	                Dirección del haz
power_dbm	            Potencia transmitida
tilt	                Tilt del panel
technology	            4G / 5G
rsrp_mean	            Valor medio RSRP
rsrq_mean	            Valor medio RSRQ
coverage_radius_m	    Radio de cobertura estimado
beamwidth	            Apertura del haz
pci	PCI / GNB-ID
🚀 Ejecución

Desde la carpeta raíz:

python src/generator.py


Esto ejecutará:
Carga del dataset y creación del GeoDataFrame.
Generación de geometrías de coverage.
Cálculo de KPIs.
Ensamble final del mapa.
Exportación a /output/coverage_map.png.

📐 Módulos Principales
geometry.py

Contiene funciones para:
Generar buffers de cobertura basados en potencia.
Generar polígonos direccionales según azimuth y beamwidth.
Convertir puntos a geometrías geoespaciales.
kpi.py

Incluye funciones como:
Generación de KPIs por celda.
Cálculo de área cubierta.
Cálculo de superposición de celdas.
Detección de huecos de cobertura (versión futura).

generator.py
Se encarga de:
Orquestar la carga de datos.
Ejecutar el pipeline geométrico.
Ejecutar KPIs.
Enviar todo a visualizer.py.

Exportar los resultados.

🗺️ Visualización

El mapa generado incluye:

✔ Sectores 4G / 5G
✔ Coberturas representadas con polígonos
✔ Colores por tecnología
✔ Centros de celda marcados
✔ Exportación a PNG

📌 Próximas versiones

Detección automática de anomalías de cobertura.
Clustering de celdas por nivel de señal.
Heatmaps de RSRP / RSRQ.
Dashboard interactivo (Streamlit / Dash).
Simulación de handovers y overlaps.

🧑‍💻 Autor

Desarrollado por Carlos Chaves – Ingeniería en Sistemas y Telecomunicaciones.