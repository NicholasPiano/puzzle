# expt.command: step11_reduced

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series

# util
import os
import numpy as np
from optparse import make_option

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

    cell_instances = series.cell_instances.all()

    for i, cell_instance in enumerate(cell_instances):
      # 1. get r,c
      r, c = cell_instance.r, cell_instance.c
      print(cell_instance.t, r, c)

      # 2. get region image
      region_gon = series.composites.get().gons.get(channel__name='-regions', t=cell_instance.t, id_token='')
      g = region_gon.load()

      # 3. get unique values
      u = list(np.unique(g))

      # 4. get mask value of mask around cell instance
      r0, r1 = r-4 if r-4>=0 else 0, r+4 if r+4<=series.rs else series.rs
      c0, c1 = c-4 if c-4>=0 else 0, c+4 if c+4<=series.cs else series.cs

      mask = g[r0:r1,c0:c1]

      region_index_scaled = np.max(mask)

      # 5. find index from array
      region_index = u.index(region_index_scaled)
      print(cell_instance.t, u, region_index)

      # 6. find true index from series data
      true_region_index = series.vertical_sort_for_region_index(region_index)

      # 7. fetch region object
      region = series.regions.get(index=true_region_index)
      print(cell_instance.t, region.index, region.vertical_sort_index)

      # 8. set region
      cell_instance.region = region
      cell_instance.save()
