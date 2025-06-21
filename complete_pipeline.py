import os
import nibabel as nib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import SimpleITK as sitk
from radiomics.featureextractor import RadiomicsFeatureExtractor
from radiomics import imageoperations
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
from neuroCombat import neuroCombat
import glob
import warnings
warnings.filterwarnings('ignore')

class CompleteDCEMRIPipeline:
    """
    Complete DCE-MRI Analysis Pipeline
    
    This unified pipeline combines:
    1. Enhanced DCE-MRI kinetic feature extraction
    2. Comprehensive radiomics analysis
    3. NIfTI colormap creation (compatible with harmonization)
    4. PNG visualization generation
    5. ComBat harmonization
    6. Final CSV output
    
    Everything in one script for complete project workflow.
    """
    
    def __init__(self, apply_normalization=True):
        self.apply_normalization = apply_normalization
        self.radiomics_settings = {
            'interpolator': 'sitkBSpline',
            'level': 1,
            'distances': [1],
            'binWidth': 5,
            'removeOutliers': None,
            'normalize': False,  # We'll handle normalization separately
            'resampledPixelSpacing': [1, 1, 1]
        }
        
        # Initialize radiomics extractor
        self.radiomics_extractor = RadiomicsFeatureExtractor(**self.radiomics_settings)
        print("Complete DCE-MRI Pipeline initialized")
        print("Features: Enhanced kinetics + Radiomics + ComBat harmonization")

    def extract_kinetic_features(self, img_0000, img_0001, mask):
        """Enhanced kinetic feature extraction"""
        # Convert mask to boolean
        roi = mask > 0
        
        if not np.any(roi):
            print("    Warning: Empty ROI mask")
            return {}, np.zeros_like(img_0000, dtype=np.uint8)
        
        # Calculate intensity changes
        intensity_change = ((img_0001 - img_0000) / (img_0000 + 1e-10)) * 100
        
        # Enhanced categorization with stricter thresholds
        colormap = np.zeros_like(img_0000, dtype=np.uint8)
        
        # More sophisticated classification
        uptake_mask = (intensity_change > 15) & roi  # Stronger uptake threshold
        plateau_mask = (intensity_change <= 15) & (intensity_change >= -5) & roi  # Tighter plateau
        washout_mask = (intensity_change < -5) & roi  # Earlier washout detection
        
        colormap[uptake_mask] = 1   # Uptake
        colormap[plateau_mask] = 2  # Plateau
        colormap[washout_mask] = 3  # Washout
        
        # Calculate comprehensive kinetic features
        roi_pixels = np.sum(roi)
        uptake_pixels = np.sum(uptake_mask)
        plateau_pixels = np.sum(plateau_mask)
        washout_pixels = np.sum(washout_mask)
        
        # Basic kinetic metrics
        features = {
            'total_roi_pixels': roi_pixels,
            'uptake_pixels': uptake_pixels,
            'plateau_pixels': plateau_pixels,
            'washout_pixels': washout_pixels,
            'uptake_percentage': (uptake_pixels / roi_pixels * 100) if roi_pixels > 0 else 0,
            'plateau_percentage': (plateau_pixels / roi_pixels * 100) if roi_pixels > 0 else 0,
            'washout_percentage': (washout_pixels / roi_pixels * 100) if roi_pixels > 0 else 0,
        }
        
        # Enhanced statistical features for each timepoint
        for timepoint, img in [('t0', img_0000), ('t1', img_0001)]:
            roi_values = img[roi]
            if len(roi_values) > 0:
                features.update({
                    f'{timepoint}_mean_intensity': np.mean(roi_values),
                    f'{timepoint}_median_intensity': np.median(roi_values),
                    f'{timepoint}_std_intensity': np.std(roi_values),
                    f'{timepoint}_skewness': float(pd.Series(roi_values).skew()),
                    f'{timepoint}_kurtosis': float(pd.Series(roi_values).kurtosis()),
                    f'{timepoint}_intensity_range': np.ptp(roi_values),
                    f'{timepoint}_q25': np.percentile(roi_values, 25),
                    f'{timepoint}_q75': np.percentile(roi_values, 75),
                })
        
        # Temporal change features
        if roi_pixels > 0:
            change_values = intensity_change[roi]
            features.update({
                'mean_intensity_change': np.mean(change_values),
                'median_intensity_change': np.median(change_values),
                'std_intensity_change': np.std(change_values),
                'max_intensity_change': np.max(change_values),
                'min_intensity_change': np.min(change_values),
                'change_range': np.ptp(change_values),
                'positive_change_ratio': np.sum(change_values > 0) / len(change_values),
                'negative_change_ratio': np.sum(change_values < 0) / len(change_values),
            })
            
            # Kinetic curve heterogeneity
            features.update({
                'kinetic_heterogeneity': np.std(change_values),
                'enhancement_entropy': self.calculate_entropy(change_values),
                'washout_severity': np.mean(change_values[change_values < -5]) if np.any(change_values < -5) else 0,
                'uptake_intensity': np.mean(change_values[change_values > 15]) if np.any(change_values > 15) else 0,
            })
        
        return features, colormap

    def calculate_entropy(self, values, bins=10):
        """Calculate entropy of intensity changes"""
        try:
            hist, _ = np.histogram(values, bins=bins)
            hist = hist / np.sum(hist)
            hist = hist[hist > 0]  # Remove zero probabilities
            return -np.sum(hist * np.log2(hist))
        except:
            return 0

    def extract_radiomics_features(self, image_path, mask_path, label=1):
        """Extract radiomics features using pyradiomics"""
        try:
            # Load image and mask
            image = sitk.ReadImage(image_path)
            mask = sitk.ReadImage(mask_path)
            
            # Resample mask to match image
            mask = sitk.Resample(mask, image, sitk.Transform(), sitk.sitkNearestNeighbor)
            
            # Extract features
            features = self.radiomics_extractor.execute(image, mask, label)
            
            # Convert to regular Python types
            clean_features = {}
            for key, value in features.items():
                try:
                    clean_features[key] = float(value)
                except (ValueError, TypeError):
                    clean_features[key] = str(value)
                    
            return clean_features
            
        except Exception as e:
            print(f"Error extracting radiomics features: {e}")
            return {}
    
    def extract_temporal_radiomics(self, img_0000_path, img_0001_path, mask_path):
        """Extract radiomics from both timepoints and calculate temporal features"""
        # Extract from both timepoints
        features_t0 = self.extract_radiomics_features(img_0000_path, mask_path, label=1)
        features_t1 = self.extract_radiomics_features(img_0001_path, mask_path, label=1)
        
        # Combine features with temporal prefixes
        combined_features = {}
        
        # Add timepoint-specific features
        for key, value in features_t0.items():
            if 'original' in key.lower():
                combined_features[f't0_{key}'] = value
                
        for key, value in features_t1.items():
            if 'original' in key.lower():
                combined_features[f't1_{key}'] = value
        
        # Calculate temporal changes for first-order features
        for key in features_t0.keys():
            if 'firstorder' in key and key in features_t1:
                try:
                    t0_val = float(features_t0[key])
                    t1_val = float(features_t1[key])
                    if t0_val != 0:
                        change = (t1_val - t0_val) / t0_val * 100
                        combined_features[f'temporal_change_{key}'] = change                
                except:
                    continue
        
        return combined_features
    def save_colormap_files(self, case_id, case_path, img_0000, colormap, mask, tp0_file):
        """Save RGB NIfTI colormap and PNG visualization"""
        
        # Import the convert_to_rgb_nifti function from rgb_nifti_converter
        from rgb_nifti_converter import convert_to_rgb_nifti
        
        # Save RGB-encoded NIfTI for visualization in Mango and other viewers
        rgb_nifti_out_path = os.path.join(case_path, f"{case_id}_colormap.nii.gz")  # Χρησιμοποιούμε το ίδιο όνομα για συμβατότητα
        convert_to_rgb_nifti(tp0_file, colormap, rgb_nifti_out_path)
        
        # 2. Create enhanced PNG visualization
        colors = [
            (0, 0, 0, 0),      # Transparent for background
            (0, 0, 1, 0.7),    # Pure Blue with alpha for Uptake
            (0, 1, 0, 0.7),    # Pure Green with alpha for Plateau
            (1, 0, 0, 0.7)     # Pure Red with alpha for Washout
        ]
        custom_cmap = ListedColormap(colors)
        
        # Find central slice with ROI
        roi_slices = [z for z in range(colormap.shape[2]) if np.any(mask[:,:,z])]
        slice_idx = roi_slices[len(roi_slices) // 2] if roi_slices else colormap.shape[2] // 2
        
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.imshow(img_0000[:, :, slice_idx].T, cmap='gray', origin='lower', aspect='auto')
        im = ax.imshow(colormap[:, :, slice_idx].T, cmap=custom_cmap, vmin=0, vmax=3, 
                      origin='lower', aspect='auto', alpha=0.7)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, ticks=[0.375, 1.125, 1.875, 2.625], fraction=0.046, pad=0.04)
        cbar.ax.set_yticklabels(['Background', 'Uptake', 'Plateau', 'Washout'])
        cbar.ax.tick_params(labelsize=10)
        
        ax.set_title(f'Complete Pipeline Analysis - {case_id} - Slice {slice_idx}', fontsize=14)
        ax.axis('off')
        
        plt.tight_layout()
        png_out_path = os.path.join(case_path, f"{case_id}_complete_colormap.png")
        plt.savefig(png_out_path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"    Saved PNG visualization: {png_out_path}")

    def process_case(self, case_id, case_path, segment_dir):
        """Process a single case with complete feature extraction"""
        try:
            # Find image files
            tp0_file = None
            tp1_file = None
            
            for file in os.listdir(case_path):
                if file.endswith('.nii.gz'):
                    if '_0000.nii.gz' in file:
                        tp0_file = os.path.join(case_path, file)
                    elif '_0001.nii.gz' in file:
                        tp1_file = os.path.join(case_path, file)
            
            if not tp0_file or not tp1_file:
                print(f"    Missing timepoint files for {case_id}")
                return None
            
            # Find segmentation file
            seg_file = os.path.join(segment_dir, f"{case_id}.nii.gz")
            if not os.path.exists(seg_file):
                print(f"    Segmentation file not found: {seg_file}")
                return None
                
            print(f"    Processing {case_id}...")
            print(f"    Files - TP0: {os.path.basename(tp0_file)}, TP1: {os.path.basename(tp1_file)}, Seg: {os.path.basename(seg_file)}")
        
            # Load images for kinetic analysis
            img_0000 = nib.load(tp0_file).get_fdata()
            img_0001 = nib.load(tp1_file).get_fdata()
            mask = nib.load(seg_file).get_fdata()
            
            # Extract kinetic features
            kinetic_features, colormap = self.extract_kinetic_features(img_0000, img_0001, mask)
            
            # Extract radiomics features from both timepoints
            radiomics_features = self.extract_temporal_radiomics(tp0_file, tp1_file, seg_file)
            
            # Combine all features
            all_features = {
                'case_id': case_id,
                **kinetic_features,
                **radiomics_features
            }
            
            # Save colormap files (both NIfTI and PNG)
            self.save_colormap_files(case_id, case_path, img_0000, colormap, mask, tp0_file)
            
            return all_features
            
        except Exception as e:
            print(f"    Error processing {case_id}: {e}")
            return None

    def apply_comprehensive_normalization(self, features_df):
        """Apply multiple normalization techniques"""
        numeric_columns = features_df.select_dtypes(include=[np.number]).columns
        numeric_columns = [col for col in numeric_columns if col != 'case_id']
        normalized_df = features_df.copy()
        
        # Min-Max Scaling (0-1 range)
        scaler_minmax = MinMaxScaler()
        normalized_df[numeric_columns] = scaler_minmax.fit_transform(features_df[numeric_columns])
        
        return normalized_df

    def apply_combat_harmonization(self, features_df):
        """Apply ComBat harmonization to features"""
        try:
            # Extract dataset information from case_id
            features_df['dataset'] = features_df['case_id'].str.split('_').str[0]
            datasets = features_df['dataset'].unique()
            
            if len(datasets) < 2:
                print("Warning: ComBat harmonization requires at least 2 datasets")
                return features_df.drop('dataset', axis=1)
            
            print(f"Applying ComBat harmonization across datasets: {datasets}")
            
            # Prepare data for neuroCombat
            numeric_columns = features_df.select_dtypes(include=[np.number]).columns
            numeric_columns = [col for col in numeric_columns if col not in ['case_id']]
            
            if len(numeric_columns) == 0:
                print("Warning: No numeric features found for harmonization")
                return features_df.drop('dataset', axis=1)
            
            # Create batch variable (dataset indicator)
            batch = features_df['dataset'].values
            
            # Apply neuroCombat
            data_matrix = features_df[numeric_columns].T.values  # neuroCombat expects features x samples
            
            # Apply ComBat harmonization
            harmonized_data = neuroCombat(
                dat=data_matrix,
                batch=batch,
                mod=None,  # No additional covariates
                par_prior=True,
                prior_plots=False,
                mean_only=False,
                ref_batch=None,
                eb=True
            )["data"]
            
            # Create harmonized dataframe
            harmonized_df = features_df.copy()
            harmonized_df[numeric_columns] = harmonized_data.T
            
            print(f"    ComBat harmonization completed for {len(numeric_columns)} features across {len(datasets)} datasets")
            return harmonized_df.drop('dataset', axis=1)
            
        except Exception as e:
            print(f"Error in ComBat harmonization: {e}")
            print("Returning original features without harmonization")
            if 'dataset' in features_df.columns:
                return features_df.drop('dataset', axis=1)
            return features_df

    def process_all_datasets(self, base_dir):
        """Process all datasets with complete pipeline"""
        print("=== Complete DCE-MRI Analysis Pipeline ===")
        print("Processing all datasets with:")
        print("• Enhanced kinetic analysis")
        print("• Comprehensive radiomics")
        print("• NIfTI colormap creation")
        print("• PNG visualizations")
        print("• ComBat harmonization")
        print("• Final CSV export")
        print()
        
        all_features = []
        
        # Process each dataset
        for dataset in ['DUKE', 'ISPY1', 'ISPY2', 'NACT']:
            dataset_dir = os.path.join(base_dir, dataset)
            segment_dir = os.path.join(dataset_dir, 'segment')
            
            if not os.path.exists(dataset_dir) or not os.path.exists(segment_dir):
                print(f"Skipping {dataset} - directory not found")
                continue
                
            print(f"\n--- Processing {dataset} dataset ---")
            
            # Find all case directories
            case_dirs = [d for d in os.listdir(dataset_dir) 
                        if os.path.isdir(os.path.join(dataset_dir, d)) and d != 'segment']
            
            print(f"Found {len(case_dirs)} cases in {dataset}")
            
            for case_id in sorted(case_dirs):
                case_path = os.path.join(dataset_dir, case_id)
                features = self.process_case(case_id, case_path, segment_dir)
                
                if features:
                    all_features.append(features)
                    print(f"    ✓ {case_id} completed")
                else:
                    print(f"    ✗ {case_id} failed")
        
        if not all_features:
            print("No features extracted. Check your data paths.")
            return None
        
        # Create features dataframe
        features_df = pd.DataFrame(all_features)
        print(f"\n=== Feature Extraction Summary ===")
        print(f"Total cases processed: {len(features_df)}")
        print(f"Total features extracted: {len(features_df.columns) - 1}")  # Exclude case_id
        
        # Save raw features
        raw_csv_path = os.path.join(base_dir, 'complete_pipeline_raw_features.csv')
        features_df.to_csv(raw_csv_path, index=False)
        print(f"Raw features saved: {raw_csv_path}")
        
        # Apply normalization
        if self.apply_normalization:
            print("\n=== Applying Normalization ===")
            normalized_df = self.apply_comprehensive_normalization(features_df)
            
            normalized_csv_path = os.path.join(base_dir, 'complete_pipeline_normalized_features.csv')
            normalized_df.to_csv(normalized_csv_path, index=False)
            print(f"Normalized features saved: {normalized_csv_path}")
        else:
            normalized_df = features_df
        
        # Apply ComBat harmonization
        print("\n=== Applying ComBat Harmonization ===")
        harmonized_df = self.apply_combat_harmonization(normalized_df.copy())
        
        harmonized_csv_path = os.path.join(base_dir, 'complete_pipeline_harmonized_features.csv')
        harmonized_df.to_csv(harmonized_csv_path, index=False)
        print(f"Harmonized features saved: {harmonized_csv_path}")
        
        # Final summary
        print(f"\n=== Complete Pipeline Summary ===")
        print(f"✓ Raw features: {raw_csv_path}")
        if self.apply_normalization:
            print(f"✓ Normalized features: {normalized_csv_path}")
        print(f"✓ Harmonized features: {harmonized_csv_path}")
        print(f"✓ NIfTI colormaps: Created for each case (*_colormap.nii.gz)")
        print(f"✓ PNG visualizations: Created for each case (*_complete_colormap.png)")
        print("\nPipeline completed successfully!")
        
        return harmonized_df    
    def save_final_rgb_nifti(self, img_ref_path: str, class_arr: np.ndarray, out_path: str):
        """
        Αποθηκεύει το colormap ως RGB NIfTI για συμβατότητα με προγράμματα απεικόνισης όπως το Mango
        
        Args:
            img_ref_path: Διαδρομή προς το αρχείο αναφοράς για affine και header
            class_arr: Πίνακας με τις κατηγορίες (1:Uptake, 2:Plateau, 3:Washout)
            out_path: Διαδρομή για την αποθήκευση του RGB NIfTI αρχείου
        """
        # Βήματα 1-5: Δημιουργούμε το 4D array με τα χρώματα
        # Φορτώνουμε την εικόνα αναφοράς με το ίδιο μέγεθος μέσω nibabel για να αποφύγουμε προβλήματα διαστάσεων
        nii_orig = nib.load(img_ref_path)
        mri_array = nii_orig.get_fdata()
        
        # Κανονικοποιούμε το υποκείμενο MRI ώστε να έχουμε grayscale background
        # (μετατροπή σε 0-255 για απόχρωση του γκρι)
        normalized_mri = ((mri_array - mri_array.min()) / (mri_array.max() - mri_array.min() + 1e-10) * 255).astype(np.uint8)
        
        # Δημιουργούμε RGB volume με την υποκείμενη εικόνα ως grayscale background
        rgb_volume = np.zeros((*class_arr.shape, 3), dtype=np.uint8)
        
        # Ορίζουμε το grayscale background (αντιγράφουμε την ίδια τιμή σε R,G,B κανάλια)
        for i in range(3):
            rgb_volume[:, :, :, i] = normalized_mri
        
        # Παράγουμε τον χρωματικό χάρτη - τώρα θα εφαρμόζει τα χρώματα μόνο στις περιοχές ενδιαφέροντος
        colors = {
            1: [0, 0, 255],    # Uptake  -> Μπλε
            2: [0, 255, 0],    # Plateau -> Πράσινο
            3: [255, 0, 0]     # Washout -> Κόκκινο
        }
        for class_value, color_rgb in colors.items():
            mask = (class_arr == class_value)
            # Εφαρμόζουμε το κάθε χρώμα στα voxel της αντίστοιχης κλάσης
            for i, c in enumerate(color_rgb):
                rgb_volume[mask, i] = c# Βήμα 6-7: Μετατρέπουμε το array σε μορφή συμβατή με RGB NIfTI
        # Ορίζουμε τον ειδικό τύπο δεδομένων
        rgb_dtype = np.dtype([('R', np.uint8), ('G', np.uint8), ('B', np.uint8)])
        
        # Αναδιαμορφώνουμε το array ώστε να είναι συμβατό με το view
        # από (X,Y,Z,3) σε κατάλληλη μορφή για το nibabel
        # Χρησιμοποιούμε τη μέθοδο reshape για να αποφύγουμε προβλήματα με τα views
        reshaped = np.zeros(class_arr.shape, dtype=rgb_dtype)
        reshaped['R'] = rgb_volume[:, :, :, 0]
        reshaped['G'] = rgb_volume[:, :, :, 1]
        reshaped['B'] = rgb_volume[:, :, :, 2]        # Βήμα 9: Δημιουργία του τελικού NIfTI object με τα *σωστά* δεδομένα
        rgb_nii = nib.Nifti1Image(reshaped, nii_orig.affine, header=nii_orig.header)

        # Βήμα 10: Ρύθμιση του header για το RGB NIfTI
        rgb_nii.header['datatype'] = 128  # RGB24
        rgb_nii.header['bitpix'] = 24     # 24-bit RGB

        # Βήμα 11: Αποθήκευση
        nib.save(rgb_nii, out_path)
        print(f"    Saved RGB NIfTI colormap: {out_path}")

def main():
    """Main execution function"""
    # Initialize complete pipeline
    pipeline = CompleteDCEMRIPipeline(apply_normalization=True)
    
    # Set base directory
    base_dir = r"c:\Users\nickk\BiomedicalSignals"
    
    # Process all datasets
    final_features = pipeline.process_all_datasets(base_dir)
    
    if final_features is not None:
        print(f"\nFinal dataset shape: {final_features.shape}")
        print("Complete DCE-MRI analysis pipeline finished successfully!")
    else:
        print("Pipeline failed. Please check your data and try again.")

if __name__ == "__main__":
    main()
