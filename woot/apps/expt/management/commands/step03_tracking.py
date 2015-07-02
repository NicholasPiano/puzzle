# expt.command: step07_tracks

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series
from apps.expt.util import *

# util
import os
from optparse import make_option
from skimage import exposure
from scipy.ndimage.filters import gaussian_filter as gf
import numpy as np
import sys
import pygame
from pygame import surfarray

pygame.init()

# methods
def prep_img(img):
  new_img = img.copy()
  new_img = np.dstack([new_img, new_img, new_img])
  new_img = np.rot90(new_img)
  new_img = np.flipud(new_img)
  return new_img

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
    > Takes in an arbitrary number of track files from Fiji/ImageJ and converts them into tracks/markers

    2. What data structures are input?
    > None

    3. What data structures are output?
    > Track, Marker

    4. Is this stage repeated/one-time?
    > Repeated

    Steps:

    1. Scan track directory for new files
    2. Apply track template to the file names and match them with the specified experiment and series
    3. Open each file in turn and extract tracks (id's) and markers (lines)
    4. Tracks are uniquely identified by an id_token

    '''

    # 1. get series
    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])
    composite = series.composites.get()

    # 2. check for .csv files in tracking directory
    for file_name in [f for f in os.listdir(series.experiment.track_path) if '._' not in f]:
      pass

    # 3. open image sets to display
    zcomp_set = composite.gons.filter(channel__name='-zcomp')

    # 4. open pygame window and load tracking interface
    # initial image
    t = 0
    img = zcomp_set.get(t=t).load()
    img = prep_img(img)
    screen = pygame.display.set_mode(img.shape[:2], 0, 32)

    loop = True
    count = 0
    while loop:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
          print(event)
          # print(pygame.mouse.get_pos())
          count += 1

      if count == 4:
        loop = False

      # surfarray.blit_array(screen, img)
      pygame.display.flip()

    # 5. save markers to .csv file in tracking directory
