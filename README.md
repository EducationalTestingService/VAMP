# VAMP

Visualization and Analysis for Multimodal Presentation (VAMP)

VAMP is a set of scripts designed to extract high-level, expressive body language features from synchronized video, audio and skeletal data streams recorded from multimodal presentations. Release of VAMP is incremental at this point, with the current focus on facilitating the extraction of frame-level, body language features from skeletal data files. VAMP is tested to run successfully on OS X 64-bit architecture, but would be expanded to support other platforms in the future.


Reference
---------
Full details of the VAMP framework is described in our [MLA'15 paper](http://benleong.net/downloads/icmi-mla-2015-leong.pdf):

Utilizing Depth Sensors for Analyzing Multimodal Presentations: Hardware, Software and Toolkits,
Chee Wee Leong, Lei Chen, Gary Feng, Chong Min Lee and Matthew MulHolland,
in Proceedings of the 4th Multimodal Learning Analytics Workshop and Grand Challenges (MLA), Seattle, 2015

A talk about VAMP will be given at [PyGotham 2016](https://2016.pygotham.org/)

Biovision Hierarchical (BVH) Format
---------
The Biovision Hierarchy (BVH) character animation file format was developed by Biovision. BVH provides skeleton hierarchy information as well as motion data. The BVH format is an ASCII file that is used to import rotational joint data. It is currently one of the most popular motion data formats, and has been widely adopted by the animation community.

VAMP requires the Python package [BVHPlay](https://sites.google.com/a/cgspeed.com/cgspeed/bvhplay), which is a free, open-source BVH animation player for reading a BVH file and its playback. BVHPlay plays any BVH file that conforms to the basic BVH file format. It has a resizable window, four degrees-of-freedom controlling the angle of view, and provides the standard transport control buttons such as play, stop, step, forward, step back, step forward, go to start and go to end.

![BVHPlay screen dump](https://sites.google.com/a/cgspeed.com/cgspeed/bvhplay/screenshot1.jpg)

Installation
---------
VAMP also requires the [cgkit](http://cgkit.sourceforge.net/) Python package and [Pandas](http://pandas.pydata.org/) data analysis libraries. Setting up the environment is easiest through [Conda](http://conda.pydata.org/docs/) package management system. Due to limitation of BVHPlay, only Python 2.7 is supported in VAMP for the extraction of frame-level features.

If you do not have conda install, follow the instructions [here](http://docs.continuum.io/anaconda/install) to install it.

After doing a `git clone` of VAMP, type the following to install the vamp conda environment,

```
conda create --name vamp --file conda/vamp_conda_osx64.txt
conda install -n vamp -c https://conda.anaconda.org/cleong cgkit
```

Configuration
---------
VAMP can be configured to extract expressive features from arbitrary body parts, as long as these body parts are captured in BVH. The configuration is found in `inputs/body_parts.json`. For example, the `body_parts` field indicates which parts of the body in BVH would be targeted for expressive features extraction:

```javascript
"body_parts": ["Hips","Spine","LeftShoulder","RightShoulder",
    			"LeftArm","RightArm","LeftForeArm","RightForeArm",
    			"LeftHand","RightHand"]
```

For specifying the weights of each body part in contribution to the overall kinetic energy, use:

```javascript
	"weights": {"Hips": 14.81, "Spine" : 12.65, "LeftShoulder" : 0.76875,
				"RightShoulder" : 0.76875, "LeftArm" : 1.5375,
				"RightArm" : 1.5375, "LeftForeArm" : 0.86,
				"RightForeArm" : 0.86, "LeftHand" : 0.2875,
				"RightHand" : 0.2875 },
```

For symmetry indexes, the `anchor` serves as the axis of symmetry between two corresponding `parts` contained in a list:

```javascript
	"symmetry": {"anchor": "Hips", "parts": ["LeftHand", "RightHand"]},
```

Note that, for spatial displacements and their first-order (temporal) and second-order (power) derivations, the displacement is measured from the `anchor` to each member of the `parts` list:

```javascript
	"spatial": [{"anchor": "Spine", "parts": ["LeftHand", "RightHand"]},
				{"anchor": "Spine", "parts": ["LeftArm", "RightArm"]},
				{"anchor": "LeftHand", "parts": ["RightHand"]}]
```

You need to also specify a list of prefixes of the BVH files you wish to process in `inputs/sync_files.lst`, and copy the actual BVH files to the `sync_files_dir`. In this case, the prefix is `sample` for the actual BVH file `sample.bvh`


Running VAMP
---------
Extraction of the body language features are performed in two steps. First, a recursive parsing of the BVH file is done to extract frame-level motion traces. Second, feature implementations are used to transform the motion traces into higher-level body language features.

To initiate the `vamp` conda environment, type:

```
source activate vamp
```

Next, run the following to perform recursive parsing of the BVH file:

```
./bvh_parser.py
```

Finally, execute the following to store all features into the `output` directory:

```
./compute_kinect_features.py
```

After running the two steps, you should be able to see the following in the `outputs` directory:

```
sample.framelevelbvh.csv
sample.framelevelfeatures.csv
```

The `.framelevelfeatures.csv` file contains frame-level body language expressive features that can be used further for building models for multimodal presentation assessments.



