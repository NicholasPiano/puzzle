#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Experiment, Series
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
      default='050714',
      help='Path to scan for images'
    ),
    make_option('--base',
      action='store',
      dest='base',
      default=settings.DATA_ROOT,
      help='Base path on filesystem'
    ),
  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    # get path
    experiment_name = options['path']
    base_path = os.path.join(options['base'], experiment_name)

    # check if experiment exists
    experiment, exp_created = Experiment.objects.get_or_create(name=experiment_name)
    if exp_created:
      experiment.base_path = base_path
      experiment.composite_path = img_settings.default_composite_path
      experiment.img_path = img_settings.default_img_path
      experiment.plot_path = img_settings.default_plot_path
      experiment.save()

    img_path = os.path.join(experiment.base_path, experiment.img_path)

    # list directory filtered by allow extension
    image_file_list = list(filter(lambda i: os.path.splitext(i)[1] in img_settings.allowed_file_extensions, os.listdir(img_path)))

    # for each filename, generate dictionary of parameters
    for image_file_name in image_file_list:
      self.stdout.write(image_file_name + '... ', ending='')
      match = re.match(img_settings.img_template, image_file_name)

      # series
      series, series_created = experiment.series.get_or_create(name=match.group('series_name'))
      if series_created:
        series.id_token = img_settings.generate_id_token(Series)
        series.save()

      # create path objects
      path, path_created = experiment.paths.get_or_create(series=series, url=os.path.join(img_path, image_file_name))
      if path_created:
        self.stdout.write('created.', ending='\n')
        path.channel = img_settings.channel(match.group('channel'))
        path.channel_id = int(match.group('channel'))
        path.frame = int(match.group('frame'))
        path.level = int(match.group('level'))
        path.save()

        # pending composites
        experiment.pending_composite_creation = True # images have just been added
        experiment.save()
      else:
        self.stdout.write('already exists.', ending='\n')
