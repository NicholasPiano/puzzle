#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Series
from apps.img.settings import *

#util
import os
import re
import numpy as np

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # for each series, gather masks from mask directory
    for series in Series.objects.all():
      file_list = [file_name for file_name in os.listdir(series.experiment.cp_path) if os.path.splitext(file_name)[1] in allowed_img_extensions]

      # 1. make paths
      for i, file_name in enumerate(file_list):

        # get template
        template = series.experiment.match_template(file_name)
        dict = template.dict(file_name)
        t = int(dict['t'])
        z = int(dict['z'])

        # create mask path first
        mask_path, created = series.mask_paths.get_or_create(experiment=series.experiment, url=os.path.join(series.experiment.cp_path, file_name), file_name=file_name, t=t, z=z)

      # depending on match, process into gons using either single method or bulk method
      # assume only one run through
      region_paths = series.mask_paths.filter(file_name__contains='region')
      mask_paths = series.mask_paths.filter(file_name__contains='mask')

      for composite in series.composites.all():

        ### REGIONS
        region_channel = composite.channels.create(name='region')

        for t in range(series.ts):

          # gon
          gon = series.gons.create(experiment=series.experiment, composite=composite, channel=region_channel)
          gon.set_origin(0,0,0,t)
          gon.set_extent(series.rs, series.cs, series.zs)

          path = region_paths.get(t=t)
          experiment_template = series.experiment.match_template(path.file_name)
          template = composite.templates.get(name=experiment_template.name)

          for z in range(series.zs):
            print('processing %s, %d, %d' % (region_channel.name, t, z))

            # path
            gon.paths.create(composite=composite, channel=region_channel, template=template, url=path.url, file_name=path.file_name, t=t, z=z)

            # sub gon
            sub_gon = series.gons.create(experiment=series.experiment, gon=gon, channel=region_channel)
            sub_gon.set_origin(0,0,z,t)
            sub_gon.set_extent(series.rs, series.cs, 1)
            sub_gon.paths.create(composite=composite, channel=region_channel, template=template, url=path.url, file_name=path.file_name, t=t, z=z)

            sub_gon.save()

          gon.save()

        ### MASKS
        if mask_paths.count()!=0:
          mask_channel = composite.channels.create(name='mask')

          for t in range(series.ts):

            # gon
            gon = series.gons.create(experiment=series.experiment, composite=composite, channel=mask_channel)
            gon.set_origin(0,0,0,t)
            gon.set_extent(series.rs, series.cs, series.zs)

            for z in range(series.zs):
              path = mask_paths.get(t=t, z=z)
              experiment_template = series.experiment.match_template(path.file_name)
              template = composite.templates.get(name=experiment_template.name)

              print('processing %s, %d, %d' % (mask_channel.name, t, z))

              # path
              gon.paths.create(composite=composite, channel=mask_channel, template=template, url=path.url, file_name=path.file_name, t=t, z=z)

              # sub gon
              sub_gon = series.gons.create(experiment=series.experiment, gon=gon, channel=mask_channel)
              sub_gon.set_origin(0,0,z,t)
              sub_gon.set_extent(series.rs, series.cs, 1)
              sub_gon.paths.create(composite=composite, channel=mask_channel, template=template, url=path.url, file_name=path.file_name, t=t, z=z)

              sub_gon.save()

            gon.save()

        composite.save()
