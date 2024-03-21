import numpy
from scipy.stats import linregress
from rdp import rdp


def baseline_slope_calculation(pk_array, elevation_array):
    slope_list = []
    slope_buffer = [numpy.nan] * 3
    slope_list.extend(numpy.array([pk_array[:3], slope_buffer]).T)
    for i in range(3, len(elevation_array) - 3):
        elevation_subset = elevation_array[i - 3 : i + 3 + 1]
        pk = pk_array[i]
        pk_subset = pk_array[i - 3 : i + 3 + 1]
        reg = linregress(pk_subset, elevation_subset)
        slope_list.append(numpy.array([pk, reg.slope]))
    slope_list.extend(numpy.array([pk_array[-3:], slope_buffer]).T)
    return numpy.array(slope_list)


def get_rdp_points(pk_array, elevation_array, epsilon):
    rdp_starting_array = numpy.array([pk_array, elevation_array]).T
    rdp_points_kept = rdp(rdp_starting_array, epsilon=epsilon, algo="rec")
    return rdp_points_kept


def get_rdp_slope(rdp_points_kept):
    rdp_slope_list = []
    for i in range(1, len(rdp_points_kept)):
        pk_tuple = (rdp_points_kept[i - 1][0], rdp_points_kept[i][0])
        elevation_tuple = (rdp_points_kept[i - 1][1], rdp_points_kept[i][1])
        slope = (elevation_tuple[1] - elevation_tuple[0]) / (pk_tuple[1] - pk_tuple[0])
        list_elem = list(pk_tuple) + [slope]
        rdp_slope_list.append(list_elem)
    rdp_slope_list = numpy.array(rdp_slope_list)
    return rdp_slope_list


def get_interpolated_rdp_slope(pk_array, rdp_points_kept):
    rdp_slope_list = get_rdp_slope(rdp_points_kept)
    rpd_slope_interpolation = []
    rpd_slope_interpolation.append([pk_array[0], rdp_slope_list[0, 2]])
    for transect in pk_array[1:]:
        mask = (rdp_slope_list[:, 0] < transect) & (rdp_slope_list[:, 1] >= transect)
        slope = rdp_slope_list[mask, 2][0]
        rpd_slope_interpolation.append([transect, slope])
    rpd_slope_interpolation = numpy.array(rpd_slope_interpolation)
    return rpd_slope_interpolation
