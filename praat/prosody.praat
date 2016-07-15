# prosody.praat
#
# 11/2013
#
# use the new Praat script style to extract both pitch & intensity
form input a wav
     word Path
     word Wav_id
endform

# wav load
sound = do ("Read from file...", path$ + wav_id$ + ".wav")

# pitch
selectObject (sound)
do ("To Pitch...", 0, 75, 600)
do ("Down to PitchTier")
do ("Save as short text file...", path$ + wav_id$ + ".PitchTier")

# intensity
selectObject (sound)
do ("To Intensity...", 100, 0, "yes")
do ("Down to IntensityTier")
do ("Save as short text file...", path$ + wav_id$ + ".IntensityTier")