import os
import nibabel as nib
import numpy as np
import SimpleITK as sitk

def convert_to_rgb_nifti(img_ref_path, class_arr, out_path):
    """
    Αποθηκεύει το colormap ως RGB NIfTI για συμβατότητα με προγράμματα απεικόνισης όπως το Mango
    
    Args:
        img_ref_path: Διαδρομή προς το αρχείο αναφοράς για affine και header
        class_arr: Πίνακας με τις κατηγορίες (1:Uptake, 2:Plateau, 3:Washout)
        out_path: Διαδρομή για την αποθήκευση του RGB NIfTI αρχείου
    """
    # Φορτώνουμε την εικόνα αναφοράς με το ίδιο μέγεθος μέσω nibabel
    # για να αποφύγουμε προβλήματα διαστάσεων
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
            rgb_volume[mask, i] = c
    
    # Μετατρέπουμε το array σε μορφή συμβατή με RGB NIfTI
    rgb_dtype = np.dtype([('R', np.uint8), ('G', np.uint8), ('B', np.uint8)])
    
    # Αναδιαμορφώνουμε το array για συμβατότητα με το nibabel
    reshaped = np.zeros(class_arr.shape, dtype=rgb_dtype)
    reshaped['R'] = rgb_volume[:, :, :, 0]
    reshaped['G'] = rgb_volume[:, :, :, 1]
    reshaped['B'] = rgb_volume[:, :, :, 2]
    
    # Δημιουργία του τελικού NIfTI object
    rgb_nii = nib.Nifti1Image(reshaped, nii_orig.affine, header=nii_orig.header)
    
    # Ρύθμιση του header για το RGB NIfTI
    rgb_nii.header['datatype'] = 128  # RGB24
    rgb_nii.header['bitpix'] = 24     # 24-bit RGB
    
    # Αποθήκευση
    nib.save(rgb_nii, out_path)
    print(f"    Saved RGB NIfTI colormap: {out_path}")

def batch_convert_colormaps(base_dir):
    """
    Μετατροπή όλων των υφιστάμενων colormap.nii.gz σε RGB εκδόσεις
    
    Args:
        base_dir: Βασικός φάκελος του project
    """
    converted_count = 0
    datasets = ['DUKE', 'ISPY1', 'ISPY2', 'NACT']
    
    for dataset in datasets:
        dataset_dir = os.path.join(base_dir, dataset)
        if not os.path.isdir(dataset_dir):
            continue
            
        print(f"Processing {dataset} dataset...")
        
        # Βρίσκουμε όλους τους φακέλους περιπτώσεων
        case_dirs = [d for d in os.listdir(dataset_dir) 
                    if os.path.isdir(os.path.join(dataset_dir, d)) and d != 'segment']
        
        for case_id in case_dirs:
            case_path = os.path.join(dataset_dir, case_id)
            tp0_file = None
            colormap_file = None
            
            # Εύρεση των απαραίτητων αρχείων
            for file in os.listdir(case_path):
                if file.endswith('_0000.nii.gz'):
                    tp0_file = os.path.join(case_path, file)
                elif file.endswith('_colormap.nii.gz'):
                    colormap_file = os.path.join(case_path, file)
            
            if tp0_file and colormap_file:
                try:
                    # Φόρτωση του χάρτη κατηγοριών
                    class_arr = nib.load(colormap_file).get_fdata()
                    
                    # Παράγουμε το RGB NIfTI
                    rgb_out_path = colormap_file  # Αντικαθιστούμε το παλιό colormap
                    convert_to_rgb_nifti(tp0_file, class_arr, rgb_out_path)
                    
                    converted_count += 1
                    print(f"  ✓ Converted {case_id}")
                except Exception as e:
                    print(f"  ✗ Error converting {case_id}: {e}")
    
    print(f"Completed! Converted {converted_count} colormap files to RGB format.")

if __name__ == "__main__":
    base_dir = r"c:\Users\nickk\BiomedicalSignals"
    batch_convert_colormaps(base_dir)
