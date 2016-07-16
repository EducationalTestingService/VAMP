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
import sys
import json
import csv
from os.path import join
sys.path.append('BVHplay/')

from skeleton import skeleton, process_bvhfile
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


def findTargetNode(root, nodeName, l):
  """
  Recursive parsing of the BVH skeletal tree using breath-first
  search to locate the node that has the name of the targeted body part.

  Args:
      root (object): root node of the BVH skeletal tree
      nodeName (string): name of the targeted body part
      l (list): empty list

  Returns:
      list: list containing the node representing the targeted body part
  """
  if root.name == nodeName:
    l.append(root)
  else:
    for child in root.children:
      findTargetNode(child, nodeName, l)
  return l


def getFrameLevelDisplacements(nodeFound, start, finish):
  """
  Iterates through the entire time-series data for a given
  body part to extract the X,Y,Z coordinate data.

  Args:
      nodeFound (object): joint object for the targeted body part
      start (int): starting frame number
      finish (int): ending frame number

  Returns:
      list: list of lists of X,Y,Z coordiantes. The number of lists must
      equal to number of frames in the BVH
  """
  displacements = []
  for i in range(start, finish):
    X = nodeFound.trtr[i][0][3]
    Y = nodeFound.trtr[i][1][3]
    Z = nodeFound.trtr[i][2][3]
    displacements.append([X, Y, Z])

  return displacements


def getBVHFeatures(body_part, filename_path):
  """
  Extracts X,Y,Z coordinate data per frame for a given body part
  from a time-series BVH file. BVH file must be recursively parsed
  prior to the extraction to locate the relevant node to begin processing.

  Args:
      body_part (string): body part whose Cartesian coordinate is
      to be extracted filename_path (string): path of BVH file

  Returns:
      list: list of lists of X,Y,Z coordiantes. The number of lists
      must equal to number of frames in the BVH
  """
  myskeleton = process_bvhfile(filename_path, DEBUG=0)
  frameTime = myskeleton.dt

  for t in range(1, myskeleton.frames + 1):
    myskeleton.create_edges_onet(t)

  nodeFound = findTargetNode(myskeleton.hips, body_part, [])[0]
  XYZ_displacement = getFrameLevelDisplacements(
      nodeFound,
      1,
      myskeleton.frames +
      1)
  return XYZ_displacement


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
  bvh_file_lst = [filename.strip() for filename in open(sync_files_list)]
  body_parts = read_body_parts(body_parts_specification)
  header = [bp for bp in body_parts]

  for bvh_file in bvh_file_lst:
    if not os.path.exists(join(output_dir, bvh_file, 'bvh')):
      os.makedirs(join(output_dir, bvh_file, 'bvh'))
    list_bparts = []
    for body_part in body_parts:
      list_bparts.append(
          getBVHFeatures(
              body_part,
              join(
                  sync_files_dir,
                  bvh_file +
                  '.bvh')))
    this_bvh_df = pd.DataFrame(list_bparts).transpose()
    this_bvh_df.index += 1
    this_bvh_df.columns = header

    this_bvh_df.to_csv(
        join(
            output_dir,
            bvh_file,
            'bvh',
            bvh_file +
            '.framelevelbvh.csv'),
        quoting=csv.QUOTE_MINIMAL)


if __name__ == "__main__":
  main()
