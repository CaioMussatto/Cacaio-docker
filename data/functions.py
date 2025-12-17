import numpy as np
import pandas as pd
import dcor
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import gseapy as gp
import textwrap
import harmonypy as hm


def compare_centroids_distance_correlation_from_df(
    df: pd.DataFrame,
    sample_col: str = 'sample',
    dataset_col: str = 'dataset'
):
    """
    Compute distance correlation between sample centroids in a PCA/Harmony space
    provided as a DataFrame, using pre‑computed embeddings.

    Rule: dataset == 'CCLE' is cell line; else tumor.

    Args:
        df: DataFrame with columns for PCs (pc_cols), plus sample_col and dataset_col.
        sample_col: name of the column with sample IDs.
        dataset_col: name of the column with dataset labels (e.g. 'CCLE' or other).

    Returns:
        centroid_df: DataFrame with distance correlation matrix
                     (CCLE samples × Tumor samples).
        best_match: dict with keys 'CCLE', 'Tumor', 'Correlation' for the best pair.
    """
    pc_cols = [c for c in df.columns if c.startswith('PC')]
    emb = df[pc_cols + [sample_col, dataset_col]].copy()
    centroids = (
        emb
        .groupby(sample_col, observed=True)[pc_cols]
        .mean()
    )

    sample_to_ds = (
        emb
        .drop_duplicates(sample_col)
        .set_index(sample_col)[dataset_col]
    )

    ccle_centroids  = centroids.loc[sample_to_ds == 'CCLE']
    tumor_centroids = centroids.loc[sample_to_ds != 'CCLE']

    if ccle_centroids.empty or tumor_centroids.empty:
        raise ValueError("No CCLE or Tumor samples found with given criteria.")

    centroid_df = pd.DataFrame(
        index=ccle_centroids.index,
        columns=tumor_centroids.index,
        dtype=float
    )

    for ccle_s in tqdm(ccle_centroids.index, desc="Calculating distance correlations"):
        v1 = ccle_centroids.loc[ccle_s].values
        for tum_s in tumor_centroids.index:
            v2 = tumor_centroids.loc[tum_s].values
            try:
                centroid_df.at[ccle_s, tum_s] = dcor.distance_correlation(v1, v2)
            except Exception:
                centroid_df.at[ccle_s, tum_s] = np.nan

    clean = centroid_df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    if clean.empty:
        raise ValueError("Distance correlation matrix is empty after cleaning.")

    max_idx = clean.stack().idxmax()
    best_match = {
        'CCLE':       max_idx[0],
        'Tumor':      max_idx[1],
        'Correlation': clean.loc[max_idx]
    }

    return centroid_df, best_match

def convert_to_long_format(centroid_df):
    """
    Converte o DataFrame wide para formato longo com colunas:
    CCLE, Primary Tumor, Distance Correlation
    """
    long_df = centroid_df.reset_index()
    
    index_col_name = long_df.columns[0]
    
    long_df = long_df.melt(
        id_vars=index_col_name, 
        var_name='Primary Tumor', 
        value_name='Distance Correlation'
    )
    
    long_df = long_df.rename(columns={index_col_name: 'CCLE'})
    
    long_df = long_df.dropna(subset=['Distance Correlation'])
    return long_df.sort_values('Distance Correlation', ascending=False)

def plot_correlation_heatmap(centroid_matrix):
    """
    Plot a correlation heatmap.
    
    Parameters:
    -----------
    centroid_matrix : array-like
        Matrix data for the heatmap
    """
    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(
        centroid_matrix,
        cmap='rocket',
        linecolor="lightgray",
        cbar_kws={"label": "Distance Correlation"},
        xticklabels=True,
        yticklabels=True
    )

    plt.xlabel("Tumor Samples", fontdict={'weight': 'bold'}, fontsize=10)
    plt.ylabel("CCLE Samples", fontdict={'weight': 'bold'}, fontsize=10)
    plt.xticks(fontsize=8, ha='right')
    plt.yticks(fontsize=8)

    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=14)
    cbar.set_label('Distance Correlation', fontsize=10, weight='bold')

    plt.tight_layout()
    
def run_enrichment_analysis(gene_list, libraries, organism='human'):
    """
    Run enrichment analysis using Enrichr
    """
    enr = gp.enrichr(
        gene_list=gene_list, 
        gene_sets=libraries,
        organism=organism, 
        outdir=None
    )
    return enr.results[['Term', 'Overlap', 'P-value', 'Combined Score', 'Adjusted P-value']]

def create_horizontal_barplot(df):
    """
    Create horizontal bar plot for enrichment results
    """
    top = df.sort_values('Adjusted P-value', ascending=True).head(10).copy()
    
    top['-log10(Adjusted P-value)'] = -np.log10(top['Adjusted P-value'])
    
    top['Term_wrapped'] = top['Term'].apply(lambda x: '\n'.join(textwrap.wrap(x, width=25)))
    
    plt.figure(figsize=(8, 6))
    sns.barplot(
        data=top,
        x='-log10(Adjusted P-value)',
        y='Term_wrapped',
        dodge=False,
        hue="Combined Score",
        palette="rocket"
    )
    plt.xlabel(r'$-\log_{10}$ (Adjusted P-value)', fontsize=6, fontweight='bold')
    plt.yticks(fontsize=8, fontweight='bold', rotation=0)
    plt.ylabel('')
    plt.tight_layout()
    return plt.gcf()


