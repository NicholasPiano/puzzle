# expt.command: step07_tracks

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Experiment
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
      default='050714-test', # some default
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

    # 1. get experiment
    expt = Experiment.objects.get(name=options['expt'])
    series = expt.series.get(name=options['series'])

    # 2. list files in track directory
    file_list = [file_name for file_name in os.listdir(expt.track_path) if '.xls' in file_name]

    for file_name in file_list:
      # get template
      template = expt.templates.get(name='track')

      # check series name and load
      dict = template.dict(file_name)
      if dict['series']==series.name:
        with open(os.path.join(expt.track_path, file_name), 'rb') as track_file:

          tracks = {} # stores list of tracks that can then be put into the database

          lines = track_file.read().decode('mac-roman').split('\n')[1:-1]
          for i, line in enumerate(lines): # omit title line and final blank line
            print('step07 | reading tracks and markers from {} for {}.{}: ({}/{})'.format(file_name, expt.name, series.name, i+1, len(lines)), end='\n' if i==len(lines)-1 else '\r')
            line = line.split('\t')

            # details
            track_id = int(line[1])
            r = int(line[4])
            c = int(line[3])
            t = int(line[2]) - 1

            if track_id in tracks:
              tracks[track_id].append((r,c,t))
            else:
              tracks[track_id] = [(r,c,t)]

          for track_id, markers in tracks.items():
            track_index = series.tracks.filter(track_id=track_id).count()
            track, track_created = series.tracks.get_or_create(experiment=expt, series=series, track_id=track_id, index=track_index)

            if track_created:
              for marker in markers:
                track.markers.create(experiment=series.experiment, series=series, r=marker[0], c=marker[1], t=marker[2])

    # 3. load gfp, smooth and cut for each marker
    composite = series.composites.get()
    print('step07 | loading gfp...')

    for t in range(series.ts):

      # markers
      markers = series.markers.filter(t=t)
      number_of_markers = markers.count()

      # load gfp
      gfp_gon = composite.gons.get(t=t, channel__name='0')
      gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)

      # smooth gfp
      gfp_smooth = gf(gfp, sigma=5)

      # for each marker, search in the immediate area
      for marker in markers:

        max_values = []

        for size in range(7,10): # increase mask size
          r0 = marker.r - size if marker.r - size >= 0 else 0
          r1 = marker.r + size if marker.r + size <= gfp_gon.rs else gfp_gon.rs
          c0 = marker.c - size if marker.c - size >= 0 else 0
          c1 = marker.c + size if marker.c + size <= gfp_gon.cs else gfp_gon.cs

          column = gfp_smooth[r0:r1,c0:c1,:]
          column_1D = np.sum(np.sum(column, axis=0), axis=0)

          max_values.append(np.argmax(column_1D))

        marker.z = int(np.mean(max_values))
        marker.save()

      print('step07 | scanning z for each marker at t={}...'.format(t), end='\n' if t==series.ts-1 else '\r')
