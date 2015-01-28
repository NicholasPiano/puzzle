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
    #create new composite
    composite = self.composites.create()

    #add all source images to composite
    for image in self.images.all():
      composite.images.add(image)
      image.save()

    #get dimensions
    first_image = self.images.all()[0]
    first_image.load()
    rows, columns = first_image.array.shape
    levels = max([image.level for image in self.images.all()]) + 1
    timepoints = max(image.timepoint for image in self.images.all()) + 1

    composite.rows = rows
    composite.columns = columns
    composite.levels = levels
    composite.timepoints = timepoints
    composite.save()

    self.pending_composite_creation = False
    self.save()
