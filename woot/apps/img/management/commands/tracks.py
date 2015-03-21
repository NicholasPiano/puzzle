#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Experiment, Series
from apps.img import settings as img_settings

#util
import os
import re
from optparse import make_option
import codecs
import numpy as np
from scipy.misc import imsave

### Command
class Command(BaseCommand):
  args = ''
  help = ''

  def handle(self, *args, **options):
    track_file_template = r'(?P<experiment>.+)_s(?P<series>.+)_i(?P<index>.+)\.xls'

    # 1. look in each experiments track directories, determine new files
    for experiment in Experiment.objects.all():
      track_path = os.path.join(experiment.base_path, experiment.track_path)

      file = os.listdir(track_path)[1]

      # 2. open each new file, add lines to cell markers
      instances = []

      with open(os.path.join(track_path, file)) as f:

        line_template = r'(?P<n>.+),(?P<cell>.+),(?P<frame>.+),(?P<column>.+),(?P<row>.+),(?P<m>.+),(?P<l>.+),(?P<p>.+)'
        for line in f.readlines():
          m = re.match(line_template, line)
          instances.append({'id':int(m.group('cell')), 'frame':int(m.group('frame'))-1, 'row':int(m.group('row')), 'column':int(m.group('column'))})

      output_path = os.path.join(experiment.base_path, experiment.output_path)

      for frame in range(89):

        black = np.zeros((512, 512))

        for instance in filter(lambda x: x['frame']==frame, instances):

          # make white spot on black
          xx, yy = np.mgrid[:black.shape[0], :black.shape[1]]
          circle = (xx - instance['row']) ** 2 + (yy - instance['column']) ** 2 # distance from c
          black[circle<10] = 255 # radius of 10 px

        imsave(os.path.join(output_path, 'primary_f%s.tiff' % (str('0'*(len(str(89))-len(str(frame)))) + str(frame))), black)
