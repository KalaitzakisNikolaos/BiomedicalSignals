import os
import numpy as np
import pandas as pd
import nibabel as nib
import matplotlib.pyplot as plt
import seaborn as sns
from neuroCombat import neuroCombat
import glob
from scipy import stats
from scipy.interpolate import interp1d
import matplotlib.gridspec as gridspec

def extract_features_from_dataset(base_dir, dataset_name):
    """
    Extract features from all cases in a dataset
    
    Parameters:
    -----------
    base_dir : str
        Base directory path
    dataset_name : str
        Dataset name (e.g., "DUKE", "ISPY1", "ISPY2", "NACT")
    
    Returns:
    --------
    features_df : pandas.DataFrame
        DataFrame with extracted features
    """
    dataset_dir = os.path.join(base_dir, dataset_name)
    
    # Find colormap files
    colormap_files = glob.glob(os.path.join(dataset_dir, '**', '*_colormap.nii.gz'), recursive=True)
    
    features_list = []
    
    for colormap_file in colormap_files:
        # Extract case_id from filename
        case_id = os.path.basename(colormap_file).split('_colormap')[0]
        
        # Load colormap
        colormap = nib.load(colormap_file).get_fdata()
        
        # Extract basic statistical features
        n_voxels = np.sum(colormap > 0)
        n_uptake = np.sum(colormap == 1)
        n_plateau = np.sum(colormap == 2)
        n_washout = np.sum(colormap == 3)
        
        # Calculate percentages
        pct_uptake = (n_uptake / n_voxels) * 100 if n_voxels > 0 else 0
        pct_plateau = (n_plateau / n_voxels) * 100 if n_voxels > 0 else 0
        pct_washout = (n_washout / n_voxels) * 100 if n_voxels > 0 else 0
        
        features = {
            'case_id': case_id,
            'dataset': dataset_name,
            'n_voxels': n_voxels,
            'n_uptake': n_uptake,
            'n_plateau': n_plateau,
            'n_washout': n_washout,
            'pct_uptake': pct_uptake,
            'pct_plateau': pct_plateau,
            'pct_washout': pct_washout
        }
        
        features_list.append(features)
    
    return pd.DataFrame(features_list) if features_list else pd.DataFrame()

def combine_all_datasets(base_dir, datasets):
    """Combine features from all datasets"""
    all_features = []
    
    for dataset in datasets:
        print(f"Processing dataset: {dataset}")
        features = extract_features_from_dataset(base_dir, dataset)
        if not features.empty:
            all_features.append(features)
            print(f"  Found {len(features)} samples")
        else:
            print(f"  Warning: No data found for dataset {dataset}")
    
    return pd.concat(all_features, ignore_index=True) if all_features else pd.DataFrame()

def apply_combat_harmonization(data_df, feature_columns):
    """
    Apply ComBat harmonization with proper validation
    
    Parameters:
    -----------
    data_df : pandas.DataFrame
        DataFrame with features
    feature_columns : list
        Column names of features to harmonize
    
    Returns:
    --------
    harmonized_df : pandas.DataFrame
        DataFrame with harmonized features
    """
    # Check if we have enough data
    if len(data_df) < 5:
        print("Warning: Very few samples for ComBat harmonization")
        return data_df
    
    # Check batch sizes
    batch_counts = data_df['dataset'].value_counts()
    print("Batch sizes:")
    print(batch_counts)
    
    if any(batch_counts < 2):
        print("Warning: Some batches have very few samples")
    
    # Prepare data matrix (features x samples)
    data_matrix = data_df[feature_columns].values.T
    
    # Check for any missing or infinite values
    if np.any(np.isnan(data_matrix)) or np.any(np.isinf(data_matrix)):
        print("Warning: Found NaN or infinite values in data")
        data_matrix = np.nan_to_num(data_matrix)
    
    # Create covariates dataframe
    covars = pd.DataFrame({'batch': data_df['dataset'].values})
    
    print(f"Applying ComBat to {data_matrix.shape[0]} features across {data_matrix.shape[1]} samples")
    print(f"Batches: {covars['batch'].unique()}")
    
    try:
        # Apply neuroCombat
        combat_result = neuroCombat(
            dat=data_matrix,
            covars=covars,
            batch_col='batch',
            parametric=True,
            eb=True  # Empirical Bayes
        )
        
        harmonized_matrix = combat_result['data']
        
        # Create harmonized dataframe
        harmonized_df = data_df.copy()
        for i, feature in enumerate(feature_columns):
            harmonized_df[f'harmonized_{feature}'] = harmonized_matrix[i, :]
        
        print("ComBat harmonization completed successfully!")
        return harmonized_df
        
    except Exception as e:
        print(f"Error in ComBat harmonization: {e}")
        return data_df

