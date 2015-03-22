#django
from django.core.management.base import BaseCommand, CommandError

#local
from apps.img.models import Series

#util
import matplotlib.pyplot as plt

### Command
class Command(BaseCommand):
  args = ''
  help = ''

  def handle(self, *args, **options):
    if len(args)==2:
      experiment_name = args[0]
      series_name = args[1]

      if Series.objects.filter(experiment__name=experiment_name, name=series_name).count()>0:
        series = Series.objects.get(experiment__name=experiment_name, name=series_name)
        series.compose()

    else:
      print('Enter an experiment and a series')
