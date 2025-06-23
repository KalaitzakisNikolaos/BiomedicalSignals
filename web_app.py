import os
import json
import numpy as np
import pandas as pd
import nibabel as nib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import io
import base64
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load the datasets
def load_data():
    data = {}
    try:
        # Load dataset features
        raw_features = pd.read_csv('complete_pipeline_raw_features.csv')
        harmonized_features = pd.read_csv('complete_pipeline_harmonized_features.csv')
        normalized_features = pd.read_csv('complete_pipeline_normalized_features.csv')
        
        # Add dataset field
        raw_features['dataset'] = raw_features['case_id'].str.split('_').str[0]
        harmonized_features['dataset'] = harmonized_features['case_id'].str.split('_').str[0]
        normalized_features['dataset'] = normalized_features['case_id'].str.split('_').str[0]
        
        data = {
            'raw': raw_features,
            'harmonized': harmonized_features,
            'normalized': normalized_features
        }
    except Exception as e:
        print(f"Error loading data: {e}")
    
    return data

# Get available cases
def get_available_cases():
    cases = []
    
    # DUKE dataset
    duke_cases = []
    for case_dir in os.listdir('DUKE'):
        if os.path.isdir(os.path.join('DUKE', case_dir)) and case_dir.startswith('DUKE_'):
            duke_cases.append(case_dir)
    
    # ISPY1 dataset
    ispy1_cases = []
    for case_dir in os.listdir('ISPY1'):
        if os.path.isdir(os.path.join('ISPY1', case_dir)) and case_dir.startswith('ISPY1_'):
            ispy1_cases.append(case_dir)
    
    # ISPY2 dataset
    ispy2_cases = []
    for case_dir in os.listdir('ISPY2'):
        if os.path.isdir(os.path.join('ISPY2', case_dir)) and case_dir.startswith('ISPY2_'):
            ispy2_cases.append(case_dir)
    
    # NACT dataset
    nact_cases = []
    for case_dir in os.listdir('NACT'):
        if os.path.isdir(os.path.join('NACT', case_dir)) and case_dir.startswith('NACT_'):
            nact_cases.append(case_dir)
    
    return {
        'DUKE': sorted(duke_cases),
        'ISPY1': sorted(ispy1_cases),
        'ISPY2': sorted(ispy2_cases),
        'NACT': sorted(nact_cases)
    }

# Generate kinetic curves for a case
def generate_kinetic_curves(case_id, data):
    if case_id not in data['raw']['case_id'].values:
        return None
    
    case_data = data['raw'][data['raw']['case_id'] == case_id].iloc[0]
    
    # Create figure with kinetic curves
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Time points - more precise for smoother curves
    time_points = np.linspace(0.0, 3.0, 100)
    
    # Initial curve parameters (based on the reference image)
    initial_slope = 150
    max_intensity = case_data['uptake_intensity'] * 1.0  # Scale to real data
    
    # Create base curve (common initial part up to divergence point)
    t_diverge = 1.2  # Divergence time point (matches reference)
    idx_diverge = int(t_diverge * len(time_points) / 3.0)
    
    base_curve = np.zeros_like(time_points)
    # First part - common for all curves
    base_curve[:idx_diverge+1] = max_intensity * (1 - np.exp(-initial_slope * time_points[:idx_diverge+1]/max_intensity))
    
    # Create the three curve types, all sharing the same values up to divergence
    uptake_curve = np.copy(base_curve)
    plateau_curve = np.copy(base_curve)
    washout_curve = np.copy(base_curve)
    
    # Value at divergence point - all curves meet here
    diverge_value = base_curve[idx_diverge]
    
    # After divergence point - exactly match the sample image curves
    # Slope calculations
    uptake_slope = case_data['uptake_intensity'] * 0.07
    plateau_slope = -case_data['uptake_intensity'] * 0.03
    washout_slope = -case_data['uptake_intensity'] * 0.12 * case_data['washout_severity']
    
    # Apply slopes after divergence
    for i in range(idx_diverge+1, len(time_points)):
        dt = time_points[i] - time_points[idx_diverge]
        uptake_curve[i] = diverge_value + dt * uptake_slope
        plateau_curve[i] = diverge_value + dt * plateau_slope
        washout_curve[i] = diverge_value + dt * washout_slope
    
    # Plot curves with consistent colors matching the reference image
    ax.plot(time_points, uptake_curve, color='#3274A1', linewidth=2, label='Uptake')
    ax.plot(time_points, plateau_curve, color='#3A923A', linewidth=2, label='Plateau')
    ax.plot(time_points, washout_curve, color='#C03D3E', linewidth=2, label='Washout')
    
    # Add divergence point reference line
    ax.axvline(x=t_diverge, color='gray', linestyle='--', alpha=0.7)
    
    ax.set_title(f"Kinetic Curves for {case_id}")
    ax.set_xlabel("Time point")
    ax.set_ylabel("Signal Intensity (%)")
    ax.set_xlim(0.0, 3.0)
    ax.set_ylim(0, max(120, max_intensity * 1.5))  # Adjust y-axis limits based on data
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Convert plot to base64 string
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return plot_base64

