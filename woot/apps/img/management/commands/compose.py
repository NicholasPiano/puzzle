#django
from django.core.management.base import BaseCommand, CommandError

#local
from apps.img.models import Experiment

#util
import matplotlib.pyplot as plt

### Command
class Command(BaseCommand):
  args = ''
  help = ''

  def handle(self, *args, **options):
    e = Experiment.objects.get()
    s = e.series.get(name='12')
    g = s.gons.get(pk=6)
    g.load()
