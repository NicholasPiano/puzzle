#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Series
from apps.img.settings import *

#util
import os
import re
import numpy as np
from scipy.misc import imsave
import matplotlib.pyplot as plt

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    pass