# Generate pie chart of uptake/plateau/washout percentages
def generate_pie_chart(case_id, data):
    if case_id not in data['raw']['case_id'].values:
        return None
    
    raw_case_data = data['raw'][data['raw']['case_id'] == case_id].iloc[0]
    harmonized_case_data = data['harmonized'][data['harmonized']['case_id'] == case_id].iloc[0]
    
    # Create figure with two pie charts side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Data for raw pie chart
    raw_labels = ['Uptake', 'Plateau', 'Washout']
    raw_sizes = [raw_case_data['uptake_percentage'], raw_case_data['plateau_percentage'], raw_case_data['washout_percentage']]
    colors = ['#3274A1', '#3A923A', '#C03D3E']  # Match the kinetic curve colors
    
    # Data for harmonized pie chart
    harm_labels = ['Uptake', 'Plateau', 'Washout']
    harm_sizes = [harmonized_case_data['uptake_percentage'], harmonized_case_data['plateau_percentage'], harmonized_case_data['washout_percentage']]
    
    # Check if harmonized data is normalized (0-1 range)
    is_normalized = all(0 <= val <= 1 for val in harm_sizes)
      # For pie charts, if harmonized data is normalized to 0-1 scale,
    # we need to keep the proportional relationships but scale to match raw data
    # for consistent visualization
    if is_normalized:
        # Scale each value using the corresponding raw value as reference
        raw_sum = sum(raw_sizes)
        harm_sum = sum(harm_sizes)
        
        if harm_sum > 0 and raw_sum > 0:  # Avoid division by zero
            # Scale to match raw data proportionally
            scale_factor = raw_sum / harm_sum
            harm_sizes = [val * scale_factor for val in harm_sizes]
    
    # Raw data pie chart
    ax1.pie(raw_sizes, labels=raw_labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90)
    ax1.axis('equal')
    ax1.set_title(f"Raw Signal Distribution")
    
    # Harmonized data pie chart
    ax2.pie(harm_sizes, labels=harm_labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90)
    ax2.axis('equal')
    
    if is_normalized:
        ax2.set_title(f"Harmonized Signal Distribution\n(proportionally scaled for comparison)")
    else:
        ax2.set_title(f"Harmonized Signal Distribution")
    
    plt.tight_layout()
    
    # Convert plot to base64 string
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    plot_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return plot_base64

