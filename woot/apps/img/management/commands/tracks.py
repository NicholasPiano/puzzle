#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Experiment, Series
from apps.img import settings as img_settings

#util
import os
import re
import numpy as np
from scipy.misc import imsave

### Command
class Command(BaseCommand):
  args = ''
  help = ''

  def handle(self, *args, **options):
    # 1. look in each experiments track directories, determine new files
    for series in Series.objects.all():
      # open files in track directory and read lines
      file_list = [file_name for file_name in os.listdir(series.experiment.track_path) if '.csv' in file_name]

      for file_name in file_list:
        # get template
        template = series.experiment.match_template(file_name)

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
              track_index = series.cell_tracks.filter(track_id=track_id).count()
              track = series.cell_tracks.create(experiment=series.experiment, track_id=track_id, index=track_index)

              for marker in markers:
                track.markers.create(experiment=series.experiment, series=series, r=marker[0], c=marker[1], t=marker[2])
