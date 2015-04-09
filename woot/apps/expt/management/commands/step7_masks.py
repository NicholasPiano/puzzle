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
from scipy.misc import imsave
import matplotlib.pyplot as plt

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # 1. input masks for each series
    for series in Series.objects.all():
      file_list = [file_name for file_name in os.listdir(series.experiment.mask_path) if os.path.splitext(file_name)[1] in allowed_img_extensions]

      template = series.experiment.templates.get(name='cp')

      for file_name in file_list:
        print('processing mask path %s... ' % file_name, end='\r')
        file_dict = template.dict(file_name)

        # 1. get current composite, channel
        composite = series.composites.get(id_token=file_dict['composite_id'])
        channel = composite.channels.get(name=file_dict['channel'])
        cp_template = composite.templates.get(name='cp')
        mask_template = composite.templates.get(name='mask')

        # 2. get or create channel
        mask_channel, mask_channel_created = composite.channels.get_or_create(name=file_dict['secondary_channel'])

        # 3. get or create gon only if path does not yet exist
        path_url = os.path.join(series.experiment.mask_path, file_name)
        if mask_channel.paths.filter(url=path_url).count()==0:
          t = int(file_dict['t'])
          z = int(file_dict['z'])

          gon = series.gons.create(experiment=series.experiment, composite=composite, channel=mask_channel)
          gon.set_origin(0,0,z,t)
          gon.set_extent(series.rs, series.cs, 1)

          gon.paths.create(composite=composite, channel=mask_channel, template=cp_template, url=path_url, file_name=file_name, t=t, z=z)

          gon.save()

          # open file and get split into masks
          mask_array = gon.load()
          for i, unique_id in enumerate([u for u in np.unique(mask_array) if u>0]):
            print('processing mask path %s... %d masks' % (file_name, (i+1)) , end='\r')

            # make mask
            mask = gon.masks.create(composite=composite, channel=mask_channel, mask_id=unique_id)

            # cut
            unique_image = np.zeros(mask_array.shape)
            unique_image[mask_array==unique_id] = 1
            cut, (r,c,rs,cs) = cut_to_black()

            mask.r = r
            mask.c = c
            mask.rs = rs
            mask.cs = cs
            mask.save()

          print('processing mask path %s... %d masks... done.' % (file_name, (i+1)) , end='\n')
