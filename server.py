import pickle
import numpy
import geopandas
import plotly.graph_objects as go
from shiny import render, reactive, Session, ui
from shinywidgets import render_widget


def server(input, output, session: Session):
    def load_data_dict():
        with open("data/data_dict.pkl", "rb") as f:
            data_dict = pickle.load(f)
        return data_dict

    def get_pk_and_elevation_array():
        data_dict = load_data_dict()
        elevation_array = data_dict["elevation_array"]
        pk_array = data_dict["pk_array"]
        return pk_array, elevation_array

    def get_baseline_slope():
        data_dict = load_data_dict()
        baseline_slope_array = data_dict["baseline_slope"]
        return baseline_slope_array

    @reactive.Calc
    def get_current_epsilon_data():
        data_dict = load_data_dict()
        epsilon_data = data_dict["rdp_epsilon"][input.rdp_epsilon()]
        return epsilon_data

    @reactive.Calc
    def get_rdp_points_kept():
        epsilon_data = get_current_epsilon_data()
        rdp_points_kept_array = epsilon_data["rdp_points_kept_array"]
        return rdp_points_kept_array

    @reactive.Calc
    def get_interpolated_rdp_slope():
        epsilon_data = get_current_epsilon_data()
        rpd_slope_interpolation = epsilon_data["rpd_slope_interpolation"]
        return rpd_slope_interpolation

    @reactive.Calc
    def get_string_epsion():
        return str(input.rdp_epsilon()).replace(".", "_")

    @render.download(
        filename=lambda: f"/Transects_Level_2_LBRUT_rdp_{get_string_epsion()}.csv"
    )
    def download_csv_file():
        with ui.Progress(min=0, max=2) as p:
            p.set(1, message="Computing")
            df = geopandas.read_file("data/shp/Transects_Level_2_LBRUT.shp")
            rdp_points_kept_array = get_rdp_points_kept()
            baseline_slope_array = get_baseline_slope()
            rpd_slope_interpolation = get_interpolated_rdp_slope()
            df["elev_rdp"] = numpy.nan
            df["base_slope"] = numpy.nan
            df["rdp_slope"] = numpy.nan
            for pk, elevation in rdp_points_kept_array:
                df.loc[df["PK"] == pk, "elev_rdp"] = elevation
            for pk, slope in baseline_slope_array:
                df.loc[df["PK"] == pk, "base_slope"] = slope
            for pk, slope in rpd_slope_interpolation:
                df.loc[df["PK"] == pk, "rdp_slope"] = slope
            yield df.to_csv()
            p.set(1, message="File downloaded")

    @render_widget
    def generate_subset_rdp_points_plot():
        pk_array, elevation_array = get_pk_and_elevation_array()
        rdp_points_kept_array = get_rdp_points_kept()
        rdp_points_kept_array = get_rdp_points_kept()
        nb_points_original = len(pk_array)
        nb_points_kept = rdp_points_kept_array.shape[0]
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=pk_array,
                y=elevation_array,
                mode="lines+markers",
                name=f"Profil d'élévation original n={nb_points_original}",
            )
        )
        fig.update_traces(marker=dict(size=4))
        fig.add_trace(
            go.Scatter(
                x=rdp_points_kept_array[:, 0],
                y=rdp_points_kept_array[:, 1],
                mode="lines+markers",
                name=f"Profil d'élévation rdp n={nb_points_kept}",
            )
        )
        fig.update_layout(
            yaxis=dict(title="Élévation (m)"),
            xaxis=dict(title="Point Kilométrique (m)"),
            title="Élévation selon le point kilométrique",
            height=600,
        )
        return fig

    @reactive.Calc
    def get_max_y_slope():
        return input.max_y_slope()

    @render_widget
    def generate_slope_plot():
        # fig, axs = plt.subplots(3, 1, sharex=True)
        # baseline_slope_array = get_baseline_slope()
        # rpd_slope_interpolation = get_interpolated_rdp_slope()
        # axs[0].plot(baseline_slope_array[:, 0], baseline_slope_array[:, 1], label="baseline_slope", color="#ff7f0e")
        # axs[1].plot(rpd_slope_interpolation[:, 0], rpd_slope_interpolation[:, 1], label="rdp_slope", color="#1f77b4")
        # axs[2].plot(baseline_slope_array[:, 0], baseline_slope_array[:, 1], label="baseline_slope", color="#ff7f0e")
        # axs[2].plot(rpd_slope_interpolation[:, 0], rpd_slope_interpolation[:, 1], label="rdp_slope", alpha=0.7, color="#1f77b4")
        # axs[2].set_xlabel("Point Kilométrique (m)")
        # for ax in axs:
        #     ax.set_ylabel("Pente")
        #     ax.set_ylim(0, get_max_y_slope())
        #     ax.legend()
        # plt.suptitle("Pente selon le point kilométrique", y=0.92)
        # plt.tight_layout()
        # return fig
        baseline_slope_array = get_baseline_slope()
        rpd_slope_interpolation = get_interpolated_rdp_slope()
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=baseline_slope_array[:, 0],
                y=baseline_slope_array[:, 1],
                mode="lines+markers",
                name="Pente de référence",
            )
        )
        fig.update_traces(marker=dict(size=4))
        fig.add_trace(
            go.Scatter(
                x=rpd_slope_interpolation[:, 0],
                y=rpd_slope_interpolation[:, 1],
                mode="lines+markers",
                name="Pente rdp",
            )
        )
        fig.update_layout(
            yaxis=dict(title="Élévation (m)"),
            xaxis=dict(title="Point Kilométrique (m)"),
            title="Élévation selon le point kilométrique",
            height=600,
        )
        return fig
