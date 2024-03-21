import geopandas


def load_data_and_drop_duplicated(path):
    df = geopandas.read_file(path)
    df = df.drop_duplicates(subset="PK", keep="last").reset_index(drop=True)
    return df
