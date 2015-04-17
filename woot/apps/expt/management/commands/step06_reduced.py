#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.expt.util import *
from apps.img import algorithms
from apps.img.models import Composite

#util
import os
import re
import numpy as np
from optparse import make_option
from scipy.misc import imsave
import matplotlib.pyplot as plt

### Command
class Command(BaseCommand):

  option_list = BaseCommand.option_list + (

    make_option('--expt', # path of images unique to this experiment.
      action='store',
      dest='expt',
      default='050714-test',
      help='Name of experiment to modify'
    ),

    make_option('--series', # defines base search path. All images are in a subdirectory of this directory.
      action='store',
      dest='series',
      default='13',
      help='Name of series to modify'
    ),

    make_option('--composite', # path of images unique to this experiment.
      action='store',
      dest='composite',
      default='0',
      help='Composite to add to'
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    # 1. get composite
    composite = Composite.objects.get(experiment__name=options['expt'], series__name=options['series'])

    # 2. Create mod
    mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_step5_bf_gfp_reduced')
    mod.run()
