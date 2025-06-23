# MAMA-MIA DCE-MRI Analysis Project

<div align="center">
  <img src="images/mamamia_logo.png" alt="MAMA-MIA Logo" width="200"/>
  <img src="images/hmu_logo.png" alt="Hellenic Mediterranean University Logo" width="120"/>
</div>

---

## Overview
This project provides a comprehensive web application and analysis pipeline for dynamic contrast-enhanced magnetic resonance imaging (DCE-MRI) data from the MAMA-MIA public dataset. The workflow includes:

1. **Biomarker Extraction** from DCE-MRI sequences with contrast agent
2. **Pseudo-color Map Generation** based on biomarker characteristics
3. **Signal Harmonization** using the ComBat technique for multicenter data
4. **Comprehensive Visualization** of kinetic curves and harmonization effects
5. **Interactive Web Interface** for exploring case data and metrics

### Web Application
The project includes a modern, responsive web application that allows researchers to:
- Explore DCE-MRI cases across multiple datasets (DUKE, ISPY1, ISPY2, NACT)
- Visualize kinetic curves and tissue classification
- Compare raw vs. harmonized data with interactive visualizations
- Access key metrics and statistics for each case

<p align="center">
  <img src="images/website.png" alt="MAMA-MIA Web Interface" width="800"/>
</p>

---

## Example Images

### Example 1: DCE-MRI with Tumor Segmentation
<p align="center">
  <img src="images/example1.png" alt="DCE-MRI with Tumor Segmentation" width="400"/>
</p>

### Example 2: Segmentation Mask Overlay
<p align="center">
  <img src="images/segment.gif" alt="Segmentation Mask Overlay" width="400"/>
</p>

### Example 3: Pseudo-color Map (Uptake/Plateau/Washout)
<p align="center">
  <img src="ISPY1/ISPY1_1034/ISPY1_1034_complete_colormap.png" alt="Pseudo-color Map" width="400"/>
</p>

### Example 4: Dynamic Animation (DUKE_099)
<p align="center">
  <img src="images/colomap_DUKE_099.gif" alt="Dynamic Colormap Animation" width="400"/>
</p>

### Example 5: ComBat Harmonization Visualization
<p align="center">
  <img src="images/combat_visualization.png" alt="Unified Combat Visualization" width="600"/>
</p>

### Example 6: Terminal Execution Timeline
<div align="center">
  <img src="images/terminal_launch.png" alt="Terminal Launch" width="300"/>
  <img src="images/terminal_execute.png" alt="Terminal Execution" width="300"/>
  <img src="images/terminal_final.png" alt="Terminal Completion" width="300"/>
</div>

---

## Project Structure
- `DUKE/`, `ISPY1/`, `ISPY2/`, `NACT/`: Folders for each study group, each containing subfolders for individual cases and their respective DCE-MRI timepoints (e.g., `*_0000.nii.gz`, `*_0001.nii.gz`, ...).
- `segment/`: Contains segmentation masks for each case (e.g., `DUKE_032.nii.gz`).

### Core Scripts
- `complete_pipeline.py`: Unified Python script for the entire DCE-MRI pipeline. Combines enhanced feature extraction, radiomics analysis, NIfTI colormap creation, and ComBat harmonization in a single file.
- `combat_visualization.py`: Unified visualization script for creating comprehensive harmonization visualizations.
- `rgb_nifti_converter.py`: Utility for converting standard colormaps to RGB-encoded NIfTI format.
- `explore_nifti.py`: Tool for exploring and analyzing NIfTI image files.

### Web Application Files
- `web_app.py`: Main Flask application that serves the interactive web interface.
- `templates/`: Contains HTML templates for the web application:
  - `index.html`: Main page with case browser and dataset selection
  - `case.html`: Detailed case analysis page with visualizations
- `static/`: Contains static assets for the web application:
  - `css/styles.css`: Custom CSS styles for the web interface
  - `js/main.js`: JavaScript for interactive features
  - `images/`: Icons, logos, and static visualizations

### Data Files
- `images/`: Contains example images, logos, and analysis results used in this README.
- `complete_pipeline_raw_features.csv`: Raw extracted features before harmonization.
- `complete_pipeline_normalized_features.csv`: Features after normalization.
- `complete_pipeline_harmonized_features.csv`: Features after ComBat harmonization.

