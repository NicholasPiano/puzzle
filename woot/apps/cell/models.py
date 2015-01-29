#woot.apps.cell.models

#django
from django.db import models

#local


#util
import numpy as np

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
      composite.images.create(
        path=image.path,
        channel=image.channel,
        timepoint=image.timepoint,
        level=image.level
      )
      image.channel.bulk = composite
      image.channel.save()

      image.timepoint.bulk = composite
      image.timepoint.save()

    #get dimensions
    first_image = self.images.all()[0]
    first_image.load()
    rows, columns = first_image.array.shape
    levels = len(list(np.unique([image.level for image in self.images.all()])))
    timepoints = len(list(np.unique([image.timepoint.index for image in self.images.all()])))
    channels = len(list(np.unique([image.channel.index for image in self.images.all()])))

    composite.rows = rows
    composite.columns = columns
    composite.levels = levels
    composite.num_timepoints = timepoints
    composite.num_channels = channels

    #make chunks
    composite.chunkify()

    composite.save()

    self.pending_composite_creation = False
    self.save()
