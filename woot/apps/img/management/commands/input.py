#django
from django.core.management.base import BaseCommand, CommandError

#local
from apps.img.models import Experiment
from apps.img import settings as img_settings

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
      default='icr-confocal-sample-stack/base/',
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

      #1. check if experiment exists
      experiment, exp_created = Experiment.objects.get_or_create(name=str(match.group('experiment_name')))
      if exp_created:
        experiment.path = input_path

      #3. create path objects
      path, path_created = experiment.paths.get_or_create(url=os.path.join(input_path, image_file_name))
      if path_created:
        self.stdout.write('created.', ending='\n')
        path.channel = img_settings.channel(match.group('channel'))
        path.channel_id = int(match.group('channel'))
        path.timepoint = int(match.group('timepoint'))
        path.level = int(match.group('level'))
        path.save()
      else:
        self.stdout.write('already exists.', ending='\n')

      #pending composites
      experiment.pending_composite_creation = True #images have just been added
      experiment.save()

    #create new composite
    for experiment in Experiment.objects.all():
      if experiment.pending_composite_creation:
        self.stdout.write('creating new composite for experiment %s...'%experiment.name, ending='\n')
        experiment.compose()
        experiment.pending_composite_creation = False
        experiment.save()
