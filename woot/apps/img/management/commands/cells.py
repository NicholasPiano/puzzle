#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Series
from apps.img.settings import *
from apps.cell.models import Mask, CellMarker
from apps.pix.models import Gon

#util
import os
import re
import numpy as np

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # for each series, gather masks from mask directory
    for series in Series.objects.all():
      for track in series.cell_tracks.all():
        for marker in track.markers.all():

          mask_set = []

          for mask in series.gons.exclude(id_token='').filter(t=marker.t):

            inside = marker.r > mask.r and marker.r < mask.r+mask.rs and marker.c > mask.c and marker.c < mask.c+mask.cs
            if inside:
              mask_set.append(mask)

          true_mask_set = []

          for mask in mask_set:
            m = mask.load()
            if m[marker.r-mask.r, marker.c-mask.c]:
              true_mask_set.append(mask)

          print(len(true_mask_set))
