# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local
from apps.expt.models import Experiment, Series

# util
import os
import re
import numpy as np
from scipy.misc import imsave
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure

### Command
class Command(BaseCommand):
  args = ''
  help = ''

  def handle(self, *args, **options):
    # 1. look in each experiments track directories, determine new files
    for series in Series.objects.all():
      print('processing markers for series %s...' % str(series))

      # open files in track directory and read lines
      file_list = [file_name for file_name in os.listdir(series.experiment.track_path) if '.csv' in file_name]

      for file_name in file_list:
        # get template
        template = series.experiment.templates.get(name='track')

        # check series name and load
        dict = template.dict(file_name)
        if dict['series']==series.name:
          with open(os.path.join(series.experiment.track_path, file_name)) as track_file:

            tracks = {} # stores list of tracks that can then be put into the database

            for line in track_file.readlines():
              line = line.rstrip().split('\t')

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
              track = series.tracks.create(experiment=series.experiment, track_id=track_id, index=track_index)

              for marker in markers:
                track.markers.create(experiment=series.experiment, series=series, r=marker[0], c=marker[1], t=marker[2])

      for t in range(series.ts):
        print('processing marker z positions... t%d' % t)
        # markers
        markers = series.markers.filter(t=t)

        # load gfp
        gfp_gon = series.gons.filter(t=t, channel__name='0')[0]
        gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)

        # smooth gfp
        gfp_smooth = gf(gfp, sigma=5)

        # for each marker, search in the immediate area
        for marker in markers:

          max_values = []

          for size in range(5,10): # increase mask size
            r0 = marker.r - size if marker.r - size >= 0 else 0
            r1 = marker.r + size if marker.r + size <= gfp_gon.rs else gfp_gon.rs
            c0 = marker.c - size if marker.c - size >= 0 else 0
            c1 = marker.c + size if marker.c + size <= gfp_gon.cs else gfp_gon.cs

            column = gfp_smooth[r0:r1,c0:c1,:]

            column_1D = np.sum(np.sum(column, axis=0), axis=0)

            max_values.append(np.argmax(column_1D))

          marker.z = int(np.mean(max_values))
          marker.save()
