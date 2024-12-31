
# Causal-ICA-AROMA

Causal-ICA-AROMA is a data-driven method designed to enhance [ICA-AROMA](https://github.com/maartenmennes/ICA-AROMA) in the identification and removal of motion-related components in fMRI data [1].

Causal-ICA-AROMA requires the output from fmriprep's ICA-AROMA outputs as input. After fmriprep's ICA-AROMA is completed, Causal-ICA-AROMA identifies additional motion-related independent components that were not detected by ICA-AROMA. It achieves this by leveraging causal discovery to learn a causal graph of the time courses of the spatially independent components of the fMRI data, obtained via Independent Component Analysis (ICA) [2]. Causal-ICA-AROMA then applies a simple criterion to reclassify motion components: any component that is strictly caused by ICA-AROMA-identified motion components is reclassified as a motion component.

This package requires **Python**, **FSL**, and the **Causal Learn** package [3-4].

---

## Table of Contents
1. [References](#references)
2. [Required Tools](#required-tools)
3. [Installation and Usage](#installation-and-usage)
    - [Package](#package)
    - [Apptainer Image](#apptainer-image)

---

## References

1. Pruim, Raimon HR, et al. "ICA-AROMA: A robust ICA-based strategy for removing motion artifacts from fMRI data." *Neuroimage* 112 (2015): 267-277.<br>
2. Shimizu, Shohei. "LiNGAM: Non-Gaussian methods for estimating causal structures." *Behaviormetrika* 41.1 (2014): 65-98.<br>
3. Zheng, Yujia, et al. "Causal-learn: Causal discovery in python." *Journal of Machine Learning Research* 25.60 (2024): 1-8.<br>
4. Jenkinson, Mark, et al. "FSL." *Neuroimage* 62.2 (2012): 782-790.

---

## Required Tools

Ensure you have the following tools installed:

- **Python 3.11**
- [ICA-AROMA](https://github.com/maartenmennes/ICA-AROMA)
- [Causal Learn](https://causal-learn.readthedocs.io)
- [FSL](https://fsl.fmrib.ox.ac.uk/fsl/docs/#/)

**Note**: Ensure FSL is installed and accessible from your system's PATH before using this package.

---

## Installation and Usage

### Package

#### Installation
From PyPI:
```sh
pip install causal_ica_aroma
```

Local build:
```sh
pip install -e .
```

---

#### Usage
Run the following command after installation:
```sh
python -m causal_ica_aroma.causal_ICA_AROMA \
  -c LiNGAM \
  -o out \
  -i /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_space-T1w_desc-preproc_bold.nii.gz \
  -m /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-MELODIC_mixing.tsv \
  -n /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_AROMAnoiseICs.csv \
  -j /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-confounds_timeseries.json \
  -t /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-confounds_timeseries.tsv
```

'out' should be /datain/fmriprep/sub-001/ses-A/func to update motion files in fmriprep output for followup analysis, but can be another directory.

---

### Apptainer Image

#### Installation
An Ubuntu-based Apptainer recipe is provided for installing required Python and R packages, FSL, and other dependencies: [apptainer/causal-ica-aroma.def](apptainer/causal-ica-aroma.def)

##### Build Command:
```sh
apptainer build causal-ica-aroma.sif apptainer/causal-ica-aroma.def
```

#### Usage
##### On CPU:
```sh
apptainer run --cleanenv --contain -B /path/to/bids/derivatives:/datain,/path/to/Causal-ICA-AROMA-outputs:/out causal-ica-aroma.sif \
  -c LiNGAM \
  -o out \
  -i /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_space-T1w_desc-preproc_bold.nii.gz \
  -m /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-MELODIC_mixing.tsv \
  -n /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_AROMAnoiseICs.csv \
  -j /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-confounds_timeseries.json \
  -t /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-confounds_timeseries.tsv
```

##### With CUDA GPU:
```sh
apptainer run --nv --cleanenv --contain -B /path/to/bids/derivatives:/datain,/path/to/Causal-ICA-AROMA-outputs:/out causal-ica-aroma.sif \
  -c LiNGAM \
  -o out \
  -i /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_space-T1w_desc-preproc_bold.nii.gz \
  -m /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-MELODIC_mixing.tsv \
  -n /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_AROMAnoiseICs.csv \
  -j /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-confounds_timeseries.json \
  -t /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-confounds_timeseries.tsv
```

'out' should be /datain/fmriprep/sub-001/ses-A/func to update motion files in fmriprep output for followup analysis, but can be another directory.
