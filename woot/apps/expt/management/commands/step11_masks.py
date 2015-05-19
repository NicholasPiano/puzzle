# expt.command: step11_reduced

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series
from apps.expt.util import *
from apps.expt.data import *

# util
import os
from optparse import make_option

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714-test', # some default
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
    > Take in mask images from Cell Profiler and convert them into a mask/gon network

    2. What data structures are input?
    > Images

    3. What data structures are output?
    > Channel, Gon, Mask

    4. Is this stage repeated/one-time?
    > Repeated

    Steps:

    1. Add new paths in mask directory
    2. Add the new paths as gons to the current composite.
    3. Call mask mod on composite
    4. Run

    '''

    # 1.
    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])

    # input
    input_path = series.experiment.mask_path

    img_files = [f for f in os.listdir(input_path) if os.path.splitext(f)[1] in allowed_img_extensions]
    for i, file_name in enumerate(img_files):
      path, path_created, path_message = series.experiment.get_or_create_path(series, input_path, file_name)

    # 2. select composite
    # do equivalent of compose: make gons, new paths, etc.
    print('step11 | composing {} series {}... '.format(series.experiment.name, series.name), end='\r')
    composite = series.composites.get()

    for channel_name in ['bfreduced', 'pmodreduced']:
      composite_channel = composite.channels.create(name=channel_name)

      for t in range(series.ts):

        # path set
        path_set = series.paths.filter(channel__name=channel_name, template__name='cp', t=t)

        for path in path_set:

          template = composite.templates.get(name=path.template.name)
          gon = series.gons.create(experiment=series.experiment, composite=composite, channel=composite_channel, template=template)
          gon.set_origin(0,0,path.z,t)
          gon.set_extent(series.rs, series.cs, 1)

          gon.paths.create(composite=composite, channel=composite_channel, template=template, url=path.url, file_name=path.file_name, t=t, z=path.z)
          gon.save()

    # 2. Call mask mod
    mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_step11_masks')

    # 3. Run mod
    print('step11 | processing mod_step11_masks...', end='\r')
    mod.run()
    print('step11 | processing mod_step11_masks... done.')
