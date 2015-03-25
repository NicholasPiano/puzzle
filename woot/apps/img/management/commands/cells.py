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
from scipy.ndimage.measurements import center_of_mass as cm

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # for each series, gather masks from mask directory
    for series in Series.objects.all():

      for t in range(series.ts):

        # gfp gon
        gfp_gon = series.composite.gons.get(channel__name='0', t=t)
        gfp = gfp_gon.load()

        # region gon
        region_gon = series.composite.gons.get(channel__name='region', t=t)
        regions = region_gon.load()

        # markers
        markers = series.cell_markers.filter(t=t)

        for marker in markers:

          mask_set = []

          for mask in series.gons.exclude(id_token='').filter(t=marker.t):

            inside = marker.r > mask.r and marker.r < mask.r+mask.rs and marker.c > mask.c and marker.c < mask.c+mask.cs
            if inside:
              mask_set.append(mask)

          true_mask_set = []

          for mask in mask_set:
            m = mask.load()
            if m[marker.r-mask.r, marker.c-mask.c]:

              # area
              area = m[m>0].sum()

              # gfp mean
              gfp_cut = gfp[mask.r:mask.r+mask.rs, mask.c:mask.c+mask.cs, mask.z]
              masked_gfp = np.ma.array(gfp_cut, mask=m)
              gfp_mean = masked_gfp.mean()

              # center r,c
              r, c = cm(m>0)

              # region
              region = regions[r,c,mask.z]

              true_mask_set.append((mask, area, gfp_mean, r, c, region))

          # start from list of masks
          # want to know: z, r, c, A, R, t, track_id
