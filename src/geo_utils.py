import pydeck as pdk

def to_pydeck_layer_points(records, name="Points", heat=False):
    if not records:
        return []
    if heat:
        return [pdk.Layer(
            "HeatmapLayer",
            data=records,
            get_position='[lon, lat]',
            get_weight='weight',
            aggregation='MEAN',
            opacity=0.4
        )]
    return [pdk.Layer(
        "ScatterplotLayer",
        data=records,
        get_position='[lon, lat]',
        get_radius=3000,              # meters
        filled=True,
        pickable=True,
        get_fill_color=[230, 57, 70], # 🔴 visible red
        get_line_color=[20, 20, 20],
        line_width_min_pixels=1
    )]

def to_pydeck_layer_polygons(polys, name="Polygons"):
    if not polys:
        return []
    return [pdk.Layer(
        "PolygonLayer",
        data=polys,
        get_polygon='polygon',
        stroked=True,
        filled=True,
        extruded=False,
        get_fill_color='[255, 140, 0, 80]',
        get_line_color='[50, 50, 50]',
        pickable=True
    )]
