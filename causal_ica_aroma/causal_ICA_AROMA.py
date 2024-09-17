#!/usr/bin/env python

# Based on the design of ICA-AROMA https://github.com/maartenmennes/ICA-AROMA/blob/master/ICA_AROMA.py

import argparse
import json
import os

try:
    # Attempt relative import (for package usage)
    from .causal_ICA_AROMA_functions import (
        reclassify_ICs_and_edit_motion_files,
        regress_out_nuissance,
        run_causal_discovery,
    )
except ImportError:
    # Fall back to absolute import (for standalone script usage)
    from causal_ICA_AROMA_functions import (
        reclassify_ICs_and_edit_motion_files,
        regress_out_nuissance,
        run_causal_discovery,
    )

"""PARSER"""

parser = argparse.ArgumentParser(description="Script to run graph ICA-AROMA")

# Required options
reqoptions = parser.add_argument_group("Required arguments")
reqoptions.add_argument(
    "-o",
    "-out_dir",
    dest="out_dir",
    type=str,
    required=True,
    help=(
        "Directory to write edited motion ICs list. Can be the same as "
        "original directory but will overwrite."
    ),
)

# fmriprep + AROMA mode
fmripreparomaoptions = parser.add_argument_group("Aroma Arguments")
fmripreparomaoptions.add_argument(
    "-i",
    "-fmri_scan_niigz",
    dest="input_fmri_scan_niigz",
    type=str,
    required=False,
    help=(
        "Input fMRI scan where motion components will be regressed  or. "
        "Assumes ICA-AROMA motion components have not already been regressed "
    ),
)
fmripreparomaoptions.add_argument(
    "-m",
    "-melodic_mixing_tsv",
    dest="input_melodic_mixing_tsv",
    type=str,
    required=True,
    help=(
        "Melodic mixing matrix; corresponds to IC time courses used for "
        "causal discovery."
    ),
)
fmripreparomaoptions.add_argument(
    "-n",
    "-aroma_noise_ICs_csv",
    dest="input_aroma_noise_ICs_csv",
    type=str,
    required=True,
    help=(
        "List of ICA-AROMA identified motion components. "
        "Will be edited to include newly identified motion ICs."
    ),
)
fmripreparomaoptions.add_argument(
    "-j",
    "-confound_timeseries_json",
    dest="input_confound_timeseries_json",
    type=str,
    required=True,
    help=(
        "Confound time series including features and classification of ICs "
        "as ICA-AROMA motion ICs. Will be edited to reflect newly identified "
        "motion ICs. json file."
    ),
)
fmripreparomaoptions.add_argument(
    "-t",
    "-confound_timeseries_tsv",
    dest="input_confound_timeseries_tsv",
    type=str,
    required=True,
    help=(
        "Confound time series including features and classification of ICs "
        "as ICA-AROMA motion ICs. Will be edited to reflect newly identified "
        "motion ICs. tsv file."
    ),
)

# non-Required options
nonreqoptions = parser.add_argument_group("non-Required arguments")
nonreqoptions.add_argument(
    "--overwrite",
    "--ow",
    dest="ow",
    required=False,
    action="store_true",
    help="Overwrite previous analysis.",
)
nonreqoptions.add_argument(
    "-c",
    "--causal_discovery_algorithm",
    dest="causal_discovery_algorithm",
    type=str,
    required=False,
    default="LiNGAM",
    choices=["PC", "LiNGAM"],
    help="Applied causal discovery algorithm.",
)
nonreqoptions.add_argument(
    "--causal_criterion",
    dest="causal_criterion",
    type=str,
    required=False,
    default="all_parents_aroma_motion",
    choices=["all_parents_aroma_motion"],
    help=(
        "Causal criterion to use. Current only option is to reclassify "
        "an IC as motion is all parents are aroma motion ICs."
    ),
)
nonreqoptions.add_argument(
    "--fsl_dir",
    dest="fsl_dir",
    type=str,
    required=False,
    default=(
        os.path.join(os.environ["FSLDIR"], "bin")
        if "FSLDIR" in os.environ
        else None
    ),
    help="Directory to installed FSL.",
)
nonreqoptions.add_argument(
    "--group",
    dest="group",
    required=False,
    action="store_true",
    help="Group analysis.",
)
nonreqoptions.add_argument(
    "--seed",
    dest="seed",
    type=int,
    required=False,
    default=1234,
    help="Random state for non-deterministic parts, e.g., FastICA.",
)

"""PARSE ARGUMENTS"""
args = parser.parse_args()

if args.fsl_dir is None and "FSLDIR" in os.environ:
    args.fsl_dir = os.path.join(os.environ["FSLDIR"], "bin")

input_melodic_mixing_tsv = args.input_melodic_mixing_tsv
input_aroma_noise_ICs_csv = args.input_aroma_noise_ICs_csv
input_confound_timeseries_json = args.input_confound_timeseries_json
input_confound_timeseries_tsv = args.input_confound_timeseries_tsv
input_fmri_scan_niigz = args.input_fmri_scan_niigz
out_dir = args.out_dir

assert os.path.exists(
    input_melodic_mixing_tsv
), f"{input_melodic_mixing_tsv} does not exist"
assert os.path.exists(
    input_aroma_noise_ICs_csv
), f"{input_aroma_noise_ICs_csv} does not exist"
assert os.path.exists(
    input_confound_timeseries_json
), f"{input_confound_timeseries_json} does not exist"
assert os.path.exists(
    input_confound_timeseries_tsv
), f"{input_confound_timeseries_tsv} does not exist"

if not os.path.isdir(out_dir):
    os.mkdir(out_dir)
elif os.path.isdir(out_dir) and not args.ow:
    print("{} exists and --overwrite not selected.".format(out_dir))
    exit()

descr = {
    "causal_discovery_algorithm": args.causal_discovery_algorithm,
    "causal_criterion": args.causal_criterion,
}

with open(os.path.join(out_dir, "description.json"), "w") as f:
    json.dump(descr, f)


prepend = args.input_aroma_noise_ICs_csv.split("/")[-1]
prepend = prepend.split(".")[0]
prepend = "_".join(prepend.split("_")[:-1]) + "_"

# Causal Discovery
print("#" * 10 + " Running Causal Discovery " + "#" * 10)
causal_DAG = run_causal_discovery(
    input_melodic_mixing_tsv,
    args.causal_discovery_algorithm,
    out_dir,
    args.seed,
    prepend,
)

# Reclassification
print("#" * 10 + " Reclassifying noiseICs based on Graph " + "#" * 10)
reclassification_is_success = reclassify_ICs_and_edit_motion_files(
    causal_DAG,
    args.input_aroma_noise_ICs_csv,
    args.input_melodic_mixing_tsv,
    args.input_confound_timeseries_json,
    args.input_confound_timeseries_tsv,
    args.causal_criterion,
    out_dir,
)

assert reclassification_is_success, "Causal reclassification did not succeed."

if args.group:
    readme_put_filename = "causal-discovery_{}_{}_group_".format(
        args.causal_discovery_algorithm, args.causal_criterion
    )
else:
    readme_put_filename = "causal-discovery_{}_{}_".format(
        args.causal_discovery_algorithm, args.causal_criterion
    )

with open(os.path.join(out_dir, "README"), "w") as f:
    f.write(readme_put_filename)

# Confound Regression
if input_fmri_scan_niigz and os.path.exists(args.fsl_dir):
    assert os.path.exists(
        input_fmri_scan_niigz
    ), f"{input_fmri_scan_niigz} does not exist"

    motion_IC_indices = []
    with open(args.input_aroma_noise_ICs_csv) as f:
        for line in f:
            line = line.rstrip().split(",")
            motion_IC_indices += [int(i) for i in line]

    print("#" * 10 + " Regressing  new noiseICs " + "#" * 10)
    regress_out_nuissance(
        args.fsl_dir,
        args.input_fmri_scan_niigz,
        out_dir,
        input_melodic_mixing_tsv,
        motion_IC_indices=motion_IC_indices,
    )
else:
    print(
        (
            "Either no in file passed in or FSL not installed, so regressing "
            "confounds is skipped, but newly identified motion components "
            "have been updated in confound files."
        )
    )
