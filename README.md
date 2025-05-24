# MAMA-MIA DCE-MRI Analysis Project

<p align="center">
  <img src="images/mamamia_logo.png" alt="MAMA-MIA Logo" width="200"/>
</p>

---

## Overview
This project provides a complete pipeline for the analysis of dynamic contrast-enhanced magnetic resonance imaging (DCE-MRI) data from the MAMA-MIA public dataset. The workflow includes:

1. **Biomarker Extraction** from DCE-MRI sequences with contrast agent.
2. **Pseudo-color Map Generation** based on biomarker characteristics.
3. **Signal Harmonization** using the ComBat technique for multicenter data.

---

## Example Images

### Example 1: DCE-MRI with Tumor Segmentation
<p align="center">
  <img src="images/example1.png" alt="DCE-MRI with Tumor Segmentation" width="400"/>
</p>

### Example 2: Segmentation Mask Overlay
<p align="center">
  <img src="images/example2.png" alt="Segmentation Mask Overlay" width="400"/>
</p>

### Example 3: Pseudo-color Map (Uptake/Plateau/Washout)
<p align="center">
  <img src="images/example3.png" alt="Pseudo-color Map" width="400"/>
</p>

---

## Project Structure
- `DUKE/`, `ISPY1/`, `ISPY2/`, `NACT/`: Folders for each study group, each containing subfolders for individual cases and their respective DCE-MRI timepoints (e.g., `*_0000.nii.gz`, `*_0001.nii.gz`, ...).
- `segment/`: Contains segmentation masks for each case (e.g., `DUKE_032.nii.gz`).
- `process_all_data.py`: Main Python script for generating pseudo-color maps from the DCE-MRI data.
- `images/`: Contains example images and logos used in this README.

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
- **Pseudo-color Maps:** `*_colormap.nii.gz` (e.g., `DUKE_032_colormap.nii.gz`)
  - NIfTI format images containing the classified voxels:
  - Value 0: Background (no ROI)
  - Value 1: Uptake (>10% intensity increase)
  - Value 2: Plateau (-10% to +10% intensity change)
  - Value 3: Washout (<-10% intensity decrease)
  
- **Visualization Images:** `*_colormap_slice.png` (e.g., `DUKE_032_colormap_slice.png`)
  - PNG images showing a central slice of the pseudo-color map
  - Color coding:
    - Black: Background
    - Blue: Uptake
    - Green: Plateau
    - Red: Washout
  - Includes a color legend for easy interpretation

The `process_all_data.py` script automatically generates these output files by:
1. Loading the pre and post-contrast images
2. Applying the ROI mask to isolate the region of interest
3. Calculating the percentage intensity change between timepoints
4. Classifying each voxel according to its enhancement pattern
5. Saving the results as both NIfTI (.nii.gz) and visualization (.png) files

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
- Extract radiomic features from the ROI using PyRadiomics.
- Harmonize features across centers using the ComBat technique (e.g., via `neuroCombat`).
- Compare feature distributions before and after harmonization.

---

