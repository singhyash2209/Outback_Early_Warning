import pydeck as pdk

def to_pydeck_layer_points(records, name="Points", heat=False):
    if not records: return []
    if heat:
        return [pdk.Layer("HeatmapLayer",
                          data=records,
                          get_position='[lon, lat]',
                          get_weight='weight',
                          aggregation='MEAN',
                          opacity=0.4)]
    return [pdk.Layer("ScatterplotLayer",
                      data=records,
                      get_position='[lon, lat]',
                      get_radius=2500,
                      pickable=True,
                      filled=True)]

def to_pydeck_layer_polygons(polys, name="Polygons"):
    if not polys: return []
    return [pdk.Layer("PolygonLayer",
                      data=polys,
                      get_polygon='polygon',
                      stroked=True,
                      filled=True,
                      extruded=False,
                      get_fill_color='[fill_r, fill_g, fill_b, 80]',
                      get_line_color='[80,80,80]',
                      pickable=True)]