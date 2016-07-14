#!/usr/bin/env python

import requests
import json
import sys
import os

from os.path import join, abspath

WORK_DIR = os.path.dirname(os.path.realpath(__file__))
ARGS = sys.argv
WAV_FILE = abspath(ARGS[1])
TRANSCRIPTION_OUTPUT_FILE = abspath(ARGS[2])

API_ENDPOINT = 'https://stream.watsonplatform.net/speech-to-text/api/v1/recognize'

API_DEFAULT_PARAMS = {
    'continuous': True,
    'timestamps': True,
    'word_confidence': True,
    'profanity_filter': False,
}

API_DEFAULT_HEADERS = {
    'content-type': 'audio/wav'
}


WATSON_CREDS_FILENAME = "credsfile_watson.json"


def get_watson_creds(fname='credsfile_watson.json'):
  with open(join(WORK_DIR, fname), 'r') as f:
    data=json.load(f)
    return data['credentials']


def speech_to_text_api_call(audio_filename, username, password):
  with open(audio_filename, 'rb') as a_file:
    http_response=requests.post(API_ENDPOINT,
                                  auth=(username, password),
                                  data=a_file,
                                  params=API_DEFAULT_PARAMS,
                                  headers=API_DEFAULT_HEADERS,
                                  stream=False)
    return http_response


def process_transcript_call(audio_filename, transcript_path, creds):
  resp=speech_to_text_api_call(
      audio_filename,
      username=creds['username'],
      password=creds['password'])
  with open(transcript_path, 'w') as t:
    t.write(resp.text)

  return json.loads(resp.text)


def extract_transcription(data):
  transcription=''
  speaker_id='001'
  speaker_name='vamp'
  for result in data['results']:
    if result.get('alternatives'):
      # just pick best alternative
      alt=result.get('alternatives')[0]
      timestamps=alt['timestamps']
      if timestamps:  # for some reason, timestamps can be empty in some cases
        for idx, tobject in enumerate(alt['timestamps']):
          txt, tstart, tend=tobject
          transcription += '\t'.join((speaker_id,
                                      speaker_name,
                                      str(tstart),
                                      str(tend),
                                      txt)) + '\n'

  return transcription


def main():
  creds=get_watson_creds()
  transcription_output=process_transcript_call(
      WAV_FILE,
      TRANSCRIPTION_OUTPUT_FILE,
      creds)
  print extract_transcription(transcription_output).rstrip()


if __name__ == '__main__':
  main()
