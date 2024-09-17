#!/usr/bin/env python

# Functions for Causal-ICA-AROMA v0.1 beta
# Based on the design of:
# https://github.com/maartenmennes/ICA-AROMA/blob/master/ICA_AROMA_functions.py

import json
import os
import pickle

import networkx as nx
import numpy as np
import pandas as pd
from causallearn.search.ConstraintBased.PC import pc
from causallearn.search.FCMBased.lingam import ICALiNGAM


def run_causal_discovery(
    melodic_mixing_tsv, causal_discover_algorithm, out_dir, seed, prepend=""
):
    melodic_mixing_df = pd.read_csv(melodic_mixing_tsv, sep="\t", header=None)
    melodic_mixing_df.columns = [
        i + 1 for i in range(melodic_mixing_df.shape[1])
    ]
    if causal_discover_algorithm == "LiNGAM":
        adj_matrix = (
            ICALiNGAM(seed).fit(melodic_mixing_df.values).adjacency_matrix_
        )
        causal_DAG = nx.from_numpy_array(adj_matrix, create_using=nx.DiGraph)

        node_name_mapping = {node: node + 1 for node in causal_DAG.nodes}
        causal_DAG = nx.relabel_nodes(causal_DAG, node_name_mapping)
    elif causal_discover_algorithm == "PC":
        causal_DAG = pc(melodic_mixing_df.values, indep_test="kci").nx_graph

        node_name_mapping = {node: node + 1 for node in causal_DAG.nodes}
        causal_DAG = nx.relabel_nodes(causal_DAG, node_name_mapping)
    else:
        raise NotImplementedError()

    if out_dir:
        outFile = os.path.join(
            out_dir,
            "{}{}_graph.gpickle".format(prepend, causal_discover_algorithm),
        )
        with open(outFile, "wb") as f:
            pickle.dump(causal_DAG, f, pickle.HIGHEST_PROTOCOL)
        return outFile


def reclassify_ICs_and_edit_motion_files(
    causal_graph_file_name,
    aroma_noise_ICs_csv,
    melodic_mixing_tsv,
    melodic_mixing_json,
    confound_timeseries_tsv,
    causal_criterion,
    out_dir,
):

    with open(causal_graph_file_name, "rb") as f:
        causal_DAG = pickle.load(f)

    aroma_motion_ICs = []

    with open(aroma_noise_ICs_csv, "r") as f:
        for line in f:
            line = line.rstrip().split(",")
            aroma_motion_ICs += [int(i) for i in line]

    updated_motion_ICs = get_updated_motion_ICs(
        causal_DAG, causal_criterion, aroma_motion_ICs
    )

    edit_motion_files_is_success = edit_motion_files(
        updated_motion_ICs,
        aroma_noise_ICs_csv,
        melodic_mixing_tsv,
        melodic_mixing_json,
        confound_timeseries_tsv,
        out_dir,
    )

    assert edit_motion_files_is_success

    causal_criterion_motion_ICs = list(
        set(updated_motion_ICs) - set(aroma_motion_ICs)
    )
    causal_criterion_motion_ICs.sort()

    print(aroma_motion_ICs)
    print(causal_criterion_motion_ICs)
    print(updated_motion_ICs)

    with open(os.path.join(out_dir, "CausalCriterionNoiseICs.csv"), "w") as f:
        f.write(",".join([str(i) for i in causal_criterion_motion_ICs]))
    with open(os.path.join(out_dir, "AromaNoiseICs.csv"), "w") as f:
        f.write(",".join([str(i) for i in aroma_motion_ICs]))

    return True


def get_updated_motion_ICs(G, causal_criterion, aroma_motion_ICs):
    # Read nuissance ICs; note update motion will include AROMA motion
    updated_motion_ICs = []

    for n in G.nodes():
        if n in aroma_motion_ICs:  # add AROMA motion
            updated_motion_ICs.append(n)
            continue
        parents, children = list(G.predecessors(n)), list(G.successors(n))
        if reclassify_ICs(
            parents, children, causal_criterion, aroma_motion_ICs
        ):  # checks if new motion and adds new motion
            updated_motion_ICs.append(n)

    updated_motion_ICs.sort()

    return updated_motion_ICs


def reclassify_ICs(parents, children, causal_criterion, aroma_motion_ICs):
    if causal_criterion == "all_parents_aroma_motion":
        if len(parents) == 0:
            return False
        return all([i in aroma_motion_ICs for i in parents])
    else:
        raise ValueError(
            ("criteria must be one of" "['all_parents_aroma_motion']")
        )


