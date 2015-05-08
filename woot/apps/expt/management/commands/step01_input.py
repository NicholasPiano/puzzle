# expt.command: step01_input

# django
from django.conf import settings

# local
from apps.expt.models import Experiment

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
    base_path = settings.DATA_ROOT
    expt_name = options['expt']
    series_name = options['series']
    expt_path = os.path.join(base_path, expt_name)

    # 1. check experiment name in base folder
    if os.path.exists(expt_path):
      # 2. create new experiment
      expt, expt_created = Experiment.objects.get_or_create(name=expt_name)

      if expt_created:
        expt.make_paths(base_path)
        expt.get_metadata()

        # 3. create new series
        if expt.allowed_series(series_name):
          series, series_created = expt.series.get_or_create(name=series_name)

          if series_created or series.paths.count()==0:

            # 4. for each path in the expt folder, create new path if the series matches.
            for root in expt.img_roots():
              print(root)

          else:
            print('series exists: {}.{}'.format(expt_name, series_name))

        else:
          print('not a valid series: {}.{}'.format(expt_name, series_name))

      else:
        print('experiment exists: {}'.format(expt_name))

    else:
      print('experiment not in base folder: {}'.format(base_path))
