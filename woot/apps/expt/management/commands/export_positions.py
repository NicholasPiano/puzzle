#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.expt.models import Series
from apps.cell.models import Marker

#util
import os
import re
import numpy as np
from scipy.misc import imsave
import matplotlib.pyplot as plt
from skimage import exposure
from scipy.ndimage.morphology import binary_dilation as dilate

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    for series in Series.objects.all():
      # data output folder
      output_path = os.path.join(series.experiment.data_path, '{}_s{}.csv'.format(series.experiment.name, series.name))

      with open(output_path, 'w+') as output:

        output.write('cell, t, row, column, v_row, v_column, region\n')

        all_m = max([marker.pk for marker in Marker.objects.filter(track__channel__name='0')])

        # loop through tracks to calculate velocity on the fly
        for track in series.tracks.filter(channel__name='0'):
          previous_marker = None

          for marker in track.markers.order_by('t'):
            print(marker.pk, all_m)

            # velocity
            vr = 0 if previous_marker is None else marker.r - previous_marker.r
            vc = 0 if previous_marker is None else marker.c - previous_marker.c

            previous_marker = marker

            # region
            region_gon = series.composites.get().channels.get(name='regions').gons.get(t=marker.t)
            regions = region_gon.load()

            region_matches = [1]
            for region_mask in region_gon.masks.all():

              # load image
              mask = dilate(region_gon.array == np.unique(region_gon.array)[region_mask.mask_id], iterations=6)

              if mask[marker.r, marker.c]:
                region_matches.append(series.vertical_sort_for_region_index(region_mask.mask_id))

            # line
            line = '{},{},{},{},{},{},{}\n'.format(track.track_id, marker.t, marker.r, marker.c, vr, vc, max(region_matches))
            output.write(line)
