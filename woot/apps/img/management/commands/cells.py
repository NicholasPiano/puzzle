#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Series
from apps.img.settings import *
from apps.cell.models import Mask, CellMarker
from apps.pix.models import Gon

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

      markers = {}

      for t in range(series.ts):
        print(t)

        for i, mask in enumerate(Mask.objects.filter(gon__t=t)):
          print([i, Mask.objects.filter(gon__t=t).count()])
          m = mask.load()
          gfp = Gon.objects.get(channel__name='0', zs=1, t=t, z=mask.gon.z)
          g = gfp.load()
          gm = np.ma.array(g, mask=np.invert(m))

          for marker in CellMarker.objects.filter(t=t):
            if m[marker.r, marker.c]:
              if marker.pk in markers:
                markers[marker.pk].append((mask.pk, m.sum(), gm.sum(), t))
              else:
                markers[marker.pk] = [(mask.pk, m.sum(), gm.sum(), t)]

      for i,(key,values) in enumerate(markers.items()):
        print([i, len(markers)])

        marker = CellMarker.objects.get(pk=key)
        track_id = marker.track.track_id

        cell, created = series.cells.get_or_create(experiment=series.experiment, cell_id=track_id)

        z_m = np.argmax([a[2] for a in values])
        mask = Mask.objects.get(pk=values[z_m][0])

        z = mask.gon.z

        r = marker.r
        c = marker.c

        t = marker.t

        a = values[z_m][1]
        region = 1

        cell_instance = cell.cell_instances.create(experiment=series.experiment, series=series, r=r, c=c, z=z, t=t, a=a, region=region)
