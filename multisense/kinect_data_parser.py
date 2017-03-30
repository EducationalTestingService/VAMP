#!/usr/bin/env python
# License: MIT
"""
Recursively parse a time-series motion trace file specified in Biovision
Hierarchical (BVH) format and extracts the time-series, Cartesian coordinated
data for a set of specified body parts.

:author: Ben Leong (cleong@ets.org)

"""


import ConfigParser
import os
import re
import sys
import json
import csv
from os.path import join
# sys.path.append('BVHplay/')

#from skeleton import skeleton, process_bvhfile
import pandas as pd


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
          coordinates needs to be extracted
          (iv) the output directory where the extracted time-series,
          Cartesian coordinate are stored


  Returns:
      a sequence of strings : parsed inputs from config file
  """
  parser = ConfigParser.SafeConfigParser()
  parser.read(configFilename)

  sync_files_list = parser.get("inputs", "sync_files_list")
  sync_files_dir = parser.get("inputs", "sync_files_dir")
  body_parts_specification = parser.get("inputs",
                                        "body_parts_specification")
  output_dir = parser.get("outputs", "output_dir")

  return sync_files_list, sync_files_dir,\
      body_parts_specification, output_dir


def read_body_parts(body_part_json):
  """
  Reads from a JSON formatted file the set of body parts whose
  Catesian coordinates are to be extracted.

  Args:
      body_part_json (json): a JSON formatted file specifying body parts

  Returns:
      list: list of body parts
  """
  with open(body_part_json) as data_file:
    body_part_list = json.load(data_file)['body_parts']
    return body_part_list


def getFrameLevelDisplacements(body_part_lst, filename_path):
  displacements = []
  with open(filename_path, 'r') as f:
    for line in f:
      parts = line.strip().split()
      temp = []
      for part in parts:
        subparts = re.split('=\[|\]\(|,|\)', part)
        subparts = filter(None, subparts)  # filter subparts
        subpart = subparts[0]

        if subpart in body_part_lst:
          X = float(subparts[1])
          Y = float(subparts[2])
          Z = float(subparts[3])
          temp.append([X, Y, Z])

      displacements.append(temp)

  return displacements


def main():
  """
  Iterates through each BVH file, and for each file, extracts
  the time-series, 3D coordinate data for a set of specified
  body parts on a per frame basis. It then stores the extracted
  data into an output directory specified by the user for further
  processing.
  """
  sync_files_list, sync_files_dir, body_parts_specification,\
      output_dir = readConfig('config.ini')
  multisense_file_lst = [filename.strip()
                         for filename in open(sync_files_list)]
  body_parts_lst = read_body_parts(body_parts_specification)
  header = body_parts_lst
  #header = [bp for bp in body_parts_lst]

  for multisense_file in multisense_file_lst:
    if not os.path.exists(join(output_dir, multisense_file, 'motiontrace')):
      os.makedirs(join(output_dir, multisense_file, 'motiontrace'))
    list_bparts = []
    filename_path = join(sync_files_dir, multisense_file + '.txt')

    this_bvh_df = pd.DataFrame(
        getFrameLevelDisplacements(
            body_parts_lst, filename_path))
    this_bvh_df.index += 1
    this_bvh_df.columns = header
    #'''
    this_bvh_df.to_csv(
        join(
            output_dir,
            multisense_file,
            'motiontrace',
            multisense_file +
            '.framelevelmotiontrace.csv'),
        quoting=csv.QUOTE_MINIMAL)


if __name__ == "__main__":
  main()
