# expt.command: step01_input

# django
from django.conf import settings

# local

# util

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='name', # refer to this in options variable
      default='050714-test', # some default
      help='Name of the experiment to import' # who cares
    ),

    make_option('--series', # option that will appear in cmd
      action='store', # no idea
      dest='name', # refer to this in options variable
      default='13', # some default
      help='Name of the series' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    '''
    1. What does this script do?
    > Converts image file names into searchable pixel space composite

    2. What data structures are input?
    > strings

    3. What data structures are output?
    > Experiment, Series, Path, Channel, Composite

    4. Is this stage repeated/one-time?
    > Repeated

    Steps:

    1. check if experiment name is in the base folder
    2. create a new experiment
    3. create a new series
    4. for each path in experiment folder, make a path object.
      - if path object matches the series, keep it, else delete
    5. make composite from series

    '''

    # vars
    base_path = settings.

    # 1. check experiment name in base folder