## Usage
1. Download the MAMA-MIA dataset from [Synapse](https://www.synapse.org/Synapse:syn60868042/files/).
2. Place the data in the corresponding folders as shown above.
3. Install required Python packages:
   ```
   pip install nibabel numpy matplotlib SimpleITK pandas
   ```
4. Run the `process_all_data.py` script to generate pseudo-color maps:
   ```
   python process_all_data.py
   ```
5. The script will process all available cases and create:
   - `*_colormap.nii.gz` - NIfTI files with classified voxels
   - `*_colormap_slice.png` - PNG visualization images
6. Visualize results using [Mango Viewer](https://mangoviewer.com/) or similar tools.

**Note**: Due to the large size of the NIfTI input files (`*_0000.nii.gz`, `*_0001.nii.gz`), they are not included in this repository. However, the processed output files (`*_colormap.nii.gz` and `*_colormap_slice.png`) are included for reference.

---

## Requirements
- Python 3.8+
- nibabel
- numpy
- PyRadiomics
- neuroCombat or similar

---

## References
- [MAMA-MIA Dataset](https://www.synapse.org/Synapse:syn60868042/files/)
- [PyRadiomics Documentation](https://pyradiomics.readthedocs.io/en/latest/)
- [neuroCombat](https://github.com/Jfortin1/neuroCombat)

---

# Ελληνικά

## Περιγραφή
Αυτό το έργο παρέχει μια πλήρη ροή ανάλυσης για δεδομένα DCE-MRI από τη δημόσια βάση MAMA-MIA. Περιλαμβάνει:

1. **Εξαγωγή βιοσημάτων** από ακολουθίες DCE-MRI με σκιαγραφικό.
2. **Δημιουργία ψευδο-χρωματικού χάρτη** με βάση τα χαρακτηριστικά του βιοσήματος.
3. **Ομογενοποίηση σημάτων** με τη μέθοδο ComBat για πολυκεντρικά δεδομένα.

---

## Δομή Έργου
- `DUKE/`, `ISPY1/`, `ISPY2/`, `NACT/`: Φάκελοι για κάθε ομάδα με υποφακέλους για κάθε περίπτωση και τα αντίστοιχα χρονικά σημεία DCE-MRI (π.χ. `*_0000.nii.gz`, `*_0001.nii.gz`, ...).
- `segment/`: Περιέχει τις μάσκες τμηματοποίησης για κάθε περίπτωση (π.χ. `DUKE_032.nii.gz`).
- `process_all_data.py`: Κύριο Python script για τη δημιουργία ψευδο-χρωματικών χαρτών από τα δεδομένα DCE-MRI.
- `images/`: Περιέχει παραδείγματα εικόνων και λογότυπα για αυτό το README.

## Αρχεία Δεδομένων

### Αρχεία Εισόδου (Δεν περιλαμβάνονται στο αποθετήριο λόγω περιορισμών μεγέθους)
- **Χρονικά Σημεία DCE-MRI:** `*_0000.nii.gz`, `*_0001.nii.gz` (π.χ. `DUKE_032_0000.nii.gz`, `DUKE_032_0001.nii.gz`)
  - Είναι οι ακατέργαστες εικόνες σε μορφή NIfTI από το σύνολο δεδομένων MAMA-MIA
  - `*_0000.nii.gz`: Εικόνα πριν το σκιαγραφικό (t=0)
  - `*_0001.nii.gz`: Εικόνα μετά το σκιαγραφικό (t=1)
  
- **Αρχεία Τμηματοποίησης:** `*/segment/*.nii.gz` (π.χ. `DUKE/segment/DUKE_032.nii.gz`)
  - Τα αρχεία αυτά περιέχουν τις τμηματοποιήσεις (μάσκες) των περιοχών ενδιαφέροντος (ROI)
  - Χρησιμοποιούνται για την αναγνώριση των περιοχών του όγκου ή ιστού προς ανάλυση

### Αρχεία Εξόδου (Περιλαμβάνονται στο αποθετήριο)
- **Ψευδο-χρωματικοί Χάρτες:** `*_colormap.nii.gz` (π.χ. `DUKE_032_colormap.nii.gz`)
  - Εικόνες σε μορφή NIfTI που περιέχουν τα ταξινομημένα voxels:
  - Τιμή 0: Φόντο (χωρίς ROI)
  - Τιμή 1: Uptake (>10% αύξηση έντασης)
  - Τιμή 2: Plateau (-10% έως +10% μεταβολή έντασης)
  - Τιμή 3: Washout (<-10% μείωση έντασης)
  
- **Εικόνες Οπτικοποίησης:** `*_colormap_slice.png` (π.χ. `DUKE_032_colormap_slice.png`)
  - Εικόνες PNG που δείχνουν μια κεντρική τομή του ψευδο-χρωματικού χάρτη
  - Χρωματική κωδικοποίηση:
    - Μαύρο: Φόντο
    - Μπλε: Uptake
    - Πράσινο: Plateau
    - Κόκκινο: Washout
  - Περιλαμβάνουν υπόμνημα χρωμάτων για εύκολη ερμηνεία

Το script `process_all_data.py` δημιουργεί αυτόματα αυτά τα αρχεία εξόδου:
1. Φορτώνοντας τις εικόνες πριν και μετά το σκιαγραφικό
2. Εφαρμόζοντας τη μάσκα ROI για να απομονώσει την περιοχή ενδιαφέροντος
3. Υπολογίζοντας την ποσοστιαία μεταβολή έντασης μεταξύ των χρονικών σημείων
4. Ταξινομώντας κάθε voxel σύμφωνα με το μοτίβο ενίσχυσής του
5. Αποθηκεύοντας τα αποτελέσματα ως αρχεία NIfTI (.nii.gz) και εικόνες οπτικοποίησης (.png)

---

## Αναλυτικά Βήματα

### 1. Εξαγωγή Βιοσημάτων
- Για κάθε περίπτωση, εξάγετε την περιοχή ενδιαφέροντος (ROI) με τη μάσκα τμηματοποίησης.
- Χρησιμοποιήστε Python (nibabel, numpy) για επεξεργασία NIfTI εικόνων.
- Εξάγετε τιμές έντασης για το ROI στα χρονικά σημεία 0000 και 0001.

### 2. Δημιουργία Ψευδο-χρωματικού Χάρτη
- Για κάθε εικονοστοιχείο του ROI, υπολογίστε τη μεταβολή έντασης μεταξύ χρονικών σημείων (π.χ. 0000 και 0001).
- Κατατάξτε κάθε voxel σε:
  - **Uptake (1):** >10% αύξηση
  - **Plateau (2):** ~10% μεταβολή
  - **Washout (3):** <10% μείωση
- Αποθηκεύστε τον χάρτη ταξινόμησης ως νέα εικόνα NIfTI.

### 3. Ομογενοποίηση Σημάτων (ComBat)
- Εξάγετε χαρακτηριστικά radiomics από το ROI με PyRadiomics.
- Ομογενοποιήστε τα χαρακτηριστικά με τη μέθοδο ComBat (π.χ. `neuroCombat`).
- Συγκρίνετε τις κατανομές πριν και μετά την ομογενοποίηση.

---

## Οδηγίες Χρήσης
1. Κατεβάστε τα δεδομένα MAMA-MIA από [Synapse](https://www.synapse.org/Synapse:syn60868042/files/).
2. Τοποθετήστε τα δεδομένα στους αντίστοιχους φακέλους όπως παραπάνω.
3. Εγκαταστήστε τις απαραίτητες βιβλιοθήκες Python:
   ```
   pip install nibabel numpy matplotlib SimpleITK pandas
   ```
4. Εκτελέστε το script `process_all_data.py` για να δημιουργήσετε τους ψευδο-χρωματικούς χάρτες:
   ```
   python process_all_data.py
   ```
5. Το script θα επεξεργαστεί όλες τις διαθέσιμες περιπτώσεις και θα δημιουργήσει:
   - `*_colormap.nii.gz` - Αρχεία NIfTI με ταξινομημένα voxels
   - `*_colormap_slice.png` - Εικόνες οπτικοποίησης PNG
6. Οπτικοποιήστε τα αποτελέσματα με το [Mango Viewer](https://mangoviewer.com/) ή παρόμοια εργαλεία.

**Σημείωση**: Λόγω του μεγάλου μεγέθους των αρχείων εισόδου NIfTI (`*_0000.nii.gz`, `*_0001.nii.gz`), δεν περιλαμβάνονται σε αυτό το αποθετήριο. Ωστόσο, τα αρχεία εξόδου (`*_colormap.nii.gz` και `*_colormap_slice.png`) περιλαμβάνονται για αναφορά.

---

## Απαιτήσεις
- Python 3.8+
- nibabel
- numpy
- PyRadiomics
- neuroCombat ή αντίστοιχο

---

## Βιβλιογραφία
- [MAMA-MIA Dataset](https://www.synapse.org/Synapse:syn60868042/files/)
- [PyRadiomics Documentation](https://pyradiomics.readthedocs.io/en/latest/)
- [neuroCombat](https://github.com/Jfortin1/neuroCombat)

---

## Credits

<p align="center">
  <img src="images/hmu_logo.png" alt="Hellenic Mediterranean University Logo" width="120"/>
</p>

<p align="center">
  <b>Developed by Kalaitzakis Nikolaos</b><br>
  Hellenic Mediterranean University
</p>
