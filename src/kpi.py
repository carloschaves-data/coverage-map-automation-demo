# kpi.py
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
from geometry import union_coverage
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

def compute_site_kpis(sectors_gdf_metric, area_gdf_metric, site_id_col="site_id"):
    """
    Compute KPIs aggregated per site:
      - num_sectors
      - mean_rsrp, mean_rsrq
      - total_coverage_area_m2 (union of sector polygons for the site)
      - coverage_ratio (area covered / area of area_gdf_metric)
    Returns a pandas DataFrame.
    """
    site_list = []
    total_area_m2 = area_gdf_metric.unary_union.area if not area_gdf_metric.empty else None

    for site, group in sectors_gdf_metric.groupby(site_id_col):
        # union of sector geometries per site
        union_geom = union_coverage(group)
        covered_area = union_geom.area if union_geom is not None else 0.0

        # numeric KPIs (columns must exist)
        mean_rsrp = safe_mean(group.get("rsrp_mean"))
        mean_rsrq = safe_mean(group.get("rsrq_mean"))
        mean_radius = safe_mean(group.get("coverage_radius_m"))

        site_list.append({
            "site_id": site,
            "num_sectors": len(group),
            "mean_rsrp": mean_rsrp,
            "mean_rsrq": mean_rsrq,
            "mean_radius_m": mean_radius,
            "covered_area_m2": covered_area,
            "coverage_ratio": (covered_area / total_area_m2) if total_area_m2 and total_area_m2 > 0 else None
        })

    kpi_df = pd.DataFrame(site_list)
    return kpi_df

def safe_mean(series):
    try:
        if series is None:
            return None
        s = pd.to_numeric(series, errors="coerce")
        return float(s.mean())
    except Exception:
        return None

def compute_overall_kpis(sectors_gdf_metric, area_gdf_metric):
    """
    KPIs for the whole area:
      - total_covered_area_m2
      - area_total_m2
      - covered_percentage
      - average_rsrp, average_rsrq
    """
    total_area = area_gdf_metric.unary_union.area if not area_gdf_metric.empty else 0.0
    union_geom = union_coverage(sectors_gdf_metric)
    total_covered = union_geom.area if union_geom is not None else 0.0

    avg_rsrp = safe_mean(sectors_gdf_metric.get("rsrp_mean"))
    avg_rsrq = safe_mean(sectors_gdf_metric.get("rsrq_mean"))

    return {
        "area_total_m2": total_area,
        "total_covered_area_m2": total_covered,
        "covered_percent": (total_covered / total_area * 100.0) if total_area > 0 else None,
        "avg_rsrp": avg_rsrp,
        "avg_rsrq": avg_rsrq,
        "num_sectors": len(sectors_gdf_metric)
    }
