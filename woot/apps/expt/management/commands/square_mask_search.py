#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.modelss

#util
import os
import re

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    #
