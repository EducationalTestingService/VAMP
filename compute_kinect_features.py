#!/usr/bin/env python
# License: MIT
"""
Extracts high-level, expressive body language features from
a time-series motion trace. Extraction is on a per frame basis.

:author: Ben Leong (cleong@ets.org)

"""


import ConfigParser
import os
import sys
import json
import csv
import re
from os.path import join
sys.path.append('BVHplay/')

import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)

from skeleton import skeleton, process_bvhfile
import pandas as pd
import numpy as np


def readConfig(configFilename):
    """
    Reads from a config file the required inputs to begin recursive parsing.

    Args:
    configFilename (txt): contains
        (i) the path to the list of sync files i.e. the
        prefix of a set of video, wave and BVH files that are
        synchronized e.g. Lab001 for the set Lab001.avi, Lab001.wav,
        Lab001.bvh
        (ii) the path to the directory where these synchronized files
        reside
        (iii) the set of body parts whose time-series, Cartesian
        coordinates are extracted
        (iv) the frame rate of the BVH
        (v) the output directory where the extracted time-series,
        high-level features are stored

    Returns:
        a sequence of strings : parsed inputs from config file
    """
    parser = ConfigParser.SafeConfigParser()
    parser.read(configFilename)

    sync_files_list = parser.get("inputs", "sync_files_list")
    sync_files_dir = parser.get("inputs", "sync_files_dir")
    body_parts_specification = parser.get("inputs", "body_parts_specification")
    frame_rate = float(parser.get("inputs", "frame_rate"))
    output_dir = parser.get("outputs", "output_dir")

    return sync_files_list, sync_files_dir, \
        body_parts_specification, frame_rate, output_dir


def read_body_part_weights(body_part_json):
    """
    Reads from a JSON formatted file the set of body parts and their
    weights.

    Args:
        body_part_json (json): a JSON formatted specifying body parts
                        and weights

    Returns:
        list: list of weights indexed by body parts
    """
    with open(body_part_json) as data_file:
        weights = json.load(data_file)['weights']
        return weights


def read_symmetry_params(body_part_json):
    """
    Reads from a JSON formatted file the body symmetry parameters.

    Args:
        body_part_json (json): a JSON formatted file specifying the
                body part forming the axis of the symmetry (anchor) and
                the symmetrical body parts around the axis (parts).

    Returns:
        a string and list of strings: anchor, list of parts
    """
    with open(body_part_json) as data_file:
        symmetry_params = json.load(data_file)['symmetry']
        anchor = symmetry_params['anchor']
        parts = symmetry_params['parts']
        return anchor, parts


def read_spatial_params(body_part_json):
    """
    Reads from a JSON formatted file the body spatial parameters.

    Args:
        body_part_json (json): a JSON formatted file specifying a
                list of dicts, where each dict consists of a body anchor and
                parts, and displacement is the sum of displacements from
                each anchor to each part

    Returns:
        a list of dicts: each dict consists of an anchor and a list of
        parts, where the displacement from the anchor to each part would
        be compueted and summed
    """
    with open(body_part_json) as data_file:
        spatial_params_list = json.load(data_file)['spatial']
        return spatial_params_list


def compute_displacement(df1, df2):
    """
    Computes the Catesian displacement between corresponding data points
    (corresponding frames) between two data frames.

    Args:
        df1 (DataFrame): first data frame
        df2 (DataFrame): second data frame

    Returns:
        DataFrame: resulting data frame comprising frame-level displacements
    """
    return (abs(df2-df1) ** 2).sum(axis=1).apply(np.sqrt)


def compute_self_displacement(df):
    """
    Computes the Catesian displacement between subsequent data points
    (subsequent frames) within a single data frame.

    Args:
        df (DataFrame): data frame whose self-displacement is to be computed

    Returns:
        DataFrame: resulting data frame comprising frame-level displacements
    """
    temp_df = df.shift()
    temp_df.iloc[0] = temp_df.iloc[1]
    return compute_displacement(df, temp_df)


def compute_derivative(df, frame_rate):
    """
    Computes the derivative between subsequent data points (subsequent frames)
    within a single data frame.

    Args:
        df (DataFrame): data frame whose derivative is to be computed
        frame_rate (float): frame rate of the data frame

    Returns:
        DataFrame: resulting data frame comprising frame-level derivative
    """
    return df.diff().fillna(float(0)) / (float(1)/frame_rate)


def format_conversion(df, body_part):
    """
    Converts a data frame with general column names and additional quoting
    into a data frame with specific column names without quoting.

    Args:
        df (DataFrame): data frame prior to conversion
        body_part (string): the body part whoe data frame is converted

    Returns:
        DataFrame: data frame after conversion
    """
    stripped_df = df[body_part].apply(lambda x: re.sub('[\[\]]', '', x))
    split_df = pd.DataFrame(
        stripped_df.to_frame().ix[
            :, 0].str.split(', ').tolist(), columns=[
            'X', 'Y', 'Z'])
    converted_df = split_df.convert_objects(convert_numeric=True)
    converted_df.index += 1
    return converted_df


