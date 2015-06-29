# expt.command: step07_tracks

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series
from apps.expt.util import *

# util
import os
from optparse import make_option
from skimage import exposure
from scipy.ndimage.filters import gaussian_filter as gf
import numpy as np

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714', # some default
      help='Name of the experiment to import' # who cares
    ),

    make_option('--series', # option that will appear in cmd
      action='store', # no idea
      dest='series', # refer to this in options variable
      default='13', # some default
      help='Name of the series' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    '''
    1. What does this script do?
    > Takes in an arbitrary number of track files from Fiji/ImageJ and converts them into tracks/markers

    2. What data structures are input?
    > None

    3. What data structures are output?
    > Track, Marker

    4. Is this stage repeated/one-time?
    > Repeated

    Steps:

    1. Scan track directory for new files
    2. Apply track template to the file names and match them with the specified experiment and series
    3. Open each file in turn and extract tracks (id's) and markers (lines)
    4. Tracks are uniquely identified by an id_token

    '''

    # 1. get series
    series = experiment.series.get(experiment__name=options['expt'], name=options['series'])

    # 2. list files in track directory
    file_list = [file_name for file_name in os.listdir(experiment.track_path) if '.csv' in file_name]

    for file_name in file_list:
      # get template
      template = experiment.templates.get(name='track')

      # check series name and load
      dict = template.dict(file_name)
      if dict['series']==series.name:
        with open(os.path.join(experiment.track_path, file_name), 'rb') as track_file:

          tracks = {} # stores list of tracks that can then be put into the database

          ### CHANGE METHOD ### ### ### ###

          lines = track_file.read().decode('mac-roman').split('\n')[1:-1]
          for i, line in enumerate(lines): # omit title line and final blank line
            print('step03 | reading tracks and markers from {} for {}.{}: ({}/{})'.format(file_name, experiment.name, series.name, i+1, len(lines)), end='\n' if i==len(lines)-1 else '\r')
            line = line.split('\t')

            # details
            track_id = int(float(line[1]))
            r = int(float(line[4]))
            c = int(float(line[3]))
            t = int(float(line[2])) - 1

            if track_id in tracks:
              tracks[track_id].append((r,c,t))
            else:
              tracks[track_id] = [(r,c,t)]

          ### CHANGE METHOD ### ### ### ###

          for track_id, markers in tracks.items():
            track_index = series.tracks.filter(track_id=track_id).count()
            track, track_created = series.tracks.get_or_create(experiment=experiment, series=series, track_id=track_id, index=track_index)

            if track_created:
              for marker in markers:
                track.markers.create(experiment=series.experiment, series=series, r=marker[0], c=marker[1], t=marker[2])

    # 3. determine z of each marker using zmod images
    