def create_enhancement_curves():
    """Create enhancement curves for different tissue types (reference plot)"""
    time_points = np.array([0, 1, 2, 3])
    curves = {
        'Uptake': np.array([0, 75, 80, 75]),
        'Plateau': np.array([0, 75, 75, 70]),
        'Washout': np.array([0, 75, 65, 55])
    }
    return time_points, curves

def interpolate_curves(time_points, curves, num_points=100):
    """Interpolate curves for smoother plotting"""
    time_interp = np.linspace(0, 3, num_points)
    curves_interp = {}
    for name, values in curves.items():
        f = interp1d(time_points, values, kind='cubic')
        curves_interp[name] = f(time_interp)
    return time_interp, curves_interp

def plot_comprehensive_comparison(data_df, feature_columns, base_dir):
    """
    Create a comprehensive comparison plot with:
    - Reference pharmacokinetic curves
    - Before/after harmonization boxplots for each feature
    """
    # Ensure images directory exists
    images_dir = os.path.join(base_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    # Color and title mappings
    color_map = {
        'pct_uptake': 'royalblue',
        'pct_plateau': 'mediumseagreen',
        'pct_washout': 'tomato'
    }
    
    feature_titles = {
        'pct_uptake': 'Uptake',
        'pct_plateau': 'Plateau',
        'pct_washout': 'Washout'
    }
    
    # Set up the comprehensive figure
    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(2, 4, height_ratios=[1, 1.2], width_ratios=[1.2, 1, 1, 1])
    
    # Reference pharmacokinetic curves (top left)
    ax_ref = plt.subplot(gs[0, 0])
    time_points, curves = create_enhancement_curves()
    time_interp, curves_interp = interpolate_curves(time_points, curves)
    
    ax_ref.plot(time_interp, curves_interp['Uptake'], 'b-', linewidth=3, label='Uptake')
    ax_ref.plot(time_interp, curves_interp['Plateau'], 'g-', linewidth=3, label='Plateau')
    ax_ref.plot(time_interp, curves_interp['Washout'], 'r-', linewidth=3, label='Washout')
    
    ax_ref.axvline(x=2, color='gray', linestyle='--', alpha=0.7)
    ax_ref.axhline(y=70, color='gray', linestyle='-', alpha=0.5)
    ax_ref.text(2.1, 72, '±10%', fontsize=10)
    
    ax_ref.set_xlabel('Time-point', fontsize=12)
    ax_ref.set_ylabel('Signal Enhancement (%)', fontsize=12)
    ax_ref.set_xlim(0, 3)
    ax_ref.set_ylim(0, 130)
    ax_ref.grid(True, alpha=0.3)
    ax_ref.set_title('Reference Kinetic Curves', fontsize=14, fontweight='bold')
    
    # Add curve labels
    ax_ref.text(2.5, 85, 'Uptake', fontsize=11, color='blue', fontweight='bold')
    ax_ref.text(2.5, 75, 'Plateau', fontsize=11, color='green', fontweight='bold')
    ax_ref.text(2.5, 65, 'Washout', fontsize=11, color='red', fontweight='bold')
    
    # Summary statistics (top right)
    ax_stats = plt.subplot(gs[0, 1:])
    ax_stats.axis('off')
    
    # Calculate summary statistics
    stats_text = "Dataset Summary:\n\n"
    dataset_counts = data_df['dataset'].value_counts()
    for dataset, count in dataset_counts.items():
        stats_text += f"{dataset}: {count} samples\n"
    
    stats_text += f"\nTotal Samples: {len(data_df)}\n"
    stats_text += f"Total Datasets: {data_df['dataset'].nunique()}\n\n"
    
    # Add harmonization metrics if available
    if any(f'harmonized_{col}' in data_df.columns for col in feature_columns):
        stats_text += "Harmonization Status: ✓ Completed\n"
        metrics = calculate_harmonization_metrics(data_df, feature_columns)
        for feature, metric in metrics.items():
            if metric:
                reduction = metric.get('variance_reduction', 0)
                stats_text += f"{feature_titles.get(feature, feature)}: {reduction:.1%} variance reduction\n"
    else:
        stats_text += "Harmonization Status: ✗ Not applied\n"
    
    ax_stats.text(0.05, 0.95, stats_text, transform=ax_stats.transAxes, 
                  fontsize=12, verticalalignment='top', fontfamily='monospace',
                  bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
    
    # Feature comparison plots (bottom row)
    for i, feature in enumerate(feature_columns):
        if i >= 3:  # Limit to 3 features to fit in the grid
            break
            
        ax = plt.subplot(gs[1, i+1])
        color = color_map.get(feature, 'gray')
        title = feature_titles.get(feature, feature)
        
        # Check if harmonized data exists
        harmonized_col = f'harmonized_{feature}'
        if harmonized_col in data_df.columns:
            # Create side-by-side comparison
            width = 0.35
            datasets = data_df['dataset'].unique()
            x_pos = np.arange(len(datasets))
            
            # Original data
            orig_means = [data_df[data_df['dataset'] == d][feature].mean() for d in datasets]
            orig_stds = [data_df[data_df['dataset'] == d][feature].std() for d in datasets]
            
            # Harmonized data
            harm_means = [data_df[data_df['dataset'] == d][harmonized_col].mean() for d in datasets]
            harm_stds = [data_df[data_df['dataset'] == d][harmonized_col].std() for d in datasets]
            
            ax.bar(x_pos - width/2, orig_means, width, yerr=orig_stds, 
                   label='Original', color=color, alpha=0.7, capsize=5)
            ax.bar(x_pos + width/2, harm_means, width, yerr=harm_stds, 
                   label='Harmonized', color=color, alpha=1.0, capsize=5)
            
            ax.set_xlabel('Dataset', fontsize=11)
            ax.set_ylabel(f'{title} (%)', fontsize=11)
            ax.set_title(f'{title} Comparison', fontsize=12, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(datasets, rotation=45)
            ax.legend()
            ax.grid(True, alpha=0.3)
        else:
            # Only original data available
            sns.boxplot(data=data_df, x='dataset', y=feature, color=color, ax=ax)
            sns.stripplot(data=data_df, x='dataset', y=feature, ax=ax, 
                         color='black', alpha=0.6, size=4)
            ax.set_title(f'{title} Distribution', fontsize=12, fontweight='bold')
            ax.set_xlabel('Dataset', fontsize=11)
            ax.set_ylabel(f'{title} (%)', fontsize=11)
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout(pad=3.0)
    plt.savefig(os.path.join(images_dir, 'comprehensive_combat_analysis.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()

def plot_individual_feature_comparison(data_df, feature_columns, base_dir):
    """Create individual comparison plots for each feature"""
    images_dir = os.path.join(base_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    color_map = {
        'pct_uptake': 'royalblue',
        'pct_plateau': 'mediumseagreen',
        'pct_washout': 'tomato'
    }
    
    feature_titles = {
        'pct_uptake': 'Uptake Percentage',
        'pct_plateau': 'Plateau Percentage',
        'pct_washout': 'Washout Percentage'
    }
    
    for feature in feature_columns:
        harmonized_col = f'harmonized_{feature}'
        if harmonized_col not in data_df.columns:
            continue
            
        color = color_map.get(feature, 'gray')
        title = feature_titles.get(feature, feature)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Before harmonization
        sns.boxplot(data=data_df, x='dataset', y=feature, color=color, ax=ax1, showfliers=False)
        sns.stripplot(data=data_df, x='dataset', y=feature, ax=ax1, 
                     jitter=True, color='.25', alpha=0.6, size=5)
        ax1.set_title(f'Before Harmonization: {title}', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Dataset', fontsize=12)
        ax1.set_ylabel(f'{title} (%)', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # After harmonization
        sns.boxplot(data=data_df, x='dataset', y=harmonized_col, color=color, ax=ax2, showfliers=False)
        sns.stripplot(data=data_df, x='dataset', y=harmonized_col, ax=ax2, 
                     jitter=True, color='.25', alpha=0.6, size=5)
        ax2.set_title(f'After Harmonization: {title}', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Dataset', fontsize=12)
        ax2.set_ylabel(f'Harmonized {title} (%)', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(os.path.join(images_dir, f'combat_{feature}.png'), 
                    dpi=300, bbox_inches='tight')
        plt.close()

def calculate_harmonization_metrics(data_df, feature_columns):
    """Calculate metrics to evaluate harmonization quality"""
    metrics = {}
    
    for feature in feature_columns:
        harmonized_col = f'harmonized_{feature}'
        if harmonized_col not in data_df.columns:
            continue
            
        # Calculate between-batch variance before and after
        datasets = data_df['dataset'].unique()
        
        # Before harmonization
        batch_means_before = []
        for dataset in datasets:
            mask = data_df['dataset'] == dataset
            if mask.sum() > 0:
                batch_means_before.append(data_df.loc[mask, feature].mean())
        
        # After harmonization
        batch_means_after = []
        for dataset in datasets:
            mask = data_df['dataset'] == dataset
            if mask.sum() > 0:
                batch_means_after.append(data_df.loc[mask, harmonized_col].mean())
        
        # Calculate variance reduction
        var_before = np.var(batch_means_before) if len(batch_means_before) > 1 else 0
        var_after = np.var(batch_means_after) if len(batch_means_after) > 1 else 0
        
        # Calculate F-statistics (ANOVA)
        try:
            f_stat_before, p_val_before = stats.f_oneway(*[
                data_df.loc[data_df['dataset'] == dataset, feature].values 
                for dataset in datasets if (data_df['dataset'] == dataset).sum() > 0
            ])
            
            f_stat_after, p_val_after = stats.f_oneway(*[
                data_df.loc[data_df['dataset'] == dataset, harmonized_col].values 
                for dataset in datasets if (data_df['dataset'] == dataset).sum() > 0
            ])
        except:
            f_stat_before = f_stat_after = 0
            p_val_before = p_val_after = 1
        
        metrics[feature] = {
            'batch_variance_before': var_before,
            'batch_variance_after': var_after,
            'variance_reduction': (var_before - var_after) / var_before if var_before > 0 else 0,
            'f_stat_before': f_stat_before,
            'f_stat_after': f_stat_after,
            'p_value_before': p_val_before,
            'p_value_after': p_val_after
        }
    
    return metrics

def print_summary_statistics(data_df, feature_columns):
    """Print comprehensive summary statistics"""
    print("\n" + "="*60)
    print("DATASET SUMMARY STATISTICS")
    print("="*60)
    
    # Dataset distribution
    print(f"\nDataset Distribution:")
    dataset_counts = data_df['dataset'].value_counts()
    for dataset, count in dataset_counts.items():
        print(f"  {dataset}: {count} samples")
    print(f"  Total: {len(data_df)} samples across {data_df['dataset'].nunique()} datasets")
    
    # Feature statistics before harmonization
    print(f"\nFeature Statistics (Before Harmonization):")
    for feature in feature_columns:
        print(f"\n{feature.upper()}:")
        for dataset in data_df['dataset'].unique():
            subset = data_df[data_df['dataset'] == dataset][feature]
            print(f"  {dataset}: Mean={subset.mean():.2f}%, Std={subset.std():.2f}%")
    
    # Harmonization metrics
    if any(f'harmonized_{col}' in data_df.columns for col in feature_columns):
        print(f"\nHarmonization Metrics:")
        metrics = calculate_harmonization_metrics(data_df, feature_columns)
        for feature, metric in metrics.items():
            if metric:
                print(f"\n{feature.upper()}:")
                print(f"  Variance Reduction: {metric['variance_reduction']:.1%}")
                print(f"  F-statistic Before: {metric['f_stat_before']:.3f} (p={metric['p_value_before']:.3f})")
                print(f"  F-statistic After: {metric['f_stat_after']:.3f} (p={metric['p_value_after']:.3f})")
        
        # Feature statistics after harmonization
        print(f"\nFeature Statistics (After Harmonization):")
        for feature in feature_columns:
            harmonized_col = f'harmonized_{feature}'
            if harmonized_col in data_df.columns:
                print(f"\n{feature.upper()}:")
                for dataset in data_df['dataset'].unique():
                    subset = data_df[data_df['dataset'] == dataset][harmonized_col]
                    print(f"  {dataset}: Mean={subset.mean():.2f}%, Std={subset.std():.2f}%")

def main():
    """Main execution function"""
    print("="*60)
    print("ComBat Harmonization Pipeline")
    print("="*60)
    
    # Configuration
    base_dir = r'C:\Users\nickk\Music\BiomedicalSignals'
    datasets = ['DUKE', 'ISPY1', 'ISPY2', 'NACT']
    feature_columns = ['pct_uptake', 'pct_plateau', 'pct_washout']
    
    print("Starting ComBat harmonization pipeline...")
    print(f"Base directory: {base_dir}")
    print(f"Datasets: {', '.join(datasets)}")
    print(f"Features: {', '.join(feature_columns)}")
    
    # Extract and combine features from all datasets
    print("\nExtracting features from datasets...")
    combined_df = combine_all_datasets(base_dir, datasets)
    
    if combined_df.empty:
        print("ERROR: No data found in any dataset!")
        print("Please check the data directory structure and file paths.")
        return
    
    # Save raw features
    raw_path = os.path.join(base_dir, 'raw_features.csv')
    combined_df.to_csv(raw_path, index=False)
    print(f"\nRaw features saved to: {raw_path}")
    
    # Print initial statistics
    print_summary_statistics(combined_df, feature_columns)
    
    # Apply ComBat harmonization
    print("\n" + "="*60)
    print("APPLYING COMBAT HARMONIZATION")
    print("="*60)
    harmonized_df = apply_combat_harmonization(combined_df, feature_columns)
    
    # Save harmonized features
    harmonized_path = os.path.join(base_dir, 'harmonized_features.csv')
    harmonized_df.to_csv(harmonized_path, index=False)
    print(f"\nHarmonized features saved to: {harmonized_path}")
    
    # Print final statistics
    print_summary_statistics(harmonized_df, feature_columns)
    
    # Generate visualizations
    print("\n" + "="*60)
    print("GENERATING VISUALIZATIONS")
    print("="*60)
    
    print("Creating comprehensive comparison plot...")
    plot_comprehensive_comparison(harmonized_df, feature_columns, base_dir)
    
    print("Creating individual feature comparison plots...")
    plot_individual_feature_comparison(harmonized_df, feature_columns, base_dir)
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"✓ Processed {len(harmonized_df)} samples from {harmonized_df['dataset'].nunique()} datasets")
    print(f"✓ Raw features saved: {raw_path}")
    print(f"✓ Harmonized features saved: {harmonized_path}")
    print(f"✓ Visualization plots saved in: {os.path.join(base_dir, 'images')}")
    print("\nCheck the 'images' folder for detailed comparison plots!")

if __name__ == "__main__":
    main()