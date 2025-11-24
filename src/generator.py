import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import os
import numpy as np

# Paths
CELLS_PATH = "./data/cells.csv"
AREA_PATH = "./data/area.geojson"
OUTPUT_DIR = "./outputs"

def load_data():
    cells = pd.read_csv(CELLS_PATH)
    area = gpd.read_file(AREA_PATH)

    # Convert cells to GeoDataFrame
    geometry = [Point(xy) for xy in zip(cells["longitude"], cells["latitude"])]
    cells_gdf = gpd.GeoDataFrame(cells, geometry=geometry, crs="EPSG:4326")

    return cells_gdf, area

def generate_coverage_map(cells_gdf, area_gdf):
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot area
    area_gdf.plot(ax=ax, color="lightgrey", edgecolor="black", alpha=0.5)

    # Plot cells with different sizes according to power
    cells_gdf.plot(
        ax=ax,
        column="power_dbm",
        cmap="viridis",
        markersize = np.interp(cells_gdf["power_dbm"], (cells_gdf["power_dbm"].min(), cells_gdf["power_dbm"].max()), (50, 300)),
        #markersize=cells_gdf["power_dbm"] * 10,
        legend=True
    )

    plt.title("Synthetic Mobile Coverage Map - Cali")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    output_path = os.path.join(OUTPUT_DIR, "coverage_map.png")
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Map generated: {output_path}")

if __name__ == "__main__":
    cells_gdf, area_gdf = load_data()
    generate_coverage_map(cells_gdf, area_gdf)
