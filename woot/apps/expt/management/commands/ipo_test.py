#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Gon

#util
import os
import re
from optparse import make_option
import scipy
import numpy as np
import matplotlib.pyplot as plt
from skimage import filter as ft
from scipy.misc import imsave

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    gon = Gon.objects.get(pk=330) # bf
    # gon = Gon.objects.get(channel__name__contains='pmod', t=0, z=36) # pmod

    image = gon.load()

    out = '/Volumes/TRANSPORT/data/puzzle/ipo-test/out'

    total = np.zeros(gon.shape())

    for n in range(5):
      edges = ft.canny(image, sigma=n)

      total += edges.astype(int)

      plt.imshow(edges, cmap='Greys_r')
      plt.savefig(os.path.join(out, 'edges_%d.png' % n))
      plt.cla()

    total += (image > image.mean()).astype(int)

    pgon = Gon.objects.get(channel__name__contains='pmod', t=0, z=36) # pmod

    image = pgon.load()

    for n in range(5):
      edges = ft.canny(image, sigma=n)

      total += edges.astype(int)

      plt.imshow(edges, cmap='Greys_r')
      plt.savefig(os.path.join(out, 'edges_p_%d.png' % n))
      plt.cla()



    total[total==np.unique(total)[1]] = 0

    total += (image > image.mean()).astype(int)

    total[total>0] = 1

    total = np.invert(total.astype(bool))

    # plt.imshow(total, cmap='jet')
    # plt.savefig(os.path.join(out, 'total.png'))

    imsave(os.path.join(out, 'total.png'), total)

    # plt.imshow(thresholded_image, cmap='Greys_r')
    # plt.show()

    # 1. get thresholded image -> some algorithm with parameters
    # binary_image = threshold_image(image)

    # 2. Label image and remove undesired objects
    # labeled_image, object_count = scipy.ndimage.label(binary_image, np.ones((3,3), bool))
    # labeled_image, object_count, maxima_suppression_size, LoG_threshold, LoG_filter_diameter = separate_neighboring_objects(labeled_image, object_count)

    # objects touching border
    # labeled_image = filter_on_border(image, labeled_image)

    # too large or too small
    # labeled_image, small_removed_labels = filter_on_size(labeled_image, object_count)

    # 3. relabel image
    # labeled_image, object_count = relabel(labeled_image)

    # 4. Done

# def threshold_image(image):
#
#   # 1. get threshold
#   local_threshold, global_threshold = get_threshold(image, mask, workspace)
#
#   # 3. get smoothed image
#   sigma = 1 # or line 889 in cellprofiler.modules.identify
#   smoothed_image = scipy.ndimage.gaussian_filter(image, sigma, mode='constant', cval=0)
#
#   # 4. get binary image
#   binary_image = (smoothed_image >= local_threshold) & mask
#
#   return binary_image
#
# def get_threshold():
#
#   # if using adaptive method, define block size
#   if self.threshold_scope == TS_ADAPTIVE:
#     image_size = np.array(img.shape[:2], dtype=int)
#     block_size = image_size / 10
#     block_size[block_size<50] = 50
#   else:
#       block_size = None
#
#   # key word parameters for external threshold calculation: cellprofiler.cpmath.threshold.get_threshold
#   kwparams = {}
#   if self.threshold_scope != TS_AUTOMATIC:
#       #
#       # General manual parameters
#       #
#       kwparams['threshold_range_min'] = self.threshold_range.min
#       kwparams['threshold_range_max'] = self.threshold_range.max
#       kwparams['threshold_correction_factor'] = self.threshold_correction_factor.value
#
#   if self.get_threshold_algorithm() == TM_OTSU:
#       #
#       # Otsu-specific parameters
#       #
#       kwparams['use_weighted_variance'] = self.use_weighted_variance.value == O_WEIGHTED_VARIANCE
#       kwparams['two_class_otsu'] = self.two_class_otsu.value == O_TWO_CLASS
#       kwparams['assign_middle_to_foreground'] = self.assign_middle_to_foreground.value == O_FOREGROUND
#
#   local_threshold, global_threshold = get_threshold(self.threshold_algorithm, self.threshold_modifier, img, mask=mask, labels=labels, adaptive_window_size=block_size, **kwparams)
#
# def smooth_with_function_and_mask():
#
# def separate_neighboring_objects():
#
# def filter_on_border():
#
# def filter_on_size():
