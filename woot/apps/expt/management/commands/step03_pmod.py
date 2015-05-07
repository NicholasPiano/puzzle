# expt.command: step03_pmod

# django

# local

# util

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--name', # option that will appear in cmd
      action='store', # no idea
      dest='name', # refer to this in options variable
      default='050714-test', # some default
      help='Path to scan for images' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    '''
    1. What does this script do?
    2. What data structures are input?
    3. What data structures are output?
    4. Is this stage repeated/one-time?

    Steps:

    1.

    '''
