from shiny import ui
from data import sc_samples, degs, libraries

gear_fill = ui.HTML(
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-gear-fill" viewBox="0 0 16 16"><path d="M9.405 1.05c-.413-1.4-2.397-1.4-2.81 0l-.1.34a1.464 1.464 0 0 1-2.105.872l-.31-.17c-1.283-.698-2.686.705-1.987 1.987l.169.311c.446.82.023 1.841-.872 2.105l-.34.1c-1.4.413-1.4 2.397 0 2.81l.34.1a1.464 1.464 0 0 1 .872 2.105l-.17.31c-.698 1.283.705 2.686 1.987 1.987l.311-.169a1.464 1.464 0 0 1 2.105.872l.1.34c.413 1.4 2.397 1.4 2.81 0l.1-.34a1.464 1.464 0 0 1 2.105-.872l.31.17c1.283.698 2.686-.705 1.987-1.987l-.169-.311a1.464 1.464 0 0 1 .872-2.105l.34-.1c1.4-.413 1.4-2.397 0-2.81l-.34-.1a1.464 1.464 0 0 1-.872-2.105l.17-.31c.698-1.283-.705-2.686-1.987-1.987l-.311.169a1.464 1.464 0 0 1-2.105-.872l-.1-.34zM8 10.93a2.929 2.929 0 1 1 0-5.86 2.929 2.929 0 0 1 0 5.858z"/></svg>'
)


app_ui = ui.page_fluid(
    ui.tags.style("""
        .btn-custom-height {
            height: 100px !important;
            padding-top: 8px !important;
            padding-bottom: 8px !important;
        }
    """),
    ui.navset_card_tab(
        ui.nav_panel(
            "Similarity Analysis",
            ui.layout_columns(
                ui.card(
                    ui.input_select(
                        "dataset_choice",
                        "Select Dataset:",
                        choices=list(sc_samples.keys()),
                        multiple=False
                    ),
                ),
                ui.input_action_button("run_analysis", "Run Analysis", width="100%", class_="btn-custom-height"),
                ui.card(
                    ui.download_button("download_table", "Download Table", class_="btn-primary"),
                    ui.output_data_frame("results_table"),
                    full_screen=True
                ),
                ui.card(
                    "Heatmap Visualization",
                    ui.output_plot("heatmap_plot", height="400px"),
                    full_screen=True
                ),
                col_widths=[8, 2, 6, 6]
            )
        ),
        ui.nav_panel(
            "Enrichment Analysis",
            ui.layout_columns(
                ui.card(
                    ui.layout_columns(
                        ui.input_select(
                            "degs_choice",
                            "DEGs Dataset:",
                            choices=list(degs.keys()),
                            multiple=False
                        ),
                        ui.input_select(
                            "contrast_choice", 
                            "Contrast:",
                            choices=[],
                            multiple=False
                        ),
                        ui.input_select(
                            "library_choice",
                            "Libraries:",
                            choices=libraries,
                            multiple=False
                        ),
                        col_widths=[4, 4, 4],
                    ),
                ),
                ui.input_action_button("run_enrichment", "Run Enrichment", width="100%", class_="btn-custom-height"),
                ui.card(
                    ui.download_button("download_enrichment", "Download Results", class_="btn-primary"),
                    ui.output_data_frame("enrichment_table"),
                    full_screen=True
                ),
                ui.card(
                    "Enrichment Plot",
                    ui.output_plot("enrichment_plot", height="400px"),
                    full_screen=True
                ),
                col_widths=[9, 2, 6, 6]
            )
        ),
        ui.nav_panel(
            "Cross-Modal Integration", 
            ui.layout_columns(
                ui.card(
                    ui.input_select(
                        "cross_modal_cancer",
                        "Cancer Dataset:",
                        choices=list(sc_samples.keys()),
                        multiple=False
                    ),
                ),
                ui.card(
                    ui.input_file(
                        "bulk_upload",
                        "Upload Bulk Data:",
                        accept=[".csv"]
                    )),
                ui.input_action_button("run_cross_modal", "Run Integration", width="100%", class_="btn-custom-height"),
                ui.card(
                    ui.download_button("download_cross_modal", "Download Matrix", class_="btn-primary"),
                    ui.output_data_frame("cross_modal_table"),
                    full_screen=True
                ),
                ui.card(
                    ui.card_header(
                        "Top Correlations",
                        ui.popover(
                            ui.span(
                                gear_fill,
                                style="position:absolute; top: 5px; right: 7px; cursor: pointer;",
                            ),
                            ui.input_select(
                                "filter_type",
                                "Filter Combinations:",
                                choices={
                                    "all": "All Combinations",
                                    "primary_tumor": "Primary Tumors vs Bulk",
                                    "cell_line": "Cell Lines vs Bulk"
                                },
                                selected="all"
                            ),
                            title="Filter Options",
                            placement="left",
                            id="card_popover",
                        ),
                    ),
                    ui.output_plot("cross_modal_plot", height="400px"),
                    full_screen=True
                ),
                col_widths=[4, 4, 2, 6, 6]
            )
        )
    )
)