# expt.command: step03_pmod

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.img.models import Composite
from apps.expt.util import *

# util
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
    '''

    # 1. select composite
    composite = Composite.objects.get(experiment__name=options['expt'], series__name=options['series'])

    # 2. Call pmod mod
    mod = composite.mods.create(id_token=generate_id_token('img', 'Mod'), algorithm='mod_gfp_smooth_sum')

    # 3. Run mod
    print('step03 | processing mod_gfp_smooth_sum...                              ', end='\r')
    mod.run()
    print('step03 | processing mod_gfp_smooth_sum... done.                            ')