def compute_kinectic_energy(df_dict, body_part_weights_norm, frame_rate):
    """
    Computes the kinectic energy of the body on a per frame basis,
    using contribution from all body parts, where the weight of each
    body part represents the amount of contribution.

    Args:
        df_dict (dict): dict of data frames, indexed by body parts
        body_part_weights_norm (dict): dict of weights, indexed by body parts
        frame_rate (float): frame rate across all data frames

    Returns:
        DataFrame: resulting data frame comprising frame-level KE
    """
    KE = 0.5
    list_KE = []
    for bp in df_dict:
        this_bp_velocity = compute_derivative(
            compute_self_displacement(
                df_dict[bp]),
            frame_rate)
        list_KE.append(body_part_weights_norm[bp] * (this_bp_velocity ** 2))
    return 0.5 * sum(list_KE)


def compute_symmetry_indexes(df_dict, sym_anchor, sym_parts_lst):
    """
    Computes the symmetric index along X,Y and Z axis on a per frame basis.

    Args:
        df_dict (dict): dicts of data frames, indexed by body parts
        sym_anchor (string): the body part being the axis of the
            symmetry
        sym_parts_lst (list): list of body parts being symmetrical
            around the axis

    Returns:
        DataFrame: resulting data frame comprising frame-level symmetry index
            values along X,Y and Z axes
    """
    anchor_df = df_dict[sym_anchor]
    part_1_df = df_dict[sym_parts_lst[0]]
    part_2_df = df_dict[sym_parts_lst[1]]
    numerator = abs(abs(anchor_df - part_1_df) - abs(anchor_df - part_2_df))
    denominator = abs(part_1_df - part_2_df)
    return numerator / denominator


def compute_posture(df_dict):
    """
    Computes posture, or bounding volume, of the body on a per frame basis.

    Args:
        df_dict (dict): dict of data frames, indexed by body parts

    Returns:
        DataFrame: resulting data frame comprising frame-level bounding volume
            values
    """
    list_X = []
    list_Y = []
    list_Z = []
    for bpart in df_dict:
        list_X.append(df_dict[bpart]['X'].values)
        list_Y.append(df_dict[bpart]['Y'].values)
        list_Z.append(df_dict[bpart]['Z'].values)
    df_X = pd.DataFrame(list_X).transpose()
    df_Y = pd.DataFrame(list_Y).transpose()
    df_Z = pd.DataFrame(list_Z).transpose()
    df_X.index += 1
    df_Y.index += 1
    df_Z.index += 1
    return abs(df_X.max(axis=1)-df_X.min(axis=1)) * abs(df_Y.max(axis=1) -
               df_Y.min(axis=1)) * abs(df_Z.max(axis=1)-df_Z.min(axis=1))


def main():
    """
    Extracts high-level, expressive body language features from a time-series
    motion trace. Extraction is on a per frame basis. For each BVH file, this
    script generates frame-level feature values for (i) kinectic energy
    (ii) symmetry indexes (iii) posture (iv) spatial dispacement. Please refer
    to the README.md on how to specify parameters for generating these feature
    values.

    Returns:
        TYPE: Description
    """
    sync_files_list, sync_files_dir, body_parts_specification,\
        frame_rate, output_dir = readConfig('config.ini')

    body_part_weights = read_body_part_weights(body_parts_specification)

    # normalize body part weights
    body_part_weights_norm = {p: float(
        body_part_weights[p]) / sum(body_part_weights.values()) for p in body_part_weights}

    sym_anchor, sym_parts_lst = read_symmetry_params(body_parts_specification)

    spatial_params_list = read_spatial_params(body_parts_specification)

    bvh_file_lst = [filename.strip() for filename in open(sync_files_list)]

    for bvh_file in bvh_file_lst:

        df_dict = dict()
        res_df = []
        res_df_headers = [
            'kinetic_energy',
            'symmetry_X',
            'symmetry_Y',
            'symmetry_Z',
            'posture']

        df = pd.read_csv(join(output_dir, bvh_file+'.framelevelbvh.csv'))
        for bp in body_part_weights:
            df_dict[bp] = format_conversion(df, bp)

        ke_df = compute_kinectic_energy(
            df_dict,
            body_part_weights_norm,
            frame_rate)
        symmetry_df = compute_symmetry_indexes(
            df_dict,
            sym_anchor,
            sym_parts_lst)
        posture_df = compute_posture(df_dict)

        res_df.append(ke_df)
        res_df.append(symmetry_df)
        res_df.append(posture_df)

        for param in spatial_params_list:
            disp_df_list = []
            anchor = param['anchor']
            feature_name_list = [anchor]
            for part in param['parts']:
                feature_name_list.append(part)
                disp_df_list.append(
                    compute_displacement(
                        df_dict[anchor],
                        df_dict[part]))

            spatial_df = sum(disp_df_list)
            res_df.append(spatial_df)
            res_df_headers.append('_'.join(feature_name_list) + '_disp')

            spatial_first_derv_df = compute_derivative(spatial_df, frame_rate)
            res_df.append(spatial_first_derv_df)
            res_df_headers.append(
                '_'.join(feature_name_list) +
                '_disp_first_derv')

            spatial_second_derv_df = compute_derivative(
                spatial_first_derv_df,
                frame_rate)
            res_df.append(spatial_second_derv_df)
            res_df_headers.append(
                '_'.join(feature_name_list) +
                '_disp_second_derv')

        output_df = pd.concat(res_df, axis=1)
        output_df.columns = res_df_headers
        output_df.to_csv(
            join(
                output_dir,
                bvh_file +
                '.framelevelfeatures.csv'),
            quoting=csv.QUOTE_MINIMAL)


if __name__ == '__main__':
    main()