def cross_modal_harmony_embeddings_from_df(
    df_pca: pd.DataFrame,
    bulk_df: pd.DataFrame,
    scaler,
    pca,
    hvg_genes: list,
    sample_col: str = 'sample',
    theta: float = 0.0,
    sigma: float = 0.2,
    n_pcs: int = 50
):
    pc_cols = [f"PC{i+1}" for i in range(n_pcs)]
    pseudo_centroids = df_pca.groupby(sample_col, observed=True)[pc_cols].mean()

    bulk_mat = bulk_df.reindex(columns=hvg_genes, fill_value=0).values
    bulk_pca = pca.transform(scaler.transform(bulk_mat))
    bulk_pca_df = pd.DataFrame(bulk_pca, index=bulk_df.index, columns=pc_cols)

    comb = pd.concat([pseudo_centroids, bulk_pca_df], axis=0)
    batch = ['scRNA'] * len(pseudo_centroids) + ['bulk'] * len(bulk_pca_df)
    meta = pd.DataFrame({'batch': batch}, index=comb.index)

    n_clusters = pseudo_centroids.shape[0]

    sigma_arr = np.full((n_clusters,), sigma)

    ho = hm.run_harmony(
        comb.values,
        meta,
        vars_use='batch',
        theta=theta,
        sigma=sigma_arr,
        nclust=n_clusters,
        verbose=False
    )

    Z = ho.Z_corr.T
    harmony_cols = [f"HarmonyPC{i+1}" for i in range(n_pcs)]
    emb_h = pd.DataFrame(Z, index=comb.index, columns=harmony_cols)

    pseudo_h = emb_h.loc[pseudo_centroids.index]
    bulk_h = emb_h.loc[bulk_pca_df.index]

    return pseudo_h, bulk_h

def compute_distance_correlation_matrix(pseudo_h: pd.DataFrame, bulk_h: pd.DataFrame):
    """
    Compute distance correlation between each bulk sample and each pseudo-bulk centroid
    """
    dcorr_df = pd.DataFrame(
        index=bulk_h.index,
        columns=pseudo_h.index,
        dtype=float
    )

    for b in tqdm(bulk_h.index, desc="Calculating distance correlations"):
        v_bulk = bulk_h.loc[b].values.astype(np.float64)
        for p in pseudo_h.index:
            v_pseudo = pseudo_h.loc[p].values.astype(np.float64)
            try:
                dc = dcor.distance_correlation(v_bulk, v_pseudo)
            except Exception:
                dc = np.nan
            dcorr_df.at[b, p] = dc

    best_match = {
        b: (dcorr_df.loc[b].idxmax(), dcorr_df.loc[b].max())
        for b in dcorr_df.index
    }

    return dcorr_df, best_match

def convert_cross_modal_to_long(correlation_matrix):
    """
    Converts the cross-modal correlation matrix to long format
    """
    long_df = correlation_matrix.reset_index()
    index_col_name = long_df.columns[0]
    
    long_df = long_df.melt(
        id_vars=index_col_name,
        var_name='Pseudo_Centroid',
        value_name='Distance_Correlation'
    )
    
    long_df = long_df.rename(columns={index_col_name: 'Bulk_Sample'})
    long_df = long_df.dropna(subset=['Distance_Correlation'])
    return long_df.sort_values('Distance_Correlation', ascending=False)

def plot_top_combinations(correlation_matrix, filter_type, sample_types, top_n=5):
    long_data = convert_cross_modal_to_long(correlation_matrix)
    
    long_data['sample_type'] = long_data['Pseudo_Centroid'].map(sample_types)
    
    if filter_type == "primary_tumor":
        long_data = long_data[long_data['sample_type'] == 'primary_tumor']
    elif filter_type == "cell_line":
        long_data = long_data[long_data['sample_type'] == 'cell_line']
    
    top_combinations = long_data.nlargest(top_n, 'Distance_Correlation')
    
    labels = []
    for _, row in top_combinations.iterrows():
        bulk = row['Bulk_Sample']
        pseudo = row['Pseudo_Centroid']
        labels.append(f"{bulk}\nvs\n{pseudo}")
    
    plt.figure(figsize=(10, 8))
    
    colors = sns.color_palette("rocket", len(top_combinations))
    
    bars = plt.barh(
        labels,
        top_combinations['Distance_Correlation'],
        color=colors,
        edgecolor='black',
        linewidth=0.5,
        alpha=0.9
    )
    
    for i, (bar, value) in enumerate(zip(bars, top_combinations['Distance_Correlation'])):
        width = bar.get_width()
        plt.text(width + 0.005, bar.get_y() + bar.get_height()/2, 
                f'{value:.4f}', 
                ha='left', va='center', 
                fontweight='bold', 
                fontsize=6,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
    
    plt.xlabel('Distance Correlation', fontsize=8, fontweight='bold')
    plt.ylabel('Sample Combinations', fontsize=8, fontweight='bold')
    plt.title(f'Top {top_n} Cross-Modal Correlations\n(Bulk Samples vs Pseudo Centroids)', 
              fontsize=10, fontweight='bold')
    plt.yticks(fontsize=6)
    
    plt.axvline(x=0, color='grey', linewidth=0.8)
    plt.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.xlim(0, min(1.0, top_combinations['Distance_Correlation'].max() * 1.15))
    plt.gca().invert_yaxis()
    
    plt.tight_layout()
    
    return plt.gcf()