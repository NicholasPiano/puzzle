#django
from django.core.management.base import BaseCommand, CommandError

#local
from apps.img.models import Bulk

#util

### Command
class Command(BaseCommand):
  args = ''
  help = ''

  def handle(self, *args, **options):
    b = Bulk.objects.get(pk=1)
    b.tile()
