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

    # Assign a color per record based on status (simple + readable)
    for r in records:
        s = (r.get("status") or "").lower()
        if "out of control" in s:
            r["color"] = [230, 57, 70]      # red
        elif "being controlled" in s:
            r["color"] = [255, 165, 0]      # orange
        else:
            r["color"] = [34, 139, 34]      # green

    return [pdk.Layer(
        "ScatterplotLayer",
        data=records,
        get_position='[lon, lat]',
        get_radius=4500,         # larger for visibility at zoom ~5 (accessibility)
        filled=True,
        pickable=True,
        get_fill_color='color',
        get_line_color=[30, 30, 30],
        line_width_min_pixels=1,
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
        get_fill_color='[255, 140, 0, 80]',  # orange with alpha
        get_line_color='[50, 50, 50]',
        pickable=True
    )]