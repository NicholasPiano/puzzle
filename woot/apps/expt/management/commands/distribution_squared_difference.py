# expt.command: step03_pmod

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.img.models import Composite
from apps.expt.util import *
from apps.img.util import *

# util
import os
from optparse import make_option
import matplotlib.pyplot as plt
from scipy.misc import imread, imsave
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
import numpy as np
from skimage import filter as ft
import random
from random import randint as rand
from scipy.ndimage.filters import laplace

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714-test', # some default
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
    '''

    ### SETUP
    def create_path(path):
      if not os.path.exists(path):
        os.mkdir(path)

    base_output_path = '/Volumes/transport/demo/test/'

    create_path(base_output_path)

    # scan point
    def scan_point(gfp, rs, cs, r, c, size=3):
      r0 = r - size if r - size >= 0 else 0
      r1 = r + size if r + size <= rs else rs
      c0 = c - size if c - size >= 0 else 0
      c1 = c + size if c + size <= cs else cs

      column = gfp[r0:r1,c0:c1,:]
      column_1D = np.sum(np.sum(column, axis=0), axis=0)

      return column_1D

    def square_difference(standard, distribution):
      diff = 0
      for s,d in zip(list(standard), list(distribution)):
        diff += (s-d)**2 / len(standard)

      return diff

    class Distribution():
      def __init__(self, r, c, data, max_value, mean_value, min_value, z, is_marker):
        self.r = r
        self.c = c
        self.data = data
        self.max_value = max_value
        self.mean_value = mean_value
        self.min_value = min_value
        self.z = z
        self.is_marker = is_marker
        self.r2 = 0

    # select composite
    composite = Composite.objects.get(experiment__name=options['expt'], series__name=options['series'])
    ### SETUP

    ### 2. Same as (1), but for each level
    ''
    path = os.path.join(base_output_path, 'mask-z')
    create_path(path)

    # mask = np.zeros(composite.series.shape(), dtype=float)
    # levels = np.zeros(composite.series.shape(), dtype=float)
    gfp_gon = composite.gons.get(channel__name='0', t=0)
    gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)
    gfp = gf(gfp, sigma=2)

    distributions = []
    marker_positions = [(marker.r, marker.c) for marker in composite.series.markers.filter(t=0)]

    step = 16
    mean = 0
    count = 0
    for r in range(0,gfp.shape[0],step):
      for c in range(0,gfp.shape[1],step):

        # get column and normalise
        gfp_column = scan_point(gfp, gfp.shape[0], gfp.shape[1], r, c)
        data = np.array(gfp_column) / np.max(gfp_column)

        # get details about each point
        max_value = np.max(data)
        mean_value = np.mean(data)
        min_value = np.min(data)
        z = np.argmax(data)
        is_marker = bool(np.sum([np.sqrt((r-R)**2 + (c-C)**2)<=3*step for R,C in marker_positions]))

        # mean
        mean += mean_value
        count += 1

        print(r,c)

        # create object with details
        distributions.append(Distribution(r=r,
                                          c=c,
                                          data=data,
                                          max_value=max_value,
                                          mean_value=mean_value,
                                          min_value=min_value,
                                          z=z,
                                          is_marker=is_marker))


    # set extrema
    mean = mean / count
    max_z = 0
    min_z = 1000

    mean_threshold_distributions = list(filter(lambda d: d.mean_value>mean, distributions))

    for distribution in mean_threshold_distributions:
      max_z = distribution.z if distribution.z>max_z else max_z
      min_z = distribution.z if distribution.z<min_z else min_z

    print(max_z,min_z)

    # build comparator
    # max is the distance between the top and the highest maximum
    # min is the distance between the bottom and the lowest minimum
    comparator_max = gfp_gon.zs - max_z
    comparator_min = -min_z

    # translate comparator bounds into distribution coordinates
    def cut(data, d_z):
      upper = d_z + comparator_max
      lower = d_z + comparator_min
      return data[lower:upper]

    for distribution in mean_threshold_distributions:
      # print(distribution.is_marker)
      #
      # if sample is None and distribution.is_marker:
      #   sample = distribution
      #   cut_sample = cut(sample.data, sample.z)
      #
      cut_distribution = cut(distribution.data, distribution.z)

      plt.plot(np.arange(comparator_min, comparator_max), cut_distribution)
      # plt.plot(np.convolve(cut_sample, cut_distribution))

    plt.show()
