#woot.apps.cell.models

#django
from django.db import models

#local


#util


### Models
class Experiment(models.Model):
  ''' The top level unit for study. Stores scaling parameters. '''
  #properties
  name = models.CharField(max_length=255)

  #methods
