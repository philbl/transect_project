import geopandas
import pandas
from pathlib import Path
from shapely.geometry import LineString, Point
from tqdm import tqdm

from src.cross_section.utils import (
    retrieve_polygon_for_pk,
    get_points_of_contact_between_two_polygon,
    farthest_points_from_list_of_points,
    get_boundaries_points_list,
    adjust_point_to_be_on_polygon_edge,
    get_extremities_points_from_points_before_and_after,
    create_all_points_from_shore_points_list,
)

MANNING = 0.037


def create_cross_section_points(
    data, distance, folder_save_path, save_boudaries_points_and_line=False
):
    pk_list = []
    error_list = []
    z_list = []
    points_list = []
    boundary_list = []
    line_list = []
    epsg = data.crs.to_epsg()
    for i in tqdm(range(1, len(data) - 1)):
        pk = data.loc[i]["PK"]
        transect_polygon = data.loc[i].geometry
        qi = data.loc[i]["Q_IMG_spli"]
        si = data.loc[i]["Slope"]
        if si == 0:
            continue

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

        # Ajouter les points qui sont sur la frontière en amont
        intersect_points_after_point_class = [
            Point(point[0], point[1]) for point in intersect_points_after
        ]
        uptstream_middle_points_list = create_all_points_from_shore_points_list(
            intersect_points_after_point_class, qi, MANNING, si, distance
        )
        points_list.extend(uptstream_middle_points_list)
        pk_list.extend([pk] * len(uptstream_middle_points_list))
        z_list.extend([point.coords[0][2] for point in uptstream_middle_points_list])
        ###

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

        adjusted_point_list = adjust_point_to_be_on_polygon_edge(
            int_point_list, transect_polygon
        )

        if LineString(adjusted_point_list).length == 0:
            error_list.append(i)
            continue

        all_middle_points_list = create_all_points_from_shore_points_list(
            adjusted_point_list, qi, MANNING, si, distance
        )
        points_list.extend(all_middle_points_list)
        pk_list.extend([pk] * len(all_middle_points_list))
        z_list.extend([point.coords[0][2] for point in all_middle_points_list])

    if save_boudaries_points_and_line:
        geo_df_int = geopandas.GeoDataFrame(geometry=boundary_list, crs=f"EPSG:{epsg}")
        geo_df_int.to_file(Path(folder_save_path, f"boundary_points_{distance}m.shp"))

        geo_df_int_ls = geopandas.GeoDataFrame(geometry=line_list, crs=f"EPSG:{epsg}")
        geo_df_int_ls.to_file(Path(folder_save_path, f"boundary_lines_{distance}m.shp"))

    df = pandas.DataFrame({"PK": pk_list, "z": z_list})
    geo_df = geopandas.GeoDataFrame(df, geometry=points_list, crs=f"EPSG:{epsg}")
    geo_df.to_file(Path(folder_save_path, f"cross_section_points_{distance}m.shp"))
