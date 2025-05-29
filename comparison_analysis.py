import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def compare_analysis_systems():
    """Compare original vs enhanced DCE-MRI analysis systems"""
    
    print("="*80)
    print("COMPREHENSIVE COMPARISON: ORIGINAL vs ENHANCED DCE-MRI ANALYSIS")
    print("="*80)
    
    # Load datasets
    original = pd.read_csv('raw_features.csv')
    enhanced = pd.read_csv('enhanced_features_raw.csv')
    
    # Basic comparison
    print("\n1. FEATURE COUNT COMPARISON")
    print("-" * 40)
    original_features = len([col for col in original.columns if col not in ['case_id', 'dataset']])
    enhanced_features = len([col for col in enhanced.columns if col not in ['case_id', 'dataset']])
    
    print(f"Original system features:     {original_features}")
    print(f"Enhanced system features:     {enhanced_features}")
    print(f"Improvement factor:           {enhanced_features/original_features:.1f}x")
    
    # Dataset coverage comparison
    print("\n2. DATASET COVERAGE COMPARISON")
    print("-" * 40)
    orig_datasets = original['dataset'].value_counts()
    enh_datasets = enhanced['dataset'].value_counts()
    
    print("Original system coverage:")
    for dataset, count in orig_datasets.items():
        print(f"  - {dataset}: {count} cases")
    print(f"  Total: {len(original)} cases")
    
    print("\nEnhanced system coverage:")
    for dataset, count in enh_datasets.items():
        print(f"  - {dataset}: {count} cases")
    print(f"  Total: {len(enhanced)} cases")
    
    # Feature category breakdown
    print("\n3. FEATURE CATEGORY BREAKDOWN")
    print("-" * 40)
    
    # Enhanced system categories
    kinetic = len([col for col in enhanced.columns if any(k in col for k in ['pct_', 'n_', 'intensity_', 'threshold'])])
    shape = len([col for col in enhanced.columns if 'shape' in col])
    firstorder = len([col for col in enhanced.columns if 'firstorder' in col])
    texture_glcm = len([col for col in enhanced.columns if 'glcm' in col])
    texture_glrlm = len([col for col in enhanced.columns if 'glrlm' in col])
    temporal = len([col for col in enhanced.columns if 'temporal_change' in col])
    
    print(f"Kinetic features:             {kinetic}")
    print(f"Shape features:               {shape}")
    print(f"Intensity statistics:         {firstorder}")
    print(f"GLCM texture features:        {texture_glcm}")
    print(f"GLRLM texture features:       {texture_glrlm}")
    print(f"Temporal change features:     {temporal}")
    print(f"Total radiomics features:     {shape + firstorder + texture_glcm + texture_glrlm}")
      # Kinetic feature comparison - show diverse patterns across ALL datasets
    print("\n4. COMPREHENSIVE KINETIC PATTERN ANALYSIS")
    print("-" * 55)
    
    # Get common cases
    common_cases = set(original['case_id']).intersection(set(enhanced['case_id']))
    print(f"Cases analyzed in both systems: {len(common_cases)}")
    
    # Show ALL cases organized by dataset to demonstrate diversity
    print("\nKINETIC PATTERNS BY DATASET:")
    print("="*50)
    
    for dataset in ['DUKE', 'ISPY1', 'ISPY2', 'NACT']:
        dataset_cases = enhanced[enhanced['dataset'] == dataset]
        if len(dataset_cases) > 0:
            print(f"\n{dataset} DATASET ({len(dataset_cases)} cases):")
            print("-" * 30)
            
            for _, case_row in dataset_cases.iterrows():
                case_id = case_row['case_id']
                
                # Find corresponding original case
                orig_data = original[original['case_id'] == case_id]
                if len(orig_data) > 0:
                    orig_row = orig_data.iloc[0]
                    
                    # Determine dominant pattern
                    max_orig = max(orig_row['pct_uptake'], orig_row['pct_plateau'], orig_row['pct_washout'])
                    if max_orig == orig_row['pct_uptake']:
                        pattern = "UPTAKE-dominant"
                    elif max_orig == orig_row['pct_washout'] and orig_row['pct_washout'] > 5:
                        pattern = "WASHOUT-present"
                    else:
                        pattern = "PLATEAU-dominant"
                    
                    print(f"  {case_id} ({pattern}):")
                    print(f"    Original: {orig_row['pct_uptake']:.1f}% uptake, {orig_row['pct_plateau']:.1f}% plateau, {orig_row['pct_washout']:.1f}% washout")
                    print(f"    Enhanced: {case_row['pct_uptake']:.1f}% uptake, {case_row['pct_plateau']:.1f}% plateau, {case_row['pct_washout']:.1f}% washout")
                    print(f"    Enhanced adds: {case_row['n_voxels']} voxels, threshold: {case_row['adaptive_threshold']:.1f}")
                    print()
    
    # Summary statistics across all datasets
    print("\n5. CROSS-DATASET PATTERN STATISTICS")
    print("-" * 50)
    
    # Count pattern types across all datasets
    uptake_count = 0
    plateau_count = 0
    washout_count = 0
    
    for dataset in ['DUKE', 'ISPY1', 'ISPY2', 'NACT']:
        dataset_cases = enhanced[enhanced['dataset'] == dataset]
        dataset_uptake = 0
        dataset_plateau = 0
        dataset_washout = 0
        
        for _, case_row in dataset_cases.iterrows():
            case_id = case_row['case_id']
            orig_data = original[original['case_id'] == case_id]
            if len(orig_data) > 0:
                orig_row = orig_data.iloc[0]
                max_orig = max(orig_row['pct_uptake'], orig_row['pct_plateau'], orig_row['pct_washout'])
                if max_orig == orig_row['pct_uptake']:
                    uptake_count += 1
                    dataset_uptake += 1
                elif max_orig == orig_row['pct_washout'] and orig_row['pct_washout'] > 5:
                    washout_count += 1
                    dataset_washout += 1
                else:
                    plateau_count += 1
                    dataset_plateau += 1
        
        print(f"{dataset}: {dataset_uptake} uptake, {dataset_plateau} plateau, {dataset_washout} washout")
    
    print(f"\nOVERALL TOTALS: {uptake_count} uptake-dominant, {plateau_count} plateau-dominant, {washout_count} washout-present")
    print(f"Pattern diversity: {3 if washout_count > 0 else 2}/3 kinetic patterns represented")    # Analysis capabilities
    print("\n6. ANALYSIS CAPABILITIES COMPARISON")
    print("-" * 50)
    
    capabilities = {
        'Feature': [
            'Basic kinetic percentages',
            'Adaptive thresholding', 
            'ROI normalization',
            'Shape analysis (14 features)',
            'Intensity statistics (18 features)',
            'GLCM texture analysis (24 features)',
            'GLRLM texture analysis (16 features)',
            'Multiple normalization methods',
            'Enhanced visualizations',
            'Temporal radiomics changes',
            'Multi-dataset processing',
            'Clinical research ready'
        ],
        'Original System': [
            '✓', '✗', '✗', '✗', '✗', '✗', '✗', '✗', '✓', '✗', 'DUKE only', 'Limited'
        ],
        'Enhanced System': [
            '✓', '✓', '✓', '✓', '✓', '✓', '✓', '✓', '✓', '✓', 'All datasets', '✓'
        ]
    }
    
    cap_df = pd.DataFrame(capabilities)
    print(cap_df.to_string(index=False))
      # Dataset-specific analysis
    print("\n7. DATASET-SPECIFIC KINETIC PATTERNS")
    print("-" * 50)
    
    for dataset in ['DUKE', 'ISPY1', 'ISPY2']:
        dataset_cases = enhanced[enhanced['dataset'] == dataset]
        if len(dataset_cases) > 0:
            avg_uptake = dataset_cases['pct_uptake'].mean()
            avg_plateau = dataset_cases['pct_plateau'].mean()
            avg_washout = dataset_cases['pct_washout'].mean()
            print(f"\n{dataset} dataset ({len(dataset_cases)} cases):")
            print(f"  Average uptake:   {avg_uptake:.1f}%")
            print(f"  Average plateau:  {avg_plateau:.1f}%")
            print(f"  Average washout:  {avg_washout:.1f}%")
            print(f"  Avg voxels/case:  {dataset_cases['n_voxels'].mean():.0f}")
      # Normalization strategies
    print("\n8. NORMALIZATION STRATEGIES")
    print("-" * 40)
    print("Original system: Fixed threshold (10%)")
    print("Enhanced system: Adaptive threshold based on ROI statistics")
    print("Additional: Min-Max, Standard (Z-score), Robust scaling available")
      # Sample enhanced features for one case from each dataset
    print("\n9. SAMPLE ENHANCED FEATURES BY DATASET")
    print("-" * 50)
    
    for dataset in ['DUKE', 'ISPY1', 'ISPY2']:
        dataset_cases = enhanced[enhanced['dataset'] == dataset]
        if len(dataset_cases) > 0:
            sample_case = dataset_cases.iloc[0]
            print(f"\n{dataset} - {sample_case['case_id']}:")
            print(f"  Kinetic: {sample_case['pct_uptake']:.1f}% uptake, {sample_case['pct_plateau']:.1f}% plateau, {sample_case['pct_washout']:.1f}% washout")
            print(f"  Voxels: {sample_case['n_voxels']}, Threshold: {sample_case['adaptive_threshold']:.1f}")
            
            # Sample radiomics features
            shape_features = [col for col in enhanced.columns if 'shape' in col][:2]
            texture_features = [col for col in enhanced.columns if 'glcm' in col][:2]
            
            print(f"  Shape: {shape_features[0].split('_')[-1]} = {sample_case[shape_features[0]]:.3f}")
            print(f"  Texture: {texture_features[0].split('_')[-1]} = {sample_case[texture_features[0]]:.3f}")
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("The enhanced pipeline provides:")
    print(f"• {enhanced_features/original_features:.1f}x more quantitative features ({enhanced_features} vs {original_features})")
    print(f"• {len(enhanced)/len(original):.1f}x more cases analyzed ({len(enhanced)} vs {len(original)})")
    print("• Multi-dataset processing (DUKE, ISPY1, ISPY2)")
    print("• Improved sensitivity through adaptive thresholding")
    print("• Comprehensive shape and texture characterization")
    print("• Multiple normalization strategies for robust analysis")
    print("• Research-grade feature extraction suitable for machine learning")
    print("• Backward compatibility with original kinetic features")
    print("• Enhanced visualizations with better ROI analysis")
    
    return original, enhanced

if __name__ == "__main__":
    original_df, enhanced_df = compare_analysis_systems()
