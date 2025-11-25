import folium
import numpy as np
from shapely.geometry import Point, Polygon
from folium.plugins import MarkerCluster

# ---------------------------
# Crear polígono direccional
# ---------------------------
def create_sector_polygon(lat, lon, azimuth, beamwidth, radius_m):
    """Genera un polígono tipo wedge (sector) basado en:
    - azimuth
    - beamwidth
    - coverage radius
    """

    center = Point(lon, lat)

    # Convertir metros a grados aproximados
    meter_to_deg = 1 / 111320

    radius_deg = radius_m * meter_to_deg

    # Ángulos del sector
    start_angle = azimuth - beamwidth / 2
    end_angle = azimuth + beamwidth / 2

    points = [(center.x, center.y)]

    for ang in np.linspace(start_angle, end_angle, 20):
        ang_rad = np.deg2rad(ang)
        x = center.x + radius_deg * np.sin(ang_rad)
        y = center.y + radius_deg * np.cos(ang_rad)
        points.append((x, y))

    points.append((center.x, center.y))
    return Polygon(points)


# ---------------------------
# Visualizador principal
# ---------------------------
def visualize_coverage(cells_gdf, output_path="coverage_map.html"):
    """Genera un mapa folium con:
    - sectores direccionales
    - colores por tecnología
    - marcadores escalados por potencia
    - labels PCI
    """

    # Centrar mapa
    m = folium.Map(location=[cells_gdf.latitude.mean(),
                             cells_gdf.longitude.mean()],
                   zoom_start=13,
                   tiles="OpenStreetMap")

    # Colores por tecnología
    tech_colors = {
        "4G": "#2ecc71",
        "5G": "#8e44ad"
    }

    cluster = MarkerCluster().add_to(m)

    # Crear polígonos
    for _, row in cells_gdf.iterrows():

        # Generar polígono del sector
        poly = create_sector_polygon(
            row["latitude"],
            row["longitude"],
            row["azimuth"],
            row["beamwidth"],
            row["coverage_radius_m"]
        )

        # Dibujar polígono
        folium.GeoJson(
            poly,
            style_function=lambda x, color=tech_colors[row["technology"]]: {
                "fillColor": color,
                "color": color,
                "weight": 1,
                "fillOpacity": 0.35
            },
            tooltip=(
                f"<b>{row['cell_id']}</b><br>"
                f"SITE: {row['site_id']}<br>"
                f"TECNOLOGÍA: {row['technology']}<br>"
                f"AZIMUTH: {row['azimuth']}°<br>"
                f"PCI: {row['pci']}<br>"
                f"RSRP mean: {row['rsrp_mean']} dBm<br>"
            )
        ).add_to(m)

        # Dibujar marcadores escalados
        power_scale = max(3, row["power_dbm"] / 10)

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=power_scale,
            color=tech_colors[row["technology"]],
            fill=True,
            fill_opacity=0.9,
            tooltip=f"{row['cell_id']} - {row['power_dbm']} dBm"
        ).add_to(cluster)

        # Etiqueta PCI flotante
        folium.map.Marker(
            [row["latitude"] + 0.0003, row["longitude"]],
            icon=folium.DivIcon(
                html=f"""<div style="font-size:12px;
                                   color:black;
                                   font-weight:bold;">
                        PCI {row['pci']}</div>"""
            )
        ).add_to(m)

    # Guardar
    m.save(output_path)
    print(f"Mapa generado: {output_path}")
