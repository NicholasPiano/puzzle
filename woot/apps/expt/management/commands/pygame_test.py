# expt.command: step11_reduced

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series

# util
import os
import numpy as np
from optparse import make_option
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
from skimage import filter as ft
from scipy.misc import imsave, imread
import sys
import pygame as pg

def scan_point(img, rs, cs, r, c, size=3):
  r0 = r - size if r - size >= 0 else 0
  r1 = r + size if r + size <= rs else rs
  c0 = c - size if c - size >= 0 else 0
  c1 = c + size if c + size <= cs else cs

  column = img[r0:r1,c0:c1,:]
  column_1D = np.sum(np.sum(column, axis=0), axis=0)

  return column_1D

def to_rgb(img):
  img = np.rot90(img, k=1)
  img = np.flipud(img)
  return np.dstack([img, img, img])

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714', # some default
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

    # vars
    output_dir = '/Volumes/Extra/test'
    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])
    composite = series.composites.get()
    t = 0

    # load gfp
    gfp_gon = composite.gons.get(t=t, channel__name='0')
    gfp = gfp_gon.load()
    gfp = exposure.rescale_intensity(gfp * 1.0)
    gfp = gf(gfp, sigma=2)

    S = to_rgb(exposure.rescale_intensity(np.sum(gfp, axis=2) * 1.0) * 255)

    # initialise pygame
    pg.init()

    # display gfp sum
    screen = pg.display.set_mode(S.shape[:2], 0, 32)

    loop = True
    while loop:
      # events
      for event in pg.event.get():
        print(event)
        if event.type == pg.QUIT:
          sys.exit()
        elif event.type == pg.MOUSEMOTION:
          print('mouse at {}'.format(event.pos))

      pg.surfarray.blit_array(screen, S)
      pg.display.flip()
