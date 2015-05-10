# expt.command: step11_reduced

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series
from apps.expt.util import *
from apps.expt.data import *
from apps.img.util import nonzero_mean

# util
import os
import numpy as np
from optparse import make_option
import matplotlib.pyplot as plt
from scipy.ndimage.measurements import center_of_mass as cm
from scipy.ndimage.morphology import distance_transform_edt as dt
from scipy.ndimage.morphology import binary_erosion as be

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
    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])
    composite = series.composites.get()

    for t in range(series.ts):
      mask_gon_set = composite.gons.filter(channel__name__in=['pmodreduced','bfreduced'], template__name='cp', t=t)

      # make stack at t
      stack = None
      stack_dictionary = {}

      for i,mask_gon in enumerate(mask_gon_set):
        stack_dictionary.update({i: mask_gon.pk})
        stack = mask_gon.load() if stack is None else np.dstack([stack, mask_gon.load()])

      # load region mask for t
      region_gon = composite.gons.get(channel__name='-regions', t=t)
      regions = region_gon.load()
      region_dict = {}
      for re, unique_region in enumerate(np.unique(regions)):
        region_dict.update({unique_region: re})

      # loop through markers
      for m, marker in enumerate(series.markers.filter(t=t)):
        # print('step 13 | t={}, marker {}/{}'.format(t, m+1, series.markers.filter(t=t).count()))
        # cut stack to a column on the marker centre
        # column = stack[marker.r, marker.c, :]
        #
        # cell_mask = np.zeros((series.rs, series.cs))
        # for i,mask_id in enumerate(column):
        #   if mask_id!=0:
        #
        #     mask = stack[:,:,i]!=mask_id
        #
        #     for j,mask_id in enumerate(column):
        #       if mask_id!=0:
        #         masked = np.ma.array(stack[:,:,j], mask=mask, fill_value=0)
        #
        #         for unique_value in [u for u in np.unique(masked.filled()) if u>0]:
        #
        #           cell_mask += (stack[:,:,j]==unique_value) * 1.0 # add modifier based on height difference here
        #
        # cell_mask[cell_mask<cell_mask.max()-cell_mask.max()/3.0] = 0

        # make new cell, cell_instance
        cell, cell_created = series.cells.get_or_create(experiment=series.experiment, cell_id=marker.track.track_id, cell_index=marker.track.index)
        cell_instance = cell.cell_instances.create(experiment=series.experiment, series=series)

        # area
        # cell_instance.a = (cell_mask>0).sum()

        # centre of mass
        # (r, c) = cm(cell_mask)
        cell_instance.r = marker.r
        cell_instance.c = marker.c
        cell_instance.z = marker.z
        cell_instance.t = marker.t

        # region
        region_query = regions[marker.r,marker.c]
        offset = 1
        while region_query==0:
          region_query = regions[marker.r,marker.c+offset]
          offset += 1
        region = series.vertical_sort_for_region_index(region_dict[region_query])
        cell_instance.region = series.regions.get(index=region)
        cell_instance.save()
        cell.save()
