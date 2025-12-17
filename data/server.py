from shiny import Inputs, Outputs, Session, reactive, render, ui
import asyncio
import pandas as pd
from io import StringIO
from functions import (
    compare_centroids_distance_correlation_from_df,
    plot_correlation_heatmap,
    convert_to_long_format,
    run_enrichment_analysis,
    create_horizontal_barplot,
    plot_top_combinations,
    compute_distance_correlation_matrix,
    cross_modal_harmony_embeddings_from_df,
    convert_cross_modal_to_long,


)
from data import sc_samples, degs


def server(input, output, session):
    
    processed_data = reactive.Value(None)
    
    @reactive.Effect
    @reactive.event(input.run_analysis)
    def _():
        if not input.dataset_choice():
            return None
        
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")
            
            for i in range(1, 15):
                p.set(i, message="Processing...")
                reactive.flush()
                
            selected_data = sc_samples[input.dataset_choice()]['df_pca_harmony']
            centroid_df, best_match = compare_centroids_distance_correlation_from_df(selected_data)
            processed_data.set(centroid_df)

    @output
    @render.data_frame
    def results_table():
        data = processed_data()
        if data is not None:
            long_data = convert_to_long_format(data)
            return render.DataTable(
                long_data.round(5),
                filters=True,
                width="100%",
                height="400px"
            )
        return None

    @output
    @render.plot
    def heatmap_plot():
        data = processed_data()
        if data is not None:
            return plot_correlation_heatmap(data)
        return None

    @render.download(
        filename=lambda: f"similarity_analysis_{input.dataset_choice() or 'data'}.csv"
    )
    def download_table():
        data = processed_data()
        if data is not None:
            long_data = convert_to_long_format(data)
            csv_buffer = StringIO()
            long_data.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            yield csv_buffer.getvalue()
    enrichment_results = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.degs_choice)
    def _():
        if input.degs_choice() and input.degs_choice() in degs:
            contrasts = list(degs[input.degs_choice()].keys())
            ui.update_selectize(
                "contrast_choice",
                choices=contrasts
            )

    @reactive.Effect
    @reactive.event(input.run_enrichment)
    def _():
        if (not input.degs_choice() or 
            not input.contrast_choice() or 
            not input.library_choice()):
            return None
        
        with ui.Progress(min=1, max=10) as p:
            p.set(message="Running enrichment analysis...", detail="This may take a while...")
            
            for i in range(1, 10):
                p.set(i, message="Processing...")
                reactive.flush()
            
            gene_list = degs[input.degs_choice()][input.contrast_choice()]['gene']
            
            results = run_enrichment_analysis(
                gene_list=gene_list,
                libraries=input.library_choice(),
                organism='human'
            )
            
            enrichment_results.set(results)

    @output
    @render.data_frame
    def enrichment_table():
        data = enrichment_results()
        if data is not None:
            return render.DataTable(
                data.round(5),
                filters=True,
                width="100%",
                height="400px"
            )
        return None

    @output
    @render.plot
    def enrichment_plot():
        data = enrichment_results()
        if data is not None:
            return create_horizontal_barplot(data)
        return None

    @render.download(
        filename=lambda: f"enrichment_analysis_{input.degs_choice()}_{input.contrast_choice()}.csv"
    )
    def download_enrichment():
        data = enrichment_results()
        if data is not None:
            csv_buffer = StringIO()
            data.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            yield csv_buffer.getvalue()
    
    cross_modal_results = reactive.Value(None)
    sample_types_reactive = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.run_cross_modal)
    def _():
        if not input.cross_modal_cancer() or not input.bulk_upload():
            return None
        
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Processing cross-modal integration...", detail="This may take a while...")
            
            for i in range(1, 15):
                p.set(i, message="Processing...")
                reactive.flush()
            
            bulk_file = input.bulk_upload()[0]
            bulk_df = pd.read_csv(bulk_file['datapath'], index_col=0)
            
            sc_data = sc_samples[input.cross_modal_cancer()]
            
            pseudo_h, bulk_h = cross_modal_harmony_embeddings_from_df(
                df_pca=sc_data['df_pca'],
                bulk_df=bulk_df,
                scaler=sc_data['scaler'],  
                pca=sc_data['pca'],       
                hvg_genes=sc_data['hv_genes'],
                sigma=0.1
            )
            
            dc_matrix, best_match = compute_distance_correlation_matrix(pseudo_h, bulk_h)
            
            sample_to_ds = sc_data['df_pca'].drop_duplicates('sample').set_index('sample')['dataset']
            sample_types = sample_to_ds.apply(lambda x: 'cell_line' if x == 'CCLE' else 'primary_tumor')
            
            cross_modal_results.set({
                'matrix': dc_matrix,
                'best_match': best_match
            })
            sample_types_reactive.set(sample_types)

    @output
    @render.data_frame
    def cross_modal_table():
        data = cross_modal_results()
        if data is not None:
            matrix = data['matrix']
            long_data = convert_cross_modal_to_long(matrix)
            return render.DataTable(
                long_data.round(5),
                filters=True,
                width="100%",
                height="400px"
            )
        return None

    @output
    @render.plot
    def cross_modal_plot():
        data = cross_modal_results()
        sample_types = sample_types_reactive()
        if data is not None and sample_types is not None:
            matrix = data['matrix']
            return plot_top_combinations(matrix, input.filter_type(), sample_types, top_n=5)
        return None

    @render.download(
        filename=lambda: f"cross_modal_integration_{input.cross_modal_cancer()}.csv"
    )
    def download_cross_modal():
        data = cross_modal_results()
        if data is not None:
            matrix = data['matrix']
            long_data = convert_cross_modal_to_long(matrix)
            csv_buffer = StringIO()
            long_data.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            yield csv_buffer.getvalue()