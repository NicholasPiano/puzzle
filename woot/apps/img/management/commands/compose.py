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
    pass
