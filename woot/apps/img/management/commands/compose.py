#django
from django.core.management.base import BaseCommand, CommandError

#local
from apps.img.models import Bulk

#util
import matplotlib.pyplot as plt
import scipy.io
import numpy as np

### Command
class Command(BaseCommand):
  args = ''
  help = ''

  def handle(self, *args, **options):
    b = Bulk.objects.get(pk=1)

    max_gfp = []
    for s in b.sub_bulks.all():
      print(s.pk)
      max_gfp.append(s.get_value('gfp','max'))

    scipy.io.savemat('/Users/nicholaspiano/code/matlab/max.mat', mdict={'max':np.array(max_gfp)})
