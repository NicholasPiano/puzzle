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
    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])
    composite = series.composites.get()
    output_dir = os.path.join(series.experiment.base_path, 'img/markers', series.name)
    sizes = range(0,20)

    for t in range(series.ts):

      # load gfp
      print('t={} loading gfp...'.format(t))
      gfp_gon = composite.gons.get(t=t, channel__name='0')
      gfp = gfp_gon.load()
      gfp = exposure.rescale_intensity(gfp * 1.0)
      gfp = gf(gfp, sigma=2)

      # load bf
      print('t={} loading bf...'.format(t))
      bf_gon = composite.gons.get(t=t, channel__name='1')
      bf = bf_gon.load()
      bf = exposure.rescale_intensity(bf * 1.0)

      # markers
      print('t={} loading marker gons...'.format(t))
      for marker in series.markers.filter(t=t):
        if series.cell_instances.filter(gon__marker=marker).count()>0:

          # load gon
          gon = marker.gon
          r, c, rs, cs = gon.r if gon.r>=0 else 0, gon.c if gon.c>=0 else 0, 256 if gon.r>=0 else gon.r + 256, 256 if gon.c>=0 else gon.c + 256

          # cut from bf at correct level
          z = marker.z - 8
          gfp_slice = np.sum(gfp[r:r+rs,c:c+cs,z-8 if z-8>=0 else 0:z+7 if z+7<series.zs else series.zs], axis=2)
          bf_slice = bf[r:r+rs,c:c+cs,z]

          # get column
          total_intensity = []
          for size in sizes:
            column = scan_point(gfp, series.rs, series.cs, marker.r, marker.c, size=size)
            # value = (column.sum() - total_intensity[-1] if len(total_intensity)>0 else 0) / (2*size + 1) ** 2 # average area
            value = 1.0 - np.mean(exposure.rescale_intensity(column * 1.0))
            total_intensity.append(value)

          data = np.array(total_intensity) / np.max(total_intensity)
          min_data = np.min(data)
          max_data = 1.0
          data_arg_max = np.argmax(data)

          # plot
          fig = plt.figure()
          fig.suptitle('t={} {} {}'.format(t, marker.gon.id_token, marker.gon.cell_instance.cell.pk))

          ### gfp plot
          ax_gfp = fig.add_subplot(221)
          ax_gfp.imshow(gfp_slice, cmap='Greys_r')

          # radius box blue
          ax_gfp.plot(np.linspace(marker.c - c + 20, marker.c - c + 20, 40), np.linspace(marker.r - r - 20, marker.r - r + 20, 40), c='blue')
          ax_gfp.plot(np.linspace(marker.c - c - 20, marker.c - c - 20, 40), np.linspace(marker.r - r - 20, marker.r - r + 20, 40), c='blue')
          ax_gfp.plot(np.linspace(marker.c - c - 20, marker.c - c + 20, 40), np.linspace(marker.r - r + 20, marker.r - r + 20, 40), c='blue')
          ax_gfp.plot(np.linspace(marker.c - c - 20, marker.c - c + 20, 40), np.linspace(marker.r - r - 20, marker.r - r - 20, 40), c='blue')

          # max box green
          ax_gfp.plot(np.linspace(marker.c - c + data_arg_max, marker.c - c + data_arg_max, 40), np.linspace(marker.r - r - data_arg_max, marker.r - r + data_arg_max, 40), c='green')
          ax_gfp.plot(np.linspace(marker.c - c - data_arg_max, marker.c - c - data_arg_max, 40), np.linspace(marker.r - r - data_arg_max, marker.r - r + data_arg_max, 40), c='green')
          ax_gfp.plot(np.linspace(marker.c - c - data_arg_max, marker.c - c + data_arg_max, 40), np.linspace(marker.r - r + data_arg_max, marker.r - r + data_arg_max, 40), c='green')
          ax_gfp.plot(np.linspace(marker.c - c - data_arg_max, marker.c - c + data_arg_max, 40), np.linspace(marker.r - r - data_arg_max, marker.r - r - data_arg_max, 40), c='green')

          ax_gfp.scatter(marker.c - c, marker.r - r)
          ax_gfp.set_ylim([gfp_slice.shape[0], 0])
          ax_gfp.set_xlim([0, gfp_slice.shape[1]])

          ### bf plot
          ax_bf = fig.add_subplot(222)
          ax_bf.imshow(bf_slice, cmap='Greys_r')

          # radius box blue
          ax_bf.plot(np.linspace(marker.c - c + 20, marker.c - c + 20, 40), np.linspace(marker.r - r - 20, marker.r - r + 20, 40), c='blue')
          ax_bf.plot(np.linspace(marker.c - c - 20, marker.c - c - 20, 40), np.linspace(marker.r - r - 20, marker.r - r + 20, 40), c='blue')
          ax_bf.plot(np.linspace(marker.c - c - 20, marker.c - c + 20, 40), np.linspace(marker.r - r + 20, marker.r - r + 20, 40), c='blue')
          ax_bf.plot(np.linspace(marker.c - c - 20, marker.c - c + 20, 40), np.linspace(marker.r - r - 20, marker.r - r - 20, 40), c='blue')

          # max box green
          ax_bf.plot(np.linspace(marker.c - c + data_arg_max, marker.c - c + data_arg_max, 40), np.linspace(marker.r - r - data_arg_max, marker.r - r + data_arg_max, 40), c='green')
          ax_bf.plot(np.linspace(marker.c - c - data_arg_max, marker.c - c - data_arg_max, 40), np.linspace(marker.r - r - data_arg_max, marker.r - r + data_arg_max, 40), c='green')
          ax_bf.plot(np.linspace(marker.c - c - data_arg_max, marker.c - c + data_arg_max, 40), np.linspace(marker.r - r + data_arg_max, marker.r - r + data_arg_max, 40), c='green')
          ax_bf.plot(np.linspace(marker.c - c - data_arg_max, marker.c - c + data_arg_max, 40), np.linspace(marker.r - r - data_arg_max, marker.r - r - data_arg_max, 40), c='green')

          ax_bf.scatter(marker.c - c, marker.r - r)
          ax_bf.set_ylim([gfp_slice.shape[0], 0])
          ax_bf.set_xlim([0, gfp_slice.shape[1]])

          ### combo plot
          ax_combo = fig.add_subplot(223)
          ax_combo.imshow(0.5 * bf_slice + 0.5 * gfp_slice, cmap='Greys_r')

          # radius box blue
          ax_combo.plot(np.linspace(marker.c - c + 20, marker.c - c + 20, 40), np.linspace(marker.r - r - 20, marker.r - r + 20, 40), c='blue')
          ax_combo.plot(np.linspace(marker.c - c - 20, marker.c - c - 20, 40), np.linspace(marker.r - r - 20, marker.r - r + 20, 40), c='blue')
          ax_combo.plot(np.linspace(marker.c - c - 20, marker.c - c + 20, 40), np.linspace(marker.r - r + 20, marker.r - r + 20, 40), c='blue')
          ax_combo.plot(np.linspace(marker.c - c - 20, marker.c - c + 20, 40), np.linspace(marker.r - r - 20, marker.r - r - 20, 40), c='blue')

          # max box green
          ax_combo.plot(np.linspace(marker.c - c + data_arg_max, marker.c - c + data_arg_max, 40), np.linspace(marker.r - r - data_arg_max, marker.r - r + data_arg_max, 40), c='green')
          ax_combo.plot(np.linspace(marker.c - c - data_arg_max, marker.c - c - data_arg_max, 40), np.linspace(marker.r - r - data_arg_max, marker.r - r + data_arg_max, 40), c='green')
          ax_combo.plot(np.linspace(marker.c - c - data_arg_max, marker.c - c + data_arg_max, 40), np.linspace(marker.r - r + data_arg_max, marker.r - r + data_arg_max, 40), c='green')
          ax_combo.plot(np.linspace(marker.c - c - data_arg_max, marker.c - c + data_arg_max, 40), np.linspace(marker.r - r - data_arg_max, marker.r - r - data_arg_max, 40), c='green')

          ax_combo.scatter(marker.c - c, marker.r - r)
          ax_combo.set_ylim([gfp_slice.shape[0], 0])
          ax_combo.set_xlim([0, gfp_slice.shape[1]])

          ### radius plot
          ax_radius = fig.add_subplot(224)
          ax_radius.plot(data)
          ax_radius.plot(np.linspace(np.argmax(data), np.argmax(data), 10), np.linspace(min_data, max_data, 10))

          plt.savefig(os.path.join(output_dir, '{}_s{}_t{}_id-{}_pk-{}.png'.format(series.experiment.name, series.name, t, marker.gon.id_token, marker.gon.cell_instance.cell.pk)))
          plt.cla()

          print('t={} loading marker gons... {} {} {} {} z{}'.format(t, r, c, rs, cs, z))