def edit_motion_files(
    updated_motion_ICs,
    aroma_noise_ICs_csv,
    melodic_mixing_tsv,
    confound_timeseries_json,
    confound_timeseries_tsv,
    out_dir,
):

    melodic_mixing_df = pd.read_csv(melodic_mixing_tsv, sep="\t", header=None)

    # Make columns start from 1 instead of 0
    melodic_mixing_df.columns = [
        i + 1 for i in range(melodic_mixing_df.shape[1])
    ]

    confound_timeseries_df = pd.read_csv(confound_timeseries_tsv, sep="\t")

    confound_timeseries_dict = json.load(open(confound_timeseries_json, "r"))
    motion_columns = []

    for n in updated_motion_ICs:
        motion_column = "aroma_motion_{:02d}".format(n)
        motion_key = "aroma_motion_{}".format(n)

        motion_columns.append(motion_column)

        # Updating potential confound dict
        confound_timeseries_dict[motion_key]["MotionNoise"] = True

        if motion_column in confound_timeseries_df.columns:
            # Sanity check that values are the same -- with tolerance for
            # float precision issues for AROMA motions
            assert all(
                np.abs(
                    confound_timeseries_df[motion_column].values
                    - melodic_mixing_df[n].values
                )
                < 1e-6
            )
        else:
            # Add new motion from Causal ICA-AROMA to confound regression df
            confound_timeseries_df[motion_column] = melodic_mixing_df[n].values

    updated_motion_ICs = pd.DataFrame(data=updated_motion_ICs).T
    updated_motion_ICs.to_csv(
        os.path.join(out_dir, os.path.basename(aroma_noise_ICs_csv)),
        header=False,
        index=False,
    )

    # Mostly for aesthetics to keep ICs confounds together
    causal_aroma_motion_df = confound_timeseries_df[motion_columns]
    confound_timeseries_df = confound_timeseries_df.drop(
        motion_columns, axis=1
    )
    confound_timeseries_df = pd.concat(
        [confound_timeseries_df, causal_aroma_motion_df], axis=1
    )

    json.dump(
        confound_timeseries_dict,
        open(
            os.path.join(out_dir, os.path.basename(confound_timeseries_json)),
            "w",
        ),
        indent=2,
    )
    confound_timeseries_df.to_csv(
        open(
            os.path.join(out_dir, os.path.basename(confound_timeseries_tsv)),
            "w",
        ),
        sep="\t",
        index=False,
    )

    return True


def regress_out_nuissance(
    fsl_dir,
    fmri_scan_niigz,
    out_dir,
    melodic_mixing_tsv,
    denoising_type="nonaggr",
    motion_IC_indices=[],
):
    """This function classifies the ICs based on the four features;
    maximum RP correlation, high-frequency content, edge-fraction and
    CSF-fraction

    Parameters
    --------------------------------------------------------------------------
    fslDir:     Full path of the bin-directory of FSL
    fmri_scan_niigz:     Full path to the data file (nii.gz) which has to be
    denoised
    out_dir:     Full path of the output directory
    melodic_mixing_tsv:     Full path of the melodic_mix text file
    denoising_type:    Type of requested denoising ('aggr': aggressive,
        'nonaggr': non-aggressive, 'both': both aggressive and non-aggressive
    motion_ICs:     Indices of the components that should be regressed out

    Output (within the requested output directory)
    --------------------------------------------------------------------------
    causal_AROMA_denoised_func_data_<denType>.nii.gz:        A nii.gz file of
        the denoised fMRI data
    """

    # Import required modules
    import os

    import numpy as np

    # Check if additional (Causal) denoising is needed (i.e. are there new
    # components classified as motion)
    denoise = motion_IC_indices.size > 0

    if denoise:
        # Put IC indices into a char array
        if motion_IC_indices.size == 1:
            den_idx_str_join = "%d" % motion_IC_indices
        else:
            den_idx_str = np.char.mod("%i", motion_IC_indices)
            den_idx_str_join = ",".join(den_idx_str)

        # Non-aggressive denoising of the data using fsl_regfilt (partial
        # regression), if requested
        if (denoising_type == "nonaggr") or (denoising_type == "both"):
            os.system(
                " ".join(
                    [
                        os.path.join(fsl_dir, "fsl_regfilt"),
                        "--in=" + fmri_scan_niigz,
                        "--design=" + melodic_mixing_tsv,
                        '--filter="' + den_idx_str_join + '"',
                        "--out="
                        + os.path.join(
                            out_dir,
                            "causal_AROMA_denoised_func_data_nonaggr.nii.gz",
                        ),
                    ]
                )
            )

        # Aggressive denoising of the data using fsl_regfilt (full regression)
        if (denoising_type == "aggr") or (denoising_type == "both"):
            os.system(
                " ".join(
                    [
                        os.path.join(fsl_dir, "fsl_regfilt"),
                        "--in=" + fmri_scan_niigz,
                        "--design=" + melodic_mixing_tsv,
                        '--filter="' + den_idx_str_join + '"',
                        "--out="
                        + os.path.join(
                            out_dir,
                            "causal_AROMA_denoised_func_data_aggr.nii.gz",
                        ),
                        "-a",
                    ]
                )
            )
