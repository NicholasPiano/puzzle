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
      file_list = [file_name for file_name in os.listdir(series.experiment.mask_path) if os.path.splitext(file_name)[1] in allowed_file_extensions]

      # make paths and series
      for i, file_name in enumerate(file_list):

        # get template
        template = series.experiment.match_template(file_name)
        path, created = template.get_or_create_path(series.experiment.mask_path, file_name)

        print('%s... %s' % (path, 'created.' if created else 'already exists.'))

        # make masks
        masks = path.load()

        unique_ids = list(np.unique(masks))

        if 'region' in file_name:
          for mask_id in unique_ids:
            path.region_masks.get_or_create(experiment=series.experiment, series=series, mask_id=mask_id)
        else:
          for mask_id in unique_ids:
            index = path.cell_masks.filter(mask_id=mask_id).count()
            path.cell_masks.create(experiment=series.experiment, series=series, mask_id=mask_id, index=index)

        path.save()
