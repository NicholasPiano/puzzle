#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.expt.models import Experiment, Series
from apps.expt.data import *
from apps.expt.util import *
from apps.img import algorithms

#util
import os
import re
from optparse import make_option
import inspect

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # path of images unique to this experiment.
      action='store',
      dest='expt',
      default='',
      help='Name of experiment to modify'
    ),

    make_option('--series', # defines base search path. All images are in a subdirectory of this directory.
      action='store',
      dest='series',
      default='',
      help='Name of series to modify'
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):

    if options['expt'] and Experiment.objects.filter(name=options['expt']).count()>0:
      experiment = Experiment.objects.get(name=options['expt'])

      if options['series'] and experiment.series.filter(name=options['series']).count()>0:
        series = experiment.series.get(name=options['series'])

        # show all composites with their pk -> input pk or id_token of composite
        composites = {str(i):composite for i, composite in enumerate(series.composites.all())}
        print('composites in experiment %s, series %s:' % (experiment.name, series.name))
        for i, composite in composites.items():
          print('%s %s -> channels:%s' % (i, composite.id_token, str(' %s,'*composite.channels.count()) % tuple([channel.name for channel in composite.channels.all()])))

        index = input('Enter the composite index: ')
        while index not in composites:
          index = input('Enter the composite index: ')

        composite = composites[index]

        # show all algorithms with an index -> input index or name
        algs = {str(i):value for i, (key, value) in enumerate(algorithms.__dict__.items()) if 'mod_' in key}
        print('available algorithms: ')
        for i, algorithm in algs.items():
          print('%s %s: %s' % (i, algorithm.__name__, algorithm.description))

        index = input('Enter the algorithm index: ')
        while index not in algs:
          index = input('Enter the algorithm index: ')

        algorithm = algs[index]

        # create mod and run
        mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm=algorithm.__name__)
        mod.run()

      else:
        print('series for experiment %s:' % (experiment.name))
        for series in experiment.series.all():
          print('series %s' % (series.name))

    else:
      print('experiments:')
      for experiment in Experiment.objects.all():
        print('%s -> series:%s' % (experiment.name, str(' %s,'*experiment.series.count()) % tuple([series.name for series in experiment.series.all()])))
