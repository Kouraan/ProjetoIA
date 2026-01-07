from pyproj import Transformer,CRS


def to_latlon(crs,x, y):
    lon, lat = Transformer.from_crs(crs,"EPSG:4326",always_xy=True).transform(x, y)
    return lat, lon