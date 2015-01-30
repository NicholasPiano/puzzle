#django
from django.core.management.base import BaseCommand, CommandError

#local
from apps.img.models import Composite

#util

### Command
class Command(BaseCommand):
  args = ''
  help = ''

  def handle(self, *args, **options):
    c = Composite.objects.get()
    c.bulkify(timepoint_index=14)