# Create colormap visualization
def generate_colormap_preview(case_id):
    # Path to colormap image
    dataset = case_id.split('_')[0]
    colormap_path = os.path.join(dataset, case_id, f"{case_id}_complete_colormap.png")
    
    if os.path.exists(colormap_path):
        with open(colormap_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    return None

# Get case metrics
def get_case_metrics(case_id, data):
    if case_id not in data['raw']['case_id'].values:
        return None
    
    raw_data = data['raw'][data['raw']['case_id'] == case_id].iloc[0]
    harmonized_data = data['harmonized'][data['harmonized']['case_id'] == case_id].iloc[0]
    
    metrics = {
        'uptake_percentage': raw_data['uptake_percentage'],
        'plateau_percentage': raw_data['plateau_percentage'],
        'washout_percentage': raw_data['washout_percentage'],
        'mean_intensity_change': raw_data['mean_intensity_change'],
        'kinetic_heterogeneity': raw_data['kinetic_heterogeneity'],
        'enhancement_entropy': raw_data['enhancement_entropy'],
        'uptake_intensity': raw_data['uptake_intensity'],
        'washout_severity': raw_data['washout_severity'],
        'total_pixels': raw_data['total_roi_pixels']
    }
    
    return metrics

# Get harmonization info to explain the difference between raw and harmonized values
def get_harmonization_info(data):
    raw_data = data['raw']
    harmonized_data = data['harmonized']
    
    info = {}
    
    # Calculate min/max/mean for raw and harmonized data across all cases
    for feature in ['uptake_percentage', 'plateau_percentage', 'washout_percentage']:
        if feature in raw_data.columns and feature in harmonized_data.columns:
            raw_min = raw_data[feature].min()
            raw_max = raw_data[feature].max()
            raw_mean = raw_data[feature].mean()
            
            harm_min = harmonized_data[feature].min()
            harm_max = harmonized_data[feature].max()
            harm_mean = harmonized_data[feature].mean()
            
            # Check if harmonized data is normalized (0-1 range)
            is_normalized = harm_max <= 1.0 and harm_min >= 0.0
            
            # Calculate typical scaling factor if normalized
            scaling_factor = None
            if is_normalized and raw_max > 0:
                scaling_factor = raw_max / harm_max if harm_max > 0 else None
            
            info[feature] = {
                'raw_min': raw_min,
                'raw_max': raw_max,
                'raw_mean': raw_mean,
                'harm_min': harm_min,
                'harm_max': harm_max,
                'harm_mean': harm_mean,
                'is_normalized': is_normalized,
                'scaling_factor': scaling_factor
            }
    
    return info

# Generate comparison between raw and harmonized curves
def generate_harmonization_comparison(case_id, data):
    if case_id not in data['raw']['case_id'].values or case_id not in data['harmonized']['case_id'].values:
        return None
    
    raw_case_data = data['raw'][data['raw']['case_id'] == case_id].iloc[0]
    harmonized_case_data = data['harmonized'][data['harmonized']['case_id'] == case_id].iloc[0]
      # Create figure with three subplots - 3 rows, 3 columns (increased height)
    fig = plt.figure(figsize=(15, 16))
    gs = plt.GridSpec(3, 3, figure=fig)
    
    # Create raw and harmonized plots for each feature type
    
    # 1. Uptake Comparison (top left)
    ax_uptake = fig.add_subplot(gs[0, 0])
    create_feature_comparison(ax_uptake, case_id, 'uptake_percentage', raw_case_data, harmonized_case_data, 'Uptake Comparison', 'blue')
    
    # 2. Plateau Comparison (top middle)
    ax_plateau = fig.add_subplot(gs[0, 1])
    create_feature_comparison(ax_plateau, case_id, 'plateau_percentage', raw_case_data, harmonized_case_data, 'Plateau Comparison', 'green')
    
    # 3. Washout Comparison (top right)
    ax_washout = fig.add_subplot(gs[0, 2])
    create_feature_comparison(ax_washout, case_id, 'washout_percentage', raw_case_data, harmonized_case_data, 'Washout Comparison', 'red')    # Create a new row for the kinetic curves to give them more space
    # 4. Raw Kinetic Curves (second row)
    ax_raw = fig.add_subplot(gs[1, :])
    create_kinetic_curves_subplot(ax_raw, case_id, raw_case_data, "Raw Kinetic Curves")
    
    # 5. Harmonized Kinetic Curves (third row)
    ax_harm = fig.add_subplot(gs[2, :])
    create_kinetic_curves_subplot(ax_harm, case_id, harmonized_case_data, "Harmonized Kinetic Curves (Scaled)", is_harmonized=True, ref_data=raw_case_data)
    
    plt.tight_layout()
    
    # Convert plot to base64 string
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    comparison_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return comparison_base64

# Helper function to create feature comparison subplots
def create_feature_comparison(ax, case_id, feature, raw_data, harmonized_data, title, color_name):
    # Get raw and harmonized values
    raw_val = raw_data[feature]
    harm_val = harmonized_data[feature]
    
    # Check if harmonized data is likely normalized (0-1 scale)
    is_normalized = 0 <= harm_val <= 1
    
    # Create a visualization with dual y-axes to show both scales
    if is_normalized:
        # Get dataset name from case_id
        dataset = case_id.split('_')[0]
        
        # Calculate scaling factor
        data_ratio = raw_val / harm_val if harm_val > 0 else 100.0
        
        # Create figure with two y-axes
        if color_name == 'blue':
            colors = ['#3274A1', '#5DA5DA']  # Dark blue, Light blue
        elif color_name == 'green':
            colors = ['#3A923A', '#60BD68']  # Dark green, Light green
        else:  # red
            colors = ['#C03D3E', '#E57373']  # Dark red, Light red
        
        # Use twin axes to show both scales        
        x = ['Raw', 'Harmonized']
        
        # First plot the raw value with percentage scale (left y-axis)
        bar1 = ax.bar(0, raw_val, width=0.35, color=colors[0], label='Raw')
        
        # Create a twin axis for harmonized data (right y-axis) with 0-1 scale
        ax2 = ax.twinx()
        bar2 = ax2.bar(1, harm_val, width=0.35, color=colors[1], label='Harmonized')
        
        # Set y-axis limits and labels
        ax.set_ylim(0, raw_val * 1.2)  # Left y-axis for raw (0-100)
        ax.set_ylabel('Raw Percentage (%)', color=colors[0])
        ax.tick_params(axis='y', labelcolor=colors[0])
        
        # Set the harmonized axis limit to a reasonable range
        max_limit = max(1.0, harm_val * 1.5)  # Ensure we show at least up to 1.0
        ax2.set_ylim(0, max_limit)
        ax2.set_ylabel('Harmonized Value (0-1 scale)', color=colors[1])
        ax2.tick_params(axis='y', labelcolor=colors[1])
        
        # Add value labels to the bars
        ax.text(0, raw_val/2, f'{raw_val:.1f}%', ha='center', va='center', 
                color='white', fontweight='bold')
        
        # For harmonized values
        if harm_val < 0.01:
            ax2.text(1, harm_val/2, f'{harm_val:.3e}', ha='center', va='center', 
                    color='white', fontweight='bold')
        else:
            ax2.text(1, harm_val/2, f'{harm_val:.3f}', ha='center', va='center', 
                    color='white', fontweight='bold')
        
        # Add scaling factor as text
        ax.text(0.5, raw_val*1.05, f'Scale Factor: {data_ratio:.1f}x', 
                ha='center', va='bottom', color='black', fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5'))
          # Set the x-axis ticks and labels
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Raw', 'Harmonized'])
    else:
        # For non-normalized data, just show side by side
        x = np.arange(2)
        width = 0.35
        
        if color_name == 'blue':
            colors = ['#3274A1', '#5DA5DA']
        elif color_name == 'green':
            colors = ['#3A923A', '#60BD68']
        else:  # red
            colors = ['#C03D3E', '#E57373']
        
        # Create bars
        bar1 = ax.bar(0, raw_val, width, color=colors[0], label='Raw')
        bar2 = ax.bar(1, harm_val, width, color=colors[1], label='Harmonized')
        
        # Annotate with percentage values
        ax.text(0, raw_val/2, f'{raw_val:.1f}%', ha='center', va='center', color='white', fontweight='bold')
        ax.text(1, harm_val/2, f'{harm_val:.1f}%', ha='center', va='center', color='white', fontweight='bold')
        
        # Set x-axis labels
        ax.set_xticks(x)
        ax.set_xticklabels(['Raw', 'Harmonized'])
        
        # Set y-axis limits based on the data
        max_val = max(raw_val, harm_val) * 1.2  # 20% headroom
        ax.set_ylim(0, max_val)
    
    # Add labels and title
    ax.set_title(title, fontsize=12, fontweight='bold')
    
    # Set y-axis label only for the primary axis (or if no twin axis)
    if not is_normalized:
        ax.set_ylabel('Percentage (%)')
      # Add grid - for dual y-axis setup, only add grid to left axis
    ax.grid(axis='y', alpha=0.3)

# Helper function to create kinetic curves subplot
def create_kinetic_curves_subplot(ax, case_id, case_data, title, is_harmonized=False, ref_data=None):
    # Time points
    time_points = np.linspace(0.0, 3.0, 100)
    
    # Set base parameters that are common for both raw and harmonized data
    if is_harmonized and ref_data is not None:
        # For harmonized data, use the raw data's intensity as baseline but adjust proportions
        # based on harmonized data percentages
        raw_uptake_pct = ref_data['uptake_percentage']
        raw_plateau_pct = ref_data['plateau_percentage'] 
        raw_washout_pct = ref_data['washout_percentage']
        
        harm_uptake_pct = case_data['uptake_percentage']
        harm_plateau_pct = case_data['plateau_percentage']
        harm_washout_pct = case_data['washout_percentage']
        
        # Check if harmonized data is normalized (0-1 scale)
        is_normalized = (0 <= harm_uptake_pct <= 1 and 
                         0 <= harm_plateau_pct <= 1 and 
                         0 <= harm_washout_pct <= 1)
        
        # Calculate scaling factor to match raw data scale
        if is_normalized:
            # Calculate average ratio between raw and harmonized values
            total_raw_pct = raw_uptake_pct + raw_plateau_pct + raw_washout_pct
            total_harm_pct = harm_uptake_pct + harm_plateau_pct + harm_washout_pct
            if total_harm_pct > 0:
                scale_factor = total_raw_pct / total_harm_pct
            else:
                scale_factor = 100.0  # Default if harmonized values are zero
                
            # Scale harmonized percentages to match raw scale
            harm_uptake_pct *= scale_factor
            harm_plateau_pct *= scale_factor
            harm_washout_pct *= scale_factor
        
        # Use raw data's intensity but harmonized data's percentages for curve heights
        uptake_intensity = ref_data['uptake_intensity']
        washout_severity = ref_data['washout_severity'] 
        
        # For harmonized data, adjust the curve strengths based on harmonized percentages
        uptake_strength = harm_uptake_pct / max(1.0, raw_uptake_pct)
        plateau_strength = harm_plateau_pct / max(1.0, raw_plateau_pct)
        washout_strength = harm_washout_pct / max(1.0, raw_washout_pct)
    else:
        # For raw data, use values as-is
        uptake_intensity = case_data['uptake_intensity']
        washout_severity = case_data['washout_severity']
        uptake_strength = 1.0
        plateau_strength = 1.0
        washout_strength = 1.0
    
    # Initial curve parameters - keep them constant regardless of the data
    initial_slope = 150
    max_intensity = uptake_intensity
    
    # Create base curve
    t_diverge = 1.2
    idx_diverge = int(t_diverge * len(time_points) / 3.0)
    
    base_curve = np.zeros_like(time_points)
    base_curve[:idx_diverge+1] = max_intensity * (1 - np.exp(-initial_slope * time_points[:idx_diverge+1]/max_intensity))
    
    # Create the three curve types
    uptake_curve = np.copy(base_curve)
    plateau_curve = np.copy(base_curve)
    washout_curve = np.copy(base_curve)
    
    # Value at divergence point
    diverge_value = base_curve[idx_diverge]
    
    # Slopes calculation with strength factors applied
    uptake_slope = max_intensity * 0.07 * uptake_strength
    plateau_slope = -max_intensity * 0.03 * plateau_strength
    washout_slope = -max_intensity * 0.12 * washout_severity * washout_strength
    
    # Apply slopes after divergence
    for i in range(idx_diverge+1, len(time_points)):
        dt = time_points[i] - time_points[idx_diverge]
        uptake_curve[i] = diverge_value + dt * uptake_slope
        plateau_curve[i] = diverge_value + dt * plateau_slope
        washout_curve[i] = diverge_value + dt * washout_slope
    
    # Plot curves
    ax.plot(time_points, uptake_curve, color='#3274A1', linewidth=2, label='Uptake')
    ax.plot(time_points, plateau_curve, color='#3A923A', linewidth=2, label='Plateau')
    ax.plot(time_points, washout_curve, color='#C03D3E', linewidth=2, label='Washout')
    
    # Add reference line
    ax.axvline(x=t_diverge, color='gray', linestyle='--', alpha=0.7)
    
    # Set labels and title
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Time point')
    ax.set_ylabel('Signal Intensity (%)')
    ax.set_xlim(0.0, 3.0)
    ax.set_ylim(0, max(120, max_intensity * 1.2))
    ax.legend()
    ax.grid(True, alpha=0.3)
    
@app.route('/')
def index():
    cases = get_available_cases()
    return render_template('index.html', cases=cases)

@app.route('/case/<case_id>')
def case_view(case_id):
    data = load_data()
    kinetic_curves = generate_kinetic_curves(case_id, data)
    pie_chart = generate_pie_chart(case_id, data)
    colormap = generate_colormap_preview(case_id)
    metrics = get_case_metrics(case_id, data)
    harmonization_comparison = generate_harmonization_comparison(case_id, data)
    harmonization_info = get_harmonization_info(data)
    
    # Get the raw and harmonized values for this specific case
    case_raw_data = data['raw'][data['raw']['case_id'] == case_id].iloc[0] if case_id in data['raw']['case_id'].values else None
    case_harmonized_data = data['harmonized'][data['harmonized']['case_id'] == case_id].iloc[0] if case_id in data['harmonized']['case_id'].values else None    # Create explanation text
    harmonization_explanation = ""
    if case_raw_data is not None and case_harmonized_data is not None:
        harmonization_explanation = "<strong>What is ComBat Harmonization?</strong> "
        harmonization_explanation += "ComBat harmonization reduces batch effects between different datasets by standardizing feature values. "
        harmonization_explanation += "This makes data from different centers and scanners more comparable by removing systematic biases. "
          # Check if the harmonized data is in the 0-1 range
        if all(0 <= case_harmonized_data[feat] <= 1 for feat in ['uptake_percentage', 'plateau_percentage', 'washout_percentage']):
            harmonization_explanation += "<br><br><strong>Understanding the Scale Difference:</strong> "
            harmonization_explanation += "The harmonized data has been normalized to a 0-1 scale, "
            harmonization_explanation += "while raw percentages are on a 0-100 scale. "
            harmonization_explanation += "<br><br><strong>Reading the Bar Charts:</strong> "
            harmonization_explanation += "Each comparison has <span style='color:#3274A1;'>LEFT AXIS</span> for raw data (0-100% scale) and "
            harmonization_explanation += "<span style='color:#5DA5DA;'>RIGHT AXIS</span> for harmonized data (0-1 scale). "
            harmonization_explanation += "This dual-axis approach allows you to see both values on their native scales. "
            harmonization_explanation += "The scale factor shows how much the harmonized value would need to be multiplied to match the raw scale."
        
        # Add explanation about the kinetic curves
        harmonization_explanation += "<br><br><strong>Kinetic Curves Visualization:</strong> "
        harmonization_explanation += "The kinetic curves display how the signal intensity changes over time for different tissue types. "
        harmonization_explanation += "For the harmonized curves, we've maintained the same intensity scale as the raw data but "
        harmonization_explanation += "adjusted the curve shapes to reflect the proportional changes from the harmonization process. "
        
        # Add explanation about the comparison value
        harmonization_explanation += "<br><br><strong>What to Look For:</strong> "
        harmonization_explanation += "When comparing raw and harmonized data, focus on the <em>relative proportions</em> between features "
        harmonization_explanation += "(uptake, plateau, washout) rather than their absolute values. "
        harmonization_explanation += "Harmonization preserves the important diagnostic characteristics while "
        harmonization_explanation += "making values more comparable across different scanners and institutions."
    
    return render_template(
        'case.html',
        case_id=case_id,
        kinetic_curves=kinetic_curves,
        pie_chart=pie_chart,
        colormap=colormap,
        metrics=metrics,
        harmonization_comparison=harmonization_comparison,
        harmonization_info=harmonization_info,
        harmonization_explanation=harmonization_explanation
    )

@app.route('/api/combat_visualization', methods=['GET', 'POST'])
def combat_visualization():
    try:
        # Make sure the static images directory exists
        static_images_dir = os.path.join('static', 'images')
        os.makedirs(static_images_dir, exist_ok=True)
        
        # Generate a dynamic output filename to avoid caching issues
        import time
        output_filename = f'combat_visualization_{int(time.time())}.png'
        output_path = os.path.join(static_images_dir, output_filename)
        
        # Import the visualization module and generate the visualization
        import combat_visualization as cv
        cv.create_combat_visualization(use_real_data=True, output_path=output_path)
        
        # Get summary statistics for the description
        data = load_data()
        raw_data = data['raw']
        harmonized_data = data['harmonized']
        
        # Calculate variance reduction
        variance_reduction = {}
        for feature in ['uptake_percentage', 'plateau_percentage', 'washout_percentage']:
            if feature in raw_data.columns and feature in harmonized_data.columns:
                total_raw_var = raw_data[feature].var()
                total_harmonized_var = harmonized_data[feature].var()
                
                if total_raw_var > 0:
                    reduction = 100 * (1 - total_harmonized_var / total_raw_var)
                    variance_reduction[feature] = min(99.9, max(0, reduction))
                else:
                    variance_reduction[feature] = 0
        
        # Prepare description
        description = "ComBat harmonization successfully applied to multiple datasets. "
        description += f"Variance reduction: "
        description += f"Uptake {variance_reduction.get('uptake_percentage', 0):.1f}%, "
        description += f"Plateau {variance_reduction.get('plateau_percentage', 0):.1f}%, "
        description += f"Washout {variance_reduction.get('washout_percentage', 0):.1f}%"
        
        # Return the image path and description
        return jsonify({
            'success': True, 
            'image_path': f'static/images/{output_filename}',
            'description': description
        })
    except Exception as e:
        print(f"Error generating ComBat visualization: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
