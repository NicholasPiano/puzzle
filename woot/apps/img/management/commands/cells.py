#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Series
from apps.img.settings import *
from apps.cell.models import Mask, CellMarker
from apps.pix.models import Gon, Composite

#util
import os
import re
import numpy as np
from scipy.ndimage.measurements import center_of_mass as cm
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # for each series, gather masks from mask directory
    for composite in Composite.objects.all():

      for t in range(composite.series.ts):
        print(t)

        # gfp gon
        gfp_gon = composite.gons.get(channel__name='0', t=t)
        gfp = gfp_gon.load()

        smoothed_gfp = gf(exposure.rescale_intensity(gfp * 1.0), sigma=5)

        # region gon
        region_gon = composite.gons.get(channel__name='region', t=t)
        regions = region_gon.load()

        # markers
        markers = composite.series.cell_markers.filter(t=t)

        for marker in markers:

          mask_set = []

          for mask in composite.series.gons.exclude(id_token='').filter(t=marker.t):

            inside = marker.r > mask.r and marker.r < mask.r+mask.rs and marker.c > mask.c and marker.c < mask.c+mask.cs
            if inside:
              mask_set.append(mask)

          true_mask_set = []

          for mask in mask_set:
            m = mask.load()
            if m[marker.r-mask.r, marker.c-mask.c]:

              # area
              area = m[m>0].sum()/255.0

              gfp_list = []
              s_gfp_list = []
              for z in range(composite.series.zs):
                # gfp mean
                gfp_cut = gfp[mask.r:mask.r+mask.rs, mask.c:mask.c+mask.cs, z]
                masked_gfp = np.ma.array(gfp_cut, mask=m)
                gfp_mean = masked_gfp.mean()
                gfp_list.append(gfp_mean)

                # smooth gfp mean
                s_gfp_cut = smoothed_gfp[mask.r:mask.r+mask.rs, mask.c:mask.c+mask.cs, z]
                s_masked_gfp = np.ma.array(s_gfp_cut, mask=m)
                s_gfp_mean = s_masked_gfp.mean()
                s_gfp_list.append(s_gfp_mean)

              # center r,c
              r, c = cm(m>0)
              r += mask.r
              c += mask.c

              # region
              region = 5 - regions[r,c,mask.z]

              true_mask_set.append((mask.pk, marker.track.track_id, marker.t, area, gfp_list, s_gfp_list, r, c, mask.z, region))

          # make cell
          cell, cell_created = composite.experiment.cells.get_or_create(series=composite.series, cell_id=marker.track.track_id)

          # make cell instance
          cell_instance, cell_instance_created = cell.cell_instances.get_or_create(experiment=composite.experiment, series=composite.series, t=marker.t)

          avg_z = [np.argmax(true[5]) for true in true_mask_set]
          z = int(np.mean(avg_z))
          print(z)

          ci_max = min(true_mask_set, key=lambda x: abs(x[8]-z))
          cell_instance.a = int(ci_max[3])
          cell_instance.r = int(ci_max[6])
          cell_instance.c = int(ci_max[7])
          cell_instance.z = int(ci_max[8])
          cell_instance.region = int(ci_max[9])

          cell_instance.save()

          # for true in true_mask_set:
          #   plt.plot(true[5])
          #
          # plt.show()

          # g = [true[4] for true in sorted(true_mask_set, key=lambda x: x[7])]
          # s = [true[5] for true in sorted(true_mask_set, key=lambda x: x[7])]
          # a = [true[3] for true in sorted(true_mask_set, key=lambda x: x[7])]
          #
          # g = np.array(g) / max(g)
          # s = np.array(s) / max(s)
          # a = np.array(a) / max(a)
          #
          # plt.plot(g)
          # plt.plot(s)
          # plt.plot(a)
          # plt.show()

          # start from list of masks
          # want to know: z, r, c, A, R, t, track_id
