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

  pending_composite_creation = models.BooleanField(default=False)

  #methods
  def create_composite(self):
    ''' Adds all current images to a new composite. '''