## Data Files

### Input Files (Not included in repository due to size limitations)
- **DCE-MRI Timepoints:** `*_0000.nii.gz`, `*_0001.nii.gz` (e.g., `DUKE_032_0000.nii.gz`, `DUKE_032_0001.nii.gz`)
  - These are the raw NIfTI format images from the MAMA-MIA dataset
  - `*_0000.nii.gz`: Pre-contrast image (t=0)
  - `*_0001.nii.gz`: Post-contrast image (t=1)
  
- **Segmentation Files:** `*/segment/*.nii.gz` (e.g., `DUKE/segment/DUKE_032.nii.gz`)
  - These files contain the segmentations (masks) of the regions of interest (ROI)
  - Used to identify the tumor or tissue areas for analysis

### Output Files (Included in repository)
- **RGB Pseudo-color Maps:** `*_colormap.nii.gz` (e.g., `DUKE_032_colormap.nii.gz`)
  - Enhanced RGB-encoded NIfTI format for direct visualization in viewers like Mango
  - Shows the underlying MRI as grayscale background with colored overlay:
    - Blue: Uptake (>15% intensity increase)
    - Green: Plateau (between -5% and +15% intensity change)
    - Red: Washout (<-5% intensity decrease)
  - Compatible with standard DICOM viewers that support RGB NIfTI format
  
- **Visualization Images:** `*_complete_colormap.png` (e.g., `DUKE_032_complete_colormap.png`)
  - PNG images showing a central slice of the pseudo-color map
  - Color coding:
    - Black: Background
    - Blue: Uptake
    - Green: Plateau
    - Red: Washout
  - Includes a color legend for easy interpretation

- **Feature Analysis Files:**
  - `complete_pipeline_raw_features.csv`: Statistical features extracted from each case before harmonization
  - `complete_pipeline_normalized_features.csv`: Features after normalization
  - `complete_pipeline_harmonized_features.csv`: Features after ComBat harmonization
  - `images/combat_visualization.png`: Comprehensive analysis showing before/after harmonization
  - `images/colormap_*.gif`: Dynamic visualization of colormap analysis

The `complete_pipeline.py` script automatically generates these output files by:
1. Loading the pre and post-contrast images
2. Applying the ROI mask to isolate the region of interest
3. Calculating the percentage intensity change between timepoints
4. Classifying each voxel according to its enhancement pattern
5. Extracting comprehensive radiomics features from the ROI
6. Saving the results as both NIfTI (.nii.gz) and visualization (.png) files
7. Normalizing and harmonizing features across datasets
8. Generating final CSV output with all feature data

---

---

## Web Application Features

### Interactive Case Analysis
Our web application provides a sophisticated interface for analyzing DCE-MRI data across multiple datasets. The application allows researchers and clinicians to:

- Browse cases organized by dataset (DUKE, ISPY1, ISPY2, NACT)
- View detailed kinetic curves showing signal intensity patterns over time
- Analyze tissue classifications with color-coded visualizations
- Compare raw and harmonized data with dual-axis visualizations
- Access comprehensive metrics for quantitative analysis

### Key Visualizations

#### 1. Raw vs. Harmonized Comparison
The application provides detailed comparisons between raw data and ComBat-harmonized data, allowing researchers to understand how harmonization affects feature values across different datasets.

<p align="center">
  <img src="images/raw_harmon.png" alt="Raw vs. Harmonized Comparison" width="700"/>
</p>

#### 2. Kinetic Curves Analysis
The system generates detailed kinetic curve visualizations showing the signal intensity patterns over time, which are crucial for understanding tissue enhancement characteristics.

<p align="center">
  <img src="images/kinetic.png" alt="Kinetic Curves" width="600"/>
</p>

#### 3. Harmonized Kinetic Curves
The application also provides visualizations of harmonized kinetic curves, illustrating how the ComBat harmonization affects the temporal enhancement patterns.

<p align="center">
  <img src="images/skinetic_harmon.png" alt="Harmonized Kinetic Curves" width="600"/>
</p>

#### 4. Tissue Classification with Colormap
Advanced colormaps visualize tissue classification based on enhancement patterns with blue representing uptake, green for plateau, and red for washout regions.

<p align="center">
  <img src="images/keymetrics.png" alt="Colormap Visualization and Key Metrics" width="700"/>
