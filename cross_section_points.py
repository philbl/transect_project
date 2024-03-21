import geopandas
import pandas

from src.cross_section.create_cross_section_points import create_cross_section_points

TRANSECT_DATA_PATH = "../data/cross_section/Transects_Level_2_TRI.shp"
ADJUSTED_LEVEL_DATA_PATH = "../data/cross_section/Transect_Level_2.csv"
SAVING_FOLDER_PATH = "../data/cross_section/points/"

if __name__ == "__main__":
    data = geopandas.read_file(TRANSECT_DATA_PATH)
    level_data = pandas.read_csv(ADJUSTED_LEVEL_DATA_PATH)
    level_data = level_data.drop_duplicates("PK").reset_index(drop=True)
    level_data = level_data[["PK", "Q_ortho"]]
    level_data = level_data.rename(columns={"Q_ortho": "Q_ortho_adjusted"})
    data_adjusted = data.merge(level_data, on="PK", how="left")

    create_cross_section_points(data_adjusted, SAVING_FOLDER_PATH)
