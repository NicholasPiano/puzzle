#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.expt.models import Series
from apps.expt.data import *
from apps.expt.util import generate_id_token
from apps.img.util import cut_to_black

#util
import os
import re
import numpy as np
import tifffile as tiff
from scipy.misc import imsave, imread
import matplotlib.pyplot as plt
from scipy.ndimage.measurements import label
from scipy.ndimage.morphology import binary_erosion as erode

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # 1. input masks for each series
    for series in Series.objects.all():
      file_list = [file_name for file_name in os.listdir(series.experiment.region_path) if os.path.splitext(file_name)[1] in allowed_img_extensions]

      template = series.experiment.templates.get(name='region')

      for file_name in file_list:
        print('processing region path %s... ' % file_name, end='\r')
        file_dict = template.dict(file_name)

        if series.name==file_dict['series']:

          # 1. get current composite, channel
          composite = series.composites.get()
          region_template = composite.templates.get(name='region')
          cp_template = composite.templates.get(name='composite')

          # 2. get or create channel
          region_channel, region_channel_created = composite.channels.get_or_create(name='regions')

          # 3. get or create gon only if path does not yet exist
          t = int(file_dict['t'])
          if region_channel.paths.filter(t=t).count()<1000:
            # make gon
            gon = series.gons.create(experiment=series.experiment, composite=composite, channel=region_channel)
            gon.set_origin(0,0,0,t)
            gon.set_extent(series.rs, series.cs, 1)

            # open file and get split into masks
            region_array = tiff.imread(os.path.join(series.experiment.region_path, file_name))
            region_array = region_array[:,:,0]
            region_array[region_array>0] = 1

            # first binary erode image to ensure correct labelling
            region_array = erode(region_array)

            region_array, n = label(region_array)
            region_array = (region_array / region_array.max() * (len(np.unique(region_array))-1)).astype(int) # rescale

            # save gon image from modified gimp regions
            gon.array = region_array.copy()
            gon.save_single(os.path.join(series.experiment.composite_path, cp_template.rv), cp_template, 0)

            # save masks
            for i, unique_id in enumerate([u for u in np.unique(region_array) if u>0 and u<5]):
              print('processing region path %s... %d regions' % (file_name, (i+1)) , end='\r')

              # make mask
              mask_id = series.vertical_sort_for_region_index(unique_id)
              mask = gon.masks.create(composite=composite, channel=region_channel, mask_id=mask_id)

              unique_image = np.zeros(region_array.shape)
              unique_image[region_array==mask_id] = 1
              cut, (r,c,rs,cs) = cut_to_black(unique_image)

              mask.r = r
              mask.c = c
              mask.rs = rs
              mask.cs = cs
              mask.save()

            print('processing region path %s... %d region... done.' % (file_name, (i+1)) , end='\n')

            # if len(np.unique(region_array))>1:
            #   for i, unique_id in enumerate([u for u in np.unique(region_array) if u>0 and u<5]):
            #     print('processing region path %s... %d regions' % (file_name, (i+1)) , end='\r')
            #
            #     # make mask
            #     mask_id = series.vertical_sort_for_region_index(unique_id)
            #     mask = gon.masks.create(composite=composite, channel=region_channel, mask_id=mask_id)
            #
            #     # cut
            #     unique_image = np.zeros(region_array.shape)
            #     unique_image[region_array==mask_id] = 1
            #     cut, (r,c,rs,cs) = cut_to_black(unique_image)
            #
            #     mask.r = r
            #     mask.c = c
            #     mask.rs = rs
            #     mask.cs = cs
            #     mask.save()
            #
            # else:
            #
            #   # make mask
            #   mask_id = 1
            #   mask = gon.masks.create(composite=composite, channel=region_channel, mask_id=mask_id)
            #
            #   # cut
            #   mask.r = 0
            #   mask.c = 0
            #   mask.rs = region_array.shape[0]
            #   mask.cs = region_array.shape[1]
            #   mask.save()
            #
            # print('processing region path %s... %d region... done.' % (file_name, (i+1)) , end='\n')
