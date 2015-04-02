#django
from django.core.management.base import BaseCommand, CommandError

#local
from apps.img.models import Composite

#util
from scipy.signal import find_peaks_cwt as pks
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
import numpy as np
import matplotlib.pyplot as plt
import os

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    out = '/Volumes/TRANSPORT/data/puzzle/050714-test/plot'

    # get gfp gon
    composite = Composite.objects.get()
    gfp_gon = composite.gons.get(channel__name='0', t=0)

    # load into array
    gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)

    # smooth
    gfp_smooth = gf(gfp, sigma=5)

    # find maxima
    gfp_thresh = gfp_smooth.copy()
    gfp_thresh[gfp_thresh<gfp_thresh.mean()] = 0.0
    # gfp_thresh[gfp_thresh!=0] = 1.0

    peaks = []

    for i in range(32):
      for j in range(32):
        # coords
        r0, r1, c0, c1 = 16*i, 16*i + 16, 16*j, 16*j + 16

        # column
        column = gfp_thresh[r0:r1,c0:c1,:]

        # simplify to 1D
        column_2D = np.sum(column, axis=0)
        column_1D = np.sum(column_2D, axis=0)

        # find peaks
        p = pks(column_1D, np.arange(20,30))

        if len(p)>1:
          print([i*16,j*16,p])
          column_z = np.sum(column, axis=2)

          plt.imshow(column_z)
          plt.show()

        peaks.extend(p)

    peaks = list(np.unique(peaks))
