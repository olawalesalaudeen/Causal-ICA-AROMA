# Apptainer image
Build command:
```sh
apptainer build causal-ica-aroma.sif causal-ica-aroma.def
```

Usage:

On CPU:
```sh
apptainer run --cleanenv --contain -B /path/to/bids/derivatives:/datain,/path/to/Causal-ICA-AROMA-outputs:/out causal-ica-aroma_dev.sif -o /out -i /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_space-T1w_desc-preproc_bold.nii.gz -m /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-MELODIC_mixing.tsv -n /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_AROMAnoiseICs.csv -j /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-confounds_timeseries.json -t /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-confounds_timeseries.tsv
```

With CUDA GPU:
```sh
apptainer run --nv --cleanenv --contain -B /path/to/bids/derivatives:/datain,/path/to/Causal-ICA-AROMA-outputs:/out causal-ica-aroma_dev.sif -o /out -i /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_space-T1w_desc-preproc_bold.nii.gz -m /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-MELODIC_mixing.tsv -n /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_AROMAnoiseICs.csv -j /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-confounds_timeseries.json -t /datain/fmriprep/sub-001/ses-A/func/sub-001_ses-A_task-rest_dir-AP_run-1_desc-confounds_timeseries.tsv
```

