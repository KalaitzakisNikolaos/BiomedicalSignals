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
        
        # Δημιουργία οπτικοποίησης
        colors = [(0,0,0), (0,0,1), (0,1,0), (1,0,0)]
        custom_cmap = ListedColormap(colors)
        
        # Εύρεση της κεντρικής τομής όπου υπάρχει ROI
        roi_slices = []
        for z in range(colormap.shape[2]):
            if np.any(roi[:,:,z]):
                roi_slices.append(z)
        
        if not roi_slices:
            slice_idx = colormap.shape[2] // 2
        else:
            slice_idx = roi_slices[len(roi_slices) // 2]  # Μεσαία τομή με ROI
        
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(colormap[:, :, slice_idx], cmap=custom_cmap, vmin=0, vmax=3)
        cbar = plt.colorbar(im, ticks=[0, 1, 2, 3])
        cbar.ax.set_yticklabels(['Background', 'Uptake', 'Plateau', 'Washout'])
        
        plt.title(f'Ψευδο-χρωματικός χάρτης - {case_id} - Τομή {slice_idx}')
        img_out_path = os.path.join(dataset_dir, f"{case_id}_colormap_slice.png")
        plt.savefig(img_out_path)
        plt.close()
        
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
