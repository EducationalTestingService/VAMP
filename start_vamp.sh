#!/bin/bash

OFPATH=/Users/cleong/OpenFace
FAVEPATH=/Users/cleong/FAVE
BLUEMIXPATH=/Users/cleong/vamp/bluemix
WORKDIR=${PWD}

if [ ! -d outputs ]; then
	mkdir -p outputs;
fi;

file="inputs/sync_files.lst"
while IFS= read sync_file_id
do
	# first remove previously created directories
	# with the same sync_file_id, then create all
	# the necessary directories
	#if [ -d outputs/$sync_file_id ]; then
	#	rm -rf outputs/$sync_file_id
	#fi
	#mkdir -p outputs/$sync_file_id/bvh
	#mkdir -p outputs/$sync_file_id/speech
	#mkdir -p outputs/$sync_file_id/face
	#mkdir -p outputs/$sync_file_id/anvil

	#echo "Performing speech to text transcription using IBM's bluemix ......."
	# set up names
	#$BLUEMIXPATH/get_speech_transcription.py \
	#  sync_files_dir/$sync_file_id.wav \
	#  outputs/$sync_file_id/speech/transcription.txt \
	#  > outputs/$sync_file_id/speech/FAVE.input

	#echo "Done."

#	echo "Performing forced alignment betwwen wav and transcription ......."
#
#	cp outputs/$sync_file_id/speech/FAVE.input $FAVEPATH/FAVE-align/$sync_file_id.txt
#	cp sync_files_dir/$sync_file_id.wav $FAVEPATH/FAVE-align/$sync_file_id.temp.wav
#	cd $FAVEPATH/FAVE-align
#	ffmpeg -i $sync_file_id.temp.wav -acodec pcm_s16le -ac 1 -ar 11025 $sync_file_id.wav
#	./FAAValign.py $sync_file_id.wav $sync_file_id.txt
#	rm $sync_file_id.temp.wav
#	cd $WORKDIR
#	mv $FAVEPATH/FAVE-align/$sync_file_id* outputs/$sync_file_id/speech/
#
#	echo "Done."

#	echo "Performing pitch and intesity extraction for speech ......."
#	praat $WORKDIR/praat/prosody.praat $WORKDIR/outputs/$sync_file_id/speech/$sync_file_id
#	echo "Done."


#	echo "Performing video features extraction  ......."
#	cd sync_files_dir/
#
#	ffmpeg -i ${sync_file_id}_face.avi -c:v libx264 -r 30 ${sync_file_id}_face.mov
#	$OFPATH/bin/FeatureExtraction -root $WORKDIR/sync_files_dir/ -f ${sync_file_id}_face.mov -ov ${sync_file_id}.tracked.mov -of ${sync_file_id}.features
#	mv ${sync_file_id}.tracked.mov ${sync_file_id}.features $WORKDIR/outputs/${sync_file_id}/face
#	cd ..
#	echo "Done."

#	echo "Performing skeletal features extraction  ......."
#	cd bvh
#	./bvh_parser.py
#	./compute_kinect_features.py
#	cd ..
#	echo "Done."
#
#	echo "$sync_file_id"
done <"$file"