# Coverage Map Automation Demo

This project demonstrates how to automatically generate a synthetic mobile network coverage map using:
- Python
- GeoPandas
- Pandas
- Matplotlib
- Geospatial processing

Although inspired by real telecom workflows, **all data used here is fully synthetic or open-data**, with no proprietary or confidential information.

---

## 📌 Project Structure

coverage-map-automation-demo/
│── data/
│ ├── cells.csv # Synthetic cell data
│ ├── area.geojson # Open-data polygon of Cali, Colombia
│
│── src/
│ ├── generator.py # Main script for map generation
│
│── outputs/
│ ├── coverage_map.png # Generated map (created on run)
│
│── requirements.txt
│── README.md

## 🚀 How to Run

1. Install dependencies:
pip install -r requirements.txt
2. Run the script:
python src/generator.py
3. The output map will be saved in:
outputs/coverage_map.png


---

## 📊 Result

The script generates a map showing:
- The urban polygon of Cali  
- Synthetic cell sites  
- Colors and marker sizes proportional to transmit power  

This project simulates part of a typical telecom RF workflow using **safe, non-proprietary data**.

---

## 📡 Author
**Carlos Andrés Chaves**  
Automation & Data Engineer  
GitHub: https://github.com/carloschaves-data  
