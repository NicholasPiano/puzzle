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
    for series in Series.objects.all():
      if series.composites.count()==0:
        series.compose()
