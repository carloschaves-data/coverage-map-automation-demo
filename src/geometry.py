# geometry.py
from pathlib import Path
import math
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]

def read_cells(csv_path: Path = None):
    """
    Read cells CSV in a robust way: accepts comma or tab separators and common thousands separators.
    Returns a pandas DataFrame.
    """
    if csv_path is None:
        csv_path = ROOT / "data" / "cells.csv"

    # try to infer separator (tab or comma)
    try:
        df = pd.read_csv(csv_path, sep=None, engine="python", thousands=None)
    except Exception:
        # fallback to comma
        df = pd.read_csv(csv_path, sep=",", engine="python", thousands=None)

    # normalize column names (strip and lower)
    df.columns = [c.strip() for c in df.columns]
    return df

def df_to_gdf_points(df, lon_col="longitude", lat_col="latitude", crs="EPSG:4326"):
    """
    Convert DataFrame with lon/lat into a GeoDataFrame with given CRS.
    """
    if lon_col not in df.columns or lat_col not in df.columns:
        raise KeyError(f"Columns {lon_col} and {lat_col} required in CSV")
    geometry = [Point(xy) for xy in zip(df[lon_col].astype(float), df[lat_col].astype(float))]
    gdf = gpd.GeoDataFrame(df.copy(), geometry=geometry, crs=crs)
    return gdf

def to_metric(gdf, target_epsg=3857):
    """
    Project GeoDataFrame to metric CRS (default Web-Mercator EPSG:3857).
    """
    return gdf.to_crs(epsg=target_epsg)

def sector_polygon_m(center_x, center_y, radius_m, azimuth_deg, beamwidth_deg, n_points=64):
    """
    Create a sector polygon (wedge) in metric coordinates.
    center_x, center_y: center coordinates in meters (projected CRS)
    radius_m: coverage radius (meters)
    azimuth_deg: center azimuth in degrees (0 = North? we'll use math convention: 0° = East)
    beamwidth_deg: total beamwidth degrees
    NOTE: We will assume azimuth is degrees clockwise from North (typical in telecom).
    For geometry math we convert to radians and compute positions.
    """
    # Convert azimuth from degrees clockwise from North to radians from +x (East) CCW
    # Math: angle_rad = (90 - azimuth_deg) * pi/180 gives angle from +x axis CCW
    start_angle = azimuth_deg - (beamwidth_deg / 2.0)
    end_angle = azimuth_deg + (beamwidth_deg / 2.0)
    angles_deg = np.linspace(start_angle, end_angle, n_points)

    points = []
    for a in angles_deg:
        # convert: math_angle = 90 - a  (degrees) -> radians
        math_angle = math.radians(90.0 - a)
        x = center_x + (radius_m * math.cos(math_angle))
        y = center_y + (radius_m * math.sin(math_angle))
        points.append((x, y))

    # include center to close wedge
    coords = [(center_x, center_y)] + points + [(center_x, center_y)]
    return Polygon(coords)

def generate_sector_geometries(cells_gdf, coverage_radius_col="coverage_radius_m",
                               az_col="azimuth", beam_col="beamwidth", site_id_col="site_id",
                               sector_id_col="sector_id"):
    """
    Input: cells_gdf in EPSG:4326 (lon/lat). This function:
      - projects to metric (EPSG:3857)
      - for each row creates a sector polygon (approx wedge) using coverage_radius_m and beamwidth
      - returns a GeoDataFrame of sectors in both metric CRS (3857) and original CRS (4326)
    """
    # project to metric for meter-based buffers and geometry creation
    gdf_m = cells_gdf.to_crs(epsg=3857).copy()

    sector_polys = []
    for idx, row in gdf_m.iterrows():
        try:
            radius = float(row.get(coverage_radius_col, 500))
        except Exception:
            radius = 500.0
        try:
            az = float(row.get(az_col, 0.0))
        except Exception:
            az = 0.0
        try:
            beam = float(row.get(beam_col, 120.0))
        except Exception:
            beam = 120.0

        cx = row.geometry.x
        cy = row.geometry.y

        poly = sector_polygon_m(cx, cy, radius, az, beam, n_points=48)
        sector_polys.append(poly)

    sectors_gdf = gpd.GeoDataFrame(cells_gdf.reset_index(drop=True), geometry=sector_polys, crs="EPSG:3857")
    # also add a lon/lat geometry version
    sectors_lonlat = sectors_gdf.to_crs(epsg=4326)
    return sectors_gdf, sectors_lonlat

def union_coverage(sectors_gdf_metric):
    """
    Return union (single geometry) of all sector polygons (in metric CRS).
    """
    if sectors_gdf_metric.empty:
        return None
    union_geom = unary_union(sectors_gdf_metric.geometry.values)
    return union_geom

def load_area(area_path: Path = None):
    """
    Load area polygon GeoJSON (expected EPSG:4326) and return as GeoDataFrame in both 4326 and 3857.
    """
    if area_path is None:
        area_path = ROOT / "data" / "area.geojson"
    area = gpd.read_file(area_path)
    if area.crs is None:
        area = area.set_crs(epsg=4326)
    area_m = area.to_crs(epsg=3857)
    return area, area_m
