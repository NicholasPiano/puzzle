#django
from django.core.management.base import BaseCommand, CommandError

#local
from apps.cell.models import Experiment
from apps.img import settings as img_settings
from apps.img.models import SourceImage

#util
import os
import re
from optparse import make_option

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (
    make_option('--path',
      action='store',
      dest='path',
      default='',
      help='Path to scan for images'
    ),
    make_option('--base',
      action='store',
      dest='base',
      default='/Users/nicholaspiano/data/',
      help='Base path on filesystem'
    ),
  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    #get path
    input_path = os.path.join(options['base'], options['path'])

    #list directory filtered by allow extension
    image_file_list = list(filter(lambda i: os.path.splitext(i)[1] in img_settings.allowed_file_extensions, os.listdir(input_path)))

    #for each filename, generate dictionary of parameters
    for image_file_name in image_file_list:
      self.stdout.write(image_file_name + '... ', ending='')
      match = re.match(img_settings.img_template, image_file_name)
      #need path, experiment_name, image_type, timepoint, level, and extension to make image object
      #1. check if experiment exists
      experiment, exp_created = Experiment.objects.get_or_create(name=match.group('experiment_name'))

      #2. create image object
      image, created = experiment.images.get_or_create(path=os.path.join(input_path, image_file_name))
      if created:
        image.type = img_settings.img_type(match.group('image_type'))
        image.timepoint = int(match.group('timepoint'))
        image.level = int(match.group('level'))
        image.save()
        experiment.save()
        self.stdout.write('created.', ending='\n')
      else:
        self.stdout.write('already exists.', ending='\n')
