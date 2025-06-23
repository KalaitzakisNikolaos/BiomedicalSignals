import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

# Path to one of the NIfTI files
nifti_path = "DUKE/DUKE_099/DUKE_099_0000.nii.gz"
colormap_path = "DUKE/DUKE_099/DUKE_099_colormap.nii.gz"

# Load NIfTI files
if os.path.exists(nifti_path):
    print(f"Loading {nifti_path}...")
    img = nib.load(nifti_path)
    data = img.get_fdata()
    print(f"Image shape: {data.shape}")
    print(f"Data type: {data.dtype}")
    print(f"Data range: {data.min()} to {data.max()}")
    print(f"Image header: {img.header}")
else:
    print(f"File not found: {nifti_path}")

if os.path.exists(colormap_path):
    print(f"\nLoading {colormap_path}...")
    cmap_img = nib.load(colormap_path)
    cmap_data = cmap_img.get_fdata()
    print(f"Colormap shape: {cmap_data.shape}")
    print(f"Colormap data type: {cmap_data.dtype}")
    unique_values = np.unique(cmap_data)
    print(f"Unique values in colormap: {unique_values}")
else:
    print(f"File not found: {colormap_path}")

print("\nNow checking available features CSV files...")
for csv_file in ["complete_pipeline_raw_features.csv", "complete_pipeline_harmonized_features.csv", "complete_pipeline_normalized_features.csv"]:
    if os.path.exists(csv_file):
        print(f"Found {csv_file}")
    else:
        print(f"File not found: {csv_file}")
