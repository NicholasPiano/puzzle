#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.cell.models import Marker

#util
import os
import re
import numpy as np
from scipy.misc import imsave
import matplotlib.pyplot as plt

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # get marker
    marker = Marker.objects.get(pk=986)

    # load combined mask for marker
    combined_mask = marker.combined_mask()

    # area
    # sum entire image
    masked = np.ma.array(combined_mask, mask=combined_mask==0)
    # cell_instance.a = int(masked.sum() / masked.max())

    # region
    region_match = 0
    for region in marker.track.composite.masks.filter(channel__name='regions', gon__t=marker.t).order_by('mask_id'):
      region_array = region.load()
      if np.any(np.bitwise_and(region_array, combined_mask>combined_mask.mean())):
        region_match = region.mask_id

    region = self.vertical_sort_for_region_index(region_match)
    print(region)