</p>

### Technical Features
The web application is built using:
- **Flask**: Python web framework for the backend
- **Bootstrap 5**: Modern responsive design system 
- **Matplotlib & Plotly**: For dynamic chart generation
- **Interactive Components**: Real-time data filtering and visualization

All visualizations are dynamically generated based on actual case data, ensuring that researchers always have access to the most relevant and up-to-date information.

---

## Running the Web Application

The interactive web application provides a user-friendly interface to explore all aspects of the DCE-MRI analysis, including kinetic curves, tissue classification, and harmonization effects.

### Prerequisites
- Python 3.8 or higher
- Flask
- NumPy, Pandas
- Matplotlib 
- Nibabel

### Installation
```bash
# Install required packages
pip install flask numpy pandas matplotlib nibabel
```

### Starting the Web Server
```bash
# Navigate to the project directory
cd BiomedicalSignals

# Run the web application
python web_app.py
```

The web application will be available at [http://localhost:5000](http://localhost:5000) in your web browser.

### Using the Web Interface

1. **Home Page**: Browse available cases organized by dataset (DUKE, ISPY1, ISPY2, NACT).
2. **Case Analysis**: Click on any case to view detailed analysis including:
   - Kinetic curve visualizations
   - Signal distribution pie charts
   - Colormap visualization of tissue classification
   - Key metrics table with quantitative data
   - Raw vs. harmonized data comparisons
3. **ComBat Visualization**: Generate real-time ComBat harmonization visualizations to compare datasets.

### Key Features

- **Interactive Case Browser**: Navigate through cases by dataset
- **Dynamic Visualization Generation**: Real-time creation of visualizations based on case data
- **Dual Y-Axis Charts**: Compare raw and harmonized data with appropriate scaling
- **Responsive Design**: Works on desktop and mobile devices
- **Detailed Explanations**: Comprehensive information about harmonization effects and analysis methods

## File Naming Conventions

The unified pipeline uses consistent file naming conventions:

1. **Input Files:**
   - Original DCE-MRI: `{DATASET}_{CASEID}_{TIMEPOINT}.nii.gz` (e.g., `DUKE_032_0000.nii.gz`)
   - Segmentation masks: `{DATASET}_{CASEID}.nii.gz` (e.g., `DUKE_032.nii.gz`)

2. **Output Files:**
   - NIfTI Colormaps: `{DATASET}_{CASEID}_colormap.nii.gz` (e.g., `DUKE_032_colormap.nii.gz`)
   - PNG Visualizations: `{DATASET}_{CASEID}_complete_colormap.png` (e.g., `DUKE_032_complete_colormap.png`)
   - Raw Features: `complete_pipeline_raw_features.csv`
   - Normalized Features: `complete_pipeline_normalized_features.csv`
   - Harmonized Features: `complete_pipeline_harmonized_features.csv`
   - Visualization: `images/combat_visualization.png`

## Detailed Outputs

### 1. Colormap NIfTI Files

The colormap NIfTI files (`*_colormap.nii.gz`) contain voxel classifications where:
- Value 0: Background (no ROI)
- Value 1: Uptake (significant enhancement)
- Value 2: Plateau (stable enhancement)
- Value 3: Washout (decreasing enhancement)

### 2. Visualization PNG Files

The PNG visualizations (`*_complete_colormap.png`) show:
- Center slice of the tumor region
- Color-coded kinetic patterns
- Color legend
- Case identifier

### 3. CSV Feature Files

Three CSV files are created with increasing levels of processing:

1. **Raw Features** (`complete_pipeline_raw_features.csv`):
   - Direct feature measurements before any normalization
   - Includes case ID, dataset source, and raw kinetic percentages

2. **Normalized Features** (`complete_pipeline_normalized_features.csv`):
   - Features after standardization within each dataset
   - Normalizes values for fair comparison

3. **Harmonized Features** (`complete_pipeline_harmonized_features.csv`):
   - Final features after ComBat harmonization
   - Batch effects removed while preserving biological variation

---

## Detailed Steps

### 1. Biomarker Extraction
- For each case, extract the region of interest (ROI) using the provided segmentation mask.
- Use Python libraries (e.g., nibabel, numpy) to process the NIfTI images.
- Extract intensity values for the ROI at timepoints 0000 and 0001.

### 2. Pseudo-color Map Generation
- For each voxel in the ROI, calculate the intensity change between timepoints (e.g., 0000 and 0001).
- Classify each voxel into:
  - **Uptake (1):** >10% increase
  - **Plateau (2):** ~10% change
  - **Washout (3):** <10% decrease
- Save the resulting classification map as a new NIfTI image.

### 3. Signal Harmonization (ComBat)
- Extract statistical features from the pseudo-color maps (uptake%, plateau%, washout%).
- Apply ComBat harmonization technique to reduce batch effects.
- Generate comprehensive comparison plots showing before/after harmonization results.
- Calculate harmonization metrics including variance reduction and F-statistics.
- Save harmonized features and create detailed visualizations of the harmonization effect.

#### Understanding Raw vs. Harmonized Data

The application provides detailed visualizations to help researchers understand the differences between raw and harmonized data:

- **Dual Y-axis Scaling**: Raw values (0-100% scale) and harmonized values (0-1 scale) are displayed on separate axes for clear comparison.
- **Scale Factor Labels**: Each comparison includes the scale factor between raw and harmonized data.
- **Side-by-side Visualization**: Raw and harmonized values are shown side-by-side for easy comparison.

<p align="center">
  <img src="images/raw_harmon.png" alt="Raw vs Harmonized Comparison" width="700"/>
</p>

Key benefits of ComBat harmonization in this application:
- Reduction of batch effects between different imaging centers
- Standardization of values for fair comparison across datasets
- Preservation of biological variation while removing technical variation
- Improved statistical power for multi-center analysis

---

## Unified Pipeline Workflow

### Step 1: Complete Pipeline Execution
```bash
python complete_pipeline.py
```
This unified script processes all cases and performs:
- Enhanced DCE-MRI kinetic feature extraction
- Comprehensive radiomics analysis
- NIfTI colormap generation (`*_colormap.nii.gz`) 
- PNG visualization creation (`*_complete_colormap.png`)
- ComBat harmonization across datasets
- CSV output with raw and harmonized features

### Step 2: Visualization Generation
```bash
python combat_visualization.py
```
This script creates:
- Reference kinetic curves visualization
- Dataset summary statistics
- Before/After harmonization comparisons for Uptake, Plateau, Washout
- Comprehensive visualization dashboard

---

## Requirements
- Python 3.8+
- Flask 2.3.3
- Pandas 2.0.3
- NumPy 1.24.4
- Nibabel 5.1.0
- Matplotlib 3.7.2
- SimpleITK 2.2.1

Install with:
```bash
pip install -r requirements.txt
```

## Unified Pipeline Features
The new unified pipeline provides several advantages over the previous separate scripts:

1. **One-step Processing**: Complete DCE-MRI analysis from raw images to harmonized features in a single script
2. **Enhanced Feature Set**: Combines basic kinetic features with comprehensive radiomics
3. **Improved Visualization**: Creates standardized visualizations for both individual cases and dataset-wide analysis
4. **Automated Harmonization**: Performs ComBat harmonization with detailed statistical outputs
5. **Consistent File Naming**: Uses consistent naming conventions across all output files

## Dataset Statistics
- **Total Cases Processed**: 40 cases across 4 datasets
- **DUKE**: 10 cases
- **ISPY1**: 10 cases  
- **ISPY2**: 10 cases
- **NACT**: 10 cases
- **Features Analyzed**: Uptake percentage, Plateau percentage, Washout percentage
- **Harmonization Method**: ComBat harmonization technique

---

## References
- [MAMA-MIA Dataset](https://www.synapse.org/Synapse:syn60868042/files/)
- [PyRadiomics Documentation](https://pyradiomics.readthedocs.io/en/latest/)


---
## Contribution and Credits

<p align="center">
  <img src="images/mamamia_logo.png" alt="MAMA-MIA Logo" width="200"/>
  <img src="images/hmu_logo.png" alt="Hellenic Mediterranean University Logo" width="120"/>
</p>

<p align="center">
  <b>Developed by Nikolaos Kalaitzakis</b><br>
  Hellenic Mediterranean University<br>
  © 2024-2025 MAMA-MIA Project
</p>

### Acknowledgements
- MAMA-MIA Dataset contributors
- Hellenic Mediterranean University
- Contributors to open-source libraries used in this project
