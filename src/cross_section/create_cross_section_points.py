import geopandas
import pandas
from pathlib import Path
from shapely.geometry import LineString
from tqdm import tqdm

from src.cross_section.utils import (
    retrieve_polygon_for_pk,
    get_points_of_contact_between_two_polygon,
    farthest_points_from_list_of_points,
    get_boundaries_points_list,
    adjust_point_to_be_on_polygon_edge,
    get_extremities_points_from_points_before_and_after,
    add_z_to_points_list_from_z_list,
)

MANNING = 0.037


def create_cross_section_points(
    data, folder_save_path, save_boudaries_points_and_line=False
):
    pk_list = []
    z_list = []
    points_list = []
    boundary_list = []
    line_list = []
    for i in tqdm(range(1, len(data) - 1)):
        pk = data.loc[i]["PK"]
        transect_polygon = data.loc[i].geometry
        qi = data.loc[i]["Q_ortho_adjusted"]
        si = data.loc[i]["Slope"]

        polygon_before = retrieve_polygon_for_pk(data, pk - 5)
        polygon_after = retrieve_polygon_for_pk(data, pk + 5)

        intersect_points_before = get_points_of_contact_between_two_polygon(
            transect_polygon, polygon_before
        )
        intersect_points_after = get_points_of_contact_between_two_polygon(
            transect_polygon, polygon_after
        )

        if len(intersect_points_before) == 0 or len(intersect_points_after) == 0:
            continue

        intersect_points_before = farthest_points_from_list_of_points(
            intersect_points_before
        )
        intersect_points_after = farthest_points_from_list_of_points(
            intersect_points_after
        )

        boundary_list.extend(
            get_boundaries_points_list(intersect_points_before, intersect_points_after)
        )

        (
            int_point_list,
            int_line_list,
        ) = get_extremities_points_from_points_before_and_after(
            intersect_points_before, intersect_points_after
        )
        line_list.extend(int_line_list)

        pk_list.extend([pk] * 4)
        adjusted_point_list = adjust_point_to_be_on_polygon_edge(
            int_point_list, transect_polygon
        )
        points_list.extend(adjusted_point_list)
        z_list.extend([0] * 2)

        line_string = LineString(adjusted_point_list)
        points_list.append(line_string.line_interpolate_point(0.1, normalized=True))
        points_list.append(line_string.line_interpolate_point(0.9, normalized=True))
        wi = line_string.length
        di = ((qi * MANNING) / (wi * (si**0.5))) ** (3 / 5)
        hi = 2 * di / 1.8
        z_list.extend([hi] * 2)

    points_list_with_z = add_z_to_points_list_from_z_list(points_list, z_list)

    if save_boudaries_points_and_line:
        geo_df_int = geopandas.GeoDataFrame(geometry=boundary_list, crs="EPSG:2948")
        geo_df_int.to_file(Path(folder_save_path, "boundary_points.shp"))

        geo_df_int_ls = geopandas.GeoDataFrame(geometry=line_list, crs="EPSG:2948")
        geo_df_int_ls.to_file(Path(folder_save_path, "boundary_lines.shp"))

    df = pandas.DataFrame({"PK": pk_list, "z": z_list})

    geo_df = geopandas.GeoDataFrame(df, geometry=points_list_with_z, crs="EPSG:2948")
    geo_df.to_file(Path(folder_save_path, "cross_section_points.shp"))
