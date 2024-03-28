import geopandas

from src.cross_section.create_cross_section_points import create_cross_section_points

TRANSECT_DATA_PATH = "../data/cross_section/Transects_Level_2_ESC.shp"
SAVING_FOLDER_PATH = "../data/cross_section/points/"
DISTANCE = 1

if __name__ == "__main__":
    data = geopandas.read_file(TRANSECT_DATA_PATH)
    create_cross_section_points(data, DISTANCE, SAVING_FOLDER_PATH, True)
