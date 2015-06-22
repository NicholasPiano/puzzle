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

def scan_point(img, rs, cs, r, c, size=3):
  r0 = r - size if r - size >= 0 else 0
  r1 = r + size if r + size <= rs else rs
  c0 = c - size if c - size >= 0 else 0
  c1 = c + size if c + size <= cs else cs

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
    t = 0
    markers = series.markers.filter(t=t)
    image_template = os.path.join(output_dir, '{}_s{}_ch-{}_t{}_z{}_m{}.tiff') # expt, series, channel, t, z, marker
    delta_z = -8

    # load gfp
    gfp_gon = composite.gons.get(t=t, channel__name='0')
    gfp = gfp_gon.load()
    gfp = exposure.rescale_intensity(gfp * 1.0)
    gfp = gf(gfp, sigma=2)

    # gfp profile image
    gfp_profile_mean = np.zeros((series.rs, series.cs))
    gfp_profile_std = np.zeros((series.rs, series.cs))
    gfp_profile_z = np.zeros((series.rs, series.cs))

    if not os.path.exists(os.path.join(output_dir, 'profile_mean_t{}.tiff'.format(t))):
      for r in range(series.rs):
        for c in range(series.cs):
          print('scanning {} {} ...'.format(r,c))
          # get column and normalise
          d = scan_point(gfp, gfp.shape[0], gfp.shape[1], r, c)
          data = np.array(d) / np.max(d)

          # get details about each point
          gfp_profile_mean[r,c] = np.mean(data)
          gfp_profile_std[r,c] = np.std(data)
          gfp_profile_z[r,c] = np.argmax(data)

      imsave(os.path.join(output_dir, 'profile_mean_t{}.tiff'.format(t)), gfp_profile_mean)
      imsave(os.path.join(output_dir, 'profile_std_t{}.tiff'.format(t)), gfp_profile_std)
      imsave(os.path.join(output_dir, 'profile_z_t{}.tiff'.format(t)), gfp_profile_z)

    else:
      gfp_profile_mean = exposure.rescale_intensity(imread(os.path.join(output_dir, 'profile_mean_t{}.tiff'.format(t))) * 1.0)
      gfp_profile_std = exposure.rescale_intensity(imread(os.path.join(output_dir, 'profile_std_t{}.tiff'.format(t))) * 1.0)
      gfp_profile_z = exposure.rescale_intensity(imread(os.path.join(output_dir, 'profile_z_t{}.tiff'.format(t))) * 1.0)

    # load bf
    bf_gon = composite.gons.get(t=t, channel__name='1')
    bf = bf_gon.load()
    bf = exposure.rescale_intensity(bf * 1.0)

    for marker in markers[:1]:
      # determine z based on marker location and delta z
      z = marker.z + delta_z

      # 1. gfp intensity
      # sum z +- dz for each marker -> 050714_s13_ch-gfpsmooth_t0_z37_c0.tiff
      z0 = z - np.abs(delta_z) if z - np.abs(delta_z) >= 0 else 0
      z1 = z + np.abs(delta_z) if z + np.abs(delta_z) < series.zs else series.zs - 1
      gfp_intensity = np.sum(gfp[:,:,z0:z1], axis=2)
      imsave(image_template.format(series.experiment.name, series.name, 'gfp', t, z, marker.pk), gfp_intensity)

      # 2. gfp profile mean
      # imsave()

      # 3. gfp profile stdx

      # 4. bf edge image (smoothed)
      bf_edge = np.zeros((series.rs, series.cs))
      bf_edge_smooth = np.zeros((series.rs, series.cs))

      for sigma in range(2,5):
        bf_edge += ft.canny(bf[:,:,z], sigma=sigma)

      bf_edge_smooth = gf(bf_edge, sigma=2)
      imsave(image_template.format(series.experiment.name, series.name, 'edge', t, z, marker.pk), bf_edge)
      imsave(image_template.format(series.experiment.name, series.name, 'edgesmooth', t, z, marker.pk), bf_edge)

      # 5. brightfield image at z + dz of each marker
      imsave(image_template.format(series.experiment.name, series.name, 'bf', t, z, marker.pk), bf[:,:,z])

      # 6. marker dot in black image
      marker_img = np.zeros((series.rs, series.cs))
      marker_img[marker.r-3:marker.r+3,marker.c-3:marker.c+3] = 255
      imsave(image_template.format(series.experiment.name, series.name, 'marker', t, z, marker.pk), marker_img)

      # 7. single image with all marker at a timestep
      all_marker_img = np.zeros((series.rs, series.cs))
      for m in markers:
        all_marker_img[m.r-3:m.r+3,m.c-3:m.c+3] = 255

      imsave(image_template.format(series.experiment.name, series.name, 'allmarker', t, z, marker.pk), all_marker_img)
