from shiny import ui
from shinywidgets import output_widget


ui_main = ui.page_fluid(
    ui.h1("Exploration de l'algorithme de Ramer-Douglas-Peucker"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_numeric(
                "rdp_epsilon",
                "Epsilon de Ramer-Douglas-Peucker",
                min=0,
                max=1,
                step=0.01,
                value=0.1,
            ),
            ui.download_button("download_csv_file", "Download csv file"),
            width=350,
        ),
        output_widget(
            "generate_subset_rdp_points_plot",
            # width="900px",
            # height="600px",
        ),
        output_widget(
            "generate_slope_plot",
            # width="900px",
            # height="900px",
        ),
    ),
)
