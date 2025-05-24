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
3. Run the provided Python scripts (to be implemented) for each analysis step.
4. Visualize results using [Mango Viewer](https://mangoviewer.com/) or similar tools.

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
3. Εκτελέστε τα Python scripts (θα υλοποιηθούν) για κάθε βήμα ανάλυσης.
4. Οπτικοποιήστε τα αποτελέσματα με το [Mango Viewer](https://mangoviewer.com/) ή παρόμοια εργαλεία.

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
