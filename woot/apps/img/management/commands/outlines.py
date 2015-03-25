#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.pix.models import Gon, Composite

#util
import os
import re
from optparse import make_option
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.morphology import binary_dilation as bd
from scipy.misc import imsave

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):

    C = Composite.objects.get()

    # bf
    bf_gon = C.gons.get(channel__name='1', t=0)

    # masks
    masks = C.series.gons.filter(channel__name='mask', t=0).exclude(id_token='')

    for level in bf_gon.gons.order_by('z'):

      # load array
      array = level.load()

      # for each cell instance at this level, put an outline on the image
      for mask in masks.filter(z=level.z):
        # load
        m = mask.load()

        # place in black field
        b = np.zeros(array.shape)
        b[mask.r:mask.r+mask.rs,mask.c:mask.c+mask.cs] = m

        # dilate to get outline
        d = bd(b)
        outline = d - b

        array[outline>0] = 255

      # save array
      imsave(os.path.join(C.experiment.base_path, 'plot', 'outlines_z%d.tiff' % (level.z)), array)
