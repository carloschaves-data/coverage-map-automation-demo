# generator.py
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
import pandas as pd
import os
from geometry import read_cells, df_to_gdf_points, load_area, generate_sector_geometries, union_coverage, to_metric
from kpi import compute_site_kpis, compute_overall_kpis

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"

CELLS_CSV = DATA_DIR / "cells.csv"
AREA_GEOJSON = DATA_DIR / "area.geojson"

OUTPUT_GEOJSON = OUTPUT_DIR / "coverage_module1.geojson"
OUTPUT_MAP_PNG = OUTPUT_DIR / "coverage_module1.png"
OUTPUT_MAP_HTML = OUTPUT_DIR / "coverage_module1.html"
OUTPUT_KPI_CSV = OUTPUT_DIR / "kpis_module1.csv"

def ensure_outputs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def plot_map(sectors_lonlat_gdf, area_gdf_lonlat, output_png=OUTPUT_MAP_PNG):
    fig, ax = plt.subplots(figsize=(10,10))
    area_gdf_lonlat.plot(ax=ax, color="lightgrey", edgecolor="black", alpha=0.4)
    # plot sectors polygons colored by technology if available
    if "technology" in sectors_lonlat_gdf.columns:
        sectors_lonlat_gdf.plot(ax=ax, column="technology", categorical=True, legend=True, alpha=0.6, edgecolor="k")
    else:
        sectors_lonlat_gdf.plot(ax=ax, alpha=0.6, edgecolor="k")

    # optionally plot site points (centers)
    if "longitude" in sectors_lonlat_gdf.columns and "latitude" in sectors_lonlat_gdf.columns:
        # create center points from lon/lat
        centers = gpd.GeoDataFrame(sectors_lonlat_gdf.copy(), geometry=gpd.points_from_xy(sectors_lonlat_gdf["longitude"].astype(float),
                                                                                        sectors_lonlat_gdf["latitude"].astype(float)),
                                   crs="EPSG:4326")
        centers.plot(ax=ax, markersize=10, color="black")

    plt.title("Coverage (Module 1) - Sectors")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    # save
    plt.tight_layout()
    plt.savefig(output_png, dpi=200)
    plt.close()
    print(f"Saved map PNG: {output_png}")

def export_geojson(sectors_lonlat_gdf, path=OUTPUT_GEOJSON):
    sectors_lonlat_gdf.to_file(path, driver="GeoJSON")
    print(f"Saved GeoJSON: {path}")

def export_folium(sectors_lonlat_gdf, area_gdf_lonlat, path=OUTPUT_MAP_HTML):
    # center map in area centroid if possible
    centroid = area_gdf_lonlat.unary_union.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=12, tiles="CartoDB positron")
    # add area polygon
    folium.GeoJson(area_gdf_lonlat.__geo_interface__, name="area").add_to(m)
    # add sectors (as GeoJSON)
    folium.GeoJson(sectors_lonlat_gdf.__geo_interface__, name="sectors").add_to(m)
    m.save(str(path))
    print(f"Saved interactive map HTML: {path}")

def run_module1():
    print("Cargando datos...")
    df = read_cells(CELLS_CSV)
    # ensure numeric fields are numeric
    numeric_cols = ["latitude","longitude","azimuth","power_dbm","tilt","rsrp_mean","rsrq_mean","coverage_radius_m","beamwidth"]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    print("Convirtiendo a GeoDataFrame (puntos lon/lat)...")
    cells_gdf = df_to_gdf_points(df, lon_col="longitude", lat_col="latitude")

    print("Cargando área (polígono) ...")
    area_gdf, area_gdf_m = load_area(AREA_GEOJSON)

    print("Generando polígonos de cobertura (sectores) en métrico ...")
    sectors_metric_gdf, sectors_lonlat_gdf = generate_sector_geometries(cells_gdf,
                                                                        coverage_radius_col="coverage_radius_m",
                                                                        az_col="azimuth",
                                                                        beam_col="beamwidth",
                                                                        site_id_col="site_id",
                                                                        sector_id_col="sector_id")

    # Save outputs
    ensure_outputs()
    print("Exportando GeoJSON de sectores (lon/lat)...")
    export_geojson(sectors_lonlat_gdf, OUTPUT_GEOJSON)

    # compute KPIs
    print("Calculando KPI por sitio y globales...")
    kpi_df = compute_site_kpis(sectors_metric_gdf, area_gdf_m, site_id_col="site_id")
    overall = compute_overall_kpis(sectors_metric_gdf, area_gdf_m)
    # write KPI CSV
    combined = kpi_df.copy()
    combined["analysis_area_total_m2"] = overall["area_total_m2"]
    combined["analysis_total_covered_m2"] = overall["total_covered_area_m2"]
    combined["analysis_covered_percent"] = overall["covered_percent"]
    combined.to_csv(OUTPUT_KPI_CSV, index=False)
    print(f"Saved KPI CSV: {OUTPUT_KPI_CSV}")

    # plot static PNG
    print("Generando mapa PNG...")
    plot_map(sectors_lonlat_gdf, area_gdf, OUTPUT_MAP_PNG)

    # interactive folium map (html)
    try:
        print("Generando mapa interactivo HTML (folium)...")
        export_folium(sectors_lonlat_gdf, area_gdf, OUTPUT_MAP_HTML)
    except Exception as e:
        print("No se pudo generar HTML con folium:", e)

    print("Módulo 1 finalizado.")
    print("KPIs generales:", overall)

if __name__ == "__main__":
    run_module1()
