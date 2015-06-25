# expt.command: step11_reduced

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series

# util
import os
import numpy as np
from optparse import make_option
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
from skimage import filter as ft
from scipy.misc import imsave, imread
from scipy.optimize import curve_fit

def slice(img, rs, cs, r, c, size=0):
  r0 = r - size if r - size >= 0 else 0
  r1 = r + size + 1 if r + size + 1 <= rs else rs
  c0 = c - size if c - size >= 0 else 0
  c1 = c + size + 1 if c + size + 1 <= cs else cs

  return img[r0:r1,c0:c1]

def scan_point(img, rs, cs, r, c, size=0):
  r0 = r - size if r - size >= 0 else 0
  r1 = r + size + 1 if r + size + 1 <= rs else rs
  c0 = c - size if c - size >= 0 else 0
  c1 = c + size + 1 if c + size + 1 <= cs else cs

  column = img[r0:r1,c0:c1,:]
  column_1D = np.sum(np.sum(column, axis=0), axis=0)

  return column_1D

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
    > Use masks to build up larger masks surrounding markers

    2. What data structures are input?
    > Mask, Gon

    3. What data structures are output?
    > Channel, Gon, Mask

    4. Is this stage repeated/one-time?
    > Repeated

    Steps:

    1. load mask gons
    2. stack vertically in single array

    '''

    # vars
    output_dir = '/Volumes/Extra/test'
    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])
    composite = series.composites.get()

    for t in range(1):
      markers = series.markers.filter(t=t)

      # load gfp
      gfp_gon = composite.gons.get(t=t, channel__name='0')
      gfp = gfp_gon.load()
      gfp = exposure.rescale_intensity(gfp * 1.0)
      gfp = gf(gfp, sigma=2)

      Z = exposure.rescale_intensity(imread(os.path.join(output_dir, 'profile_z_t0.tiff')) * 1.0)
      mean = exposure.rescale_intensity(imread(os.path.join(output_dir, 'profile_mean_t0.tiff')) * 1.0)

      def f(x, a, b):
        return a*x**2 + b

      sizes = range(0,20)

      for marker in markers.filter(pk__in=[919,1008]):
        total_intensity = []
        for size in sizes:
          column = scan_point(gfp, series.rs, series.cs, marker.r, marker.c, size=size)
          value = (column.sum() - total_intensity[-1] if len(total_intensity)>0 else 0) / (2*size + 1) ** 2
          z_value = np.sum(slice(Z, series.rs, series.cs, marker.r, marker.c, size=size)) / (2*size + 1) ** 2
          mean_value = np.sum(slice(mean, series.rs, series.cs, marker.r, marker.c, size=size)) / (2*size + 1) ** 2
          total_intensity.append(column.sum())

        # curve fit
        # popt, pcov = curve_fit(f, list(range(7)), np.array(total_intensity) / np.max(total_intensity))
        # popt, pcov = curve_fit(f, list(sizes), np.array(total_intensity))
        # a, b = popt[0], popt[1]

        # fit = np.array([f(x, a, b) for x in range(7)]) - b
        # fit = np.array([f(x, a, b) for x in sizes]) - b

        if series.cell_instances.filter(gon__marker=marker).count()>0:
          # plt.plot(np.log(np.linspace(0,20,20)), np.log(np.array(total_intensity)), label='{}'.format(marker.pk), c='red' if marker.gon.cell_instance.cell.pk in [76, 77, 79, 80, 84, 86] else 'blue')
          plt.plot(np.log(np.linspace(0,20,20)), np.log(np.array(total_intensity)), label='{}'.format(marker.pk))
          print(marker.gon.cell_instance.cell.pk, marker.pk)
          # plt.plot(np.array(total_intensity) / np.max(total_intensity), c='red' if marker.gon.cell_instance.cell.pk in [76, 77, 79, 80, 84, 86] else 'blue')

    plt.legend()
    plt.show()
