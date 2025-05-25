import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.cm as cm
import glob

def create_colormap(case_id, dataset_dir, segment_dir):
    """
    Δημιουργία ψευδο-χρωματικού χάρτη για ένα συγκεκριμένο case
    
    Parameters:
    -----------
    case_id : str
        Το αναγνωριστικό του case (π.χ. "DUKE_032")
    dataset_dir : str
        Το directory που περιέχει τα δεδομένα του συγκεκριμένου case
    segment_dir : str
        Το directory που περιέχει τα αρχεία segmentation
    
    Returns:
    --------
    None
    """
    # Paths
    img_0000_path = os.path.join(dataset_dir, f"{case_id}_0000.nii.gz")
    img_0001_path = os.path.join(dataset_dir, f"{case_id}_0001.nii.gz")
    mask_path = os.path.join(segment_dir, f"{case_id}.nii.gz")
    
    # Έλεγχος αν τα αρχεία υπάρχουν
    if not os.path.exists(img_0000_path) or not os.path.exists(img_0001_path) or not os.path.exists(mask_path):
        print(f"Λείπουν αρχεία για το {case_id}, παραλείπεται...")
        return
    
    # Φόρτωση εικόνων και μάσκας
    try:
        img_0000 = nib.load(img_0000_path).get_fdata()
        img_0001 = nib.load(img_0001_path).get_fdata()
        mask = nib.load(mask_path).get_fdata()
        
        # Υπολογισμός μεταβολής έντασης
        intensity_change = np.zeros_like(img_0000)
        roi = mask > 0
        intensity_change[roi] = (img_0001[roi] - img_0000[roi]) / (img_0000[roi] + 1e-8) * 100  # % μεταβολή
        
        # Κατηγοριοποίηση
        colormap = np.zeros_like(img_0000, dtype=np.uint8)
        colormap[(intensity_change > 10) & roi] = 1  # Uptake
        colormap[(intensity_change <= 10) & (intensity_change >= -10) & roi] = 2  # Plateau
        colormap[(intensity_change < -10) & roi] = 3  # Washout
        
        # Αποθήκευση ως νέο NIfTI
        out_img = nib.Nifti1Image(colormap, affine=nib.load(img_0000_path).affine)
        out_path = os.path.join(dataset_dir, f"{case_id}_colormap.nii.gz")
        nib.save(out_img, out_path)
        
        # Δημιουργία οπτικοποίησης με overlay και βελτιωμένα χρώματα
        # Define new colors with alpha for overlay, matching the example graph:
        # Index 0 (Background in colormap): Transparent
        # Index 1 (Uptake): Pure Blue
        # Index 2 (Plateau): Pure Green
        # Index 3 (Washout): Pure Red
        colors = [
            (0, 0, 0, 0),      # Transparent for background
            (0, 0, 1, 0.7),    # Pure Blue with alpha for Uptake
            (0, 1, 0, 0.7),    # Pure Green with alpha for Plateau
            (1, 0, 0, 0.7)     # Pure Red with alpha for Washout
        ]
        custom_cmap = ListedColormap(colors)
        
        # Εύρεση της κεντρικής τομής όπου υπάρχει ROI
        roi_slices = []
        for z in range(colormap.shape[2]):
            if np.any(roi[:,:,z]): # Check if ROI exists in this slice
                roi_slices.append(z)
        
        if not roi_slices:
            # If no ROI found in any slice (e.g. empty mask), use middle slice of the volume
            slice_idx = colormap.shape[2] // 2
        else:
            slice_idx = roi_slices[len(roi_slices) // 2]  # Μεσαία τομή με ROI
        
        fig, ax = plt.subplots(figsize=(12, 10)) # Adjusted figure size
        
        # Display anatomical image (img_0000) as background
        ax.imshow(img_0000[:, :, slice_idx].T, cmap='gray', origin='lower', aspect='auto')
        
        # Overlay the colormap
        # Make sure the colormap array is oriented the same way as the anatomical image
        im = ax.imshow(colormap[:, :, slice_idx].T, cmap=custom_cmap, vmin=0, vmax=3, origin='lower', aspect='auto', alpha=0.7) # General alpha for the layer
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, ticks=[0.375, 1.125, 1.875, 2.625], fraction=0.046, pad=0.04) # Adjusted tick positions for centered labels
        cbar.ax.set_yticklabels(['Background', 'Uptake', 'Plateau', 'Washout'])
        cbar.ax.tick_params(labelsize=10)

        ax.set_title(f'Pseudo-color Map Overlay - {case_id} - Slice {slice_idx}', fontsize=14)
        ax.axis('off') # Turn off axis numbers and ticks
        
        plt.tight_layout()
        img_out_path = os.path.join(dataset_dir, f"{case_id}_colormap_slice.png")
        plt.savefig(img_out_path, dpi=200) # Slightly lower DPI for faster generation if needed, or keep 300
        plt.close(fig)
        
        print(f"{case_id}: Οι ψευδο-χρωματικοί χάρτες δημιουργήθηκαν επιτυχώς!")
        
    except Exception as e:
        print(f"Σφάλμα κατά την επεξεργασία του {case_id}: {e}")
        
def process_dataset(base_dir, dataset_name):
    """
    Επεξεργασία όλων των περιπτώσεων ενός συνόλου δεδομένων
    
    Parameters:
    -----------
    base_dir : str
        Η βασική διαδρομή του φακέλου εργασίας
    dataset_name : str
        Το όνομα του συνόλου δεδομένων (πχ. "DUKE", "ISPY1", "ISPY2", "NACT")
    """
    dataset_dir = os.path.join(base_dir, dataset_name)
    segment_dir = os.path.join(dataset_dir, "segment")
    
    # Εύρεση όλων των υπο-φακέλων που περιέχουν δεδομένα
    case_dirs = [d for d in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, d)) and d != "segment"]
    
    for case_dir in case_dirs:
        case_id = case_dir  # Το case_id είναι το ίδιο με το όνομα του φακέλου
        case_path = os.path.join(dataset_dir, case_dir)
        create_colormap(case_id, case_path, segment_dir)

def main():
    # Βασικός φάκελος δεδομένων
    base_dir = r'C:\\Users\\nickk\\Music\\BiomedicalSignals'
    
    # Επεξεργασία του συνόλου δεδομένων DUKE
    process_dataset(base_dir, "DUKE")
    process_dataset(base_dir, "ISPY1")
    process_dataset(base_dir, "ISPY2")
    process_dataset(base_dir, "NACT")
    print("Η επεξεργασία όλων των συνόλων δεδομένων ολοκληρώθηκε.")

if __name__ == "__main__":
    main()
