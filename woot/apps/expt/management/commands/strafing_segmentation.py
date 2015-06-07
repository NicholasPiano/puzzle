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

    mean = np.zeros(composite.series.shape(), dtype=float)
    regions = np.zeros(composite.series.shape(), dtype=int)
    population = np.zeros(composite.series.shape(), dtype=int)
    Z = np.zeros(composite.series.shape(), dtype=int)
    gfp_gon = composite.gons.get(channel__name='0', t=0)
    gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)
    gfp = gf(gfp, sigma=2)

    distributions = []
    marker_positions = [(marker.r, marker.c) for marker in composite.series.markers.filter(t=0)]

    step = 1
    count = 0
    for r in range(0,gfp.shape[0],step):
      for c in range(0,gfp.shape[1],step):

        # get column and normalise
        gfp_column = scan_point(gfp, gfp.shape[0], gfp.shape[1], r, c)
        data = np.array(gfp_column) / np.max(gfp_column)

        # get details about each point
        z = np.argmax(data)
        is_marker = bool(np.sum([np.sqrt((r-R)**2 + (c-C)**2)<=3*step for R,C in marker_positions]))

        # mean
        mean[r,c] = np.mean(data)

        # z
        Z[r,c] = z

        # segmentation
        neighbours = [(R,C) for (R,C) in [(r-1, c-1),(r-1, c),(r, c-1),(r-1, c+1)] if (R>=0 and C>=0 and R<gfp_gon.rs and C<gfp_gon.cs)]
        region_neighbours = [regions[R,C] for R,C in neighbours]
        population_neighbours = [population[R,C] for R,C in neighbours]
        z_neighbours = [abs(Z[R,C]-z) for R,C in neighbours]
        mean_neighbours = [abs(mean[R,C]-mean[r,c]) for R,C in neighbours]

        n = np.argmin(z_neighbours) if len(z_neighbours)>0 else -1
        if n>-1:
          if z_neighbours[n] <= 3 and mean_neighbours[n] <= 0.1:
            regions[r,c] = region_neighbours[n]
          else:
            regions[r,c] = regions.max()+1 # new region

        else:
          regions[r,c] = 1 # no neighbours, so must be first pixel

        population[regions==regions[r,c]] = np.sum(regions==regions[r,c]) # update population

        # print(r, c, z, z_neighbours, region_neighbours, population_neighbours)
        print(r,c)

    # display = np.zeros(composite.series.shape(), dtype=int)
    # display[population>population.mean()] = 1

    plt.imshow(regions)
    plt.show()

    # match distributions based on continuity
