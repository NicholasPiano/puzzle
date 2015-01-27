#woot.apps.img.models

#django
from django.db import models

#local
from apps.cell.models import Experiment

#util
import os
from scipy.misc import imread, imsave

### Models
class Bulk(models.Model):
  ''' A 3D collection of chunks. '''
  #connections

  #properties

  #methods

class SourceImage(models.Model):
  '''
  Stores original details about the source images from which pixel objects and chunk objects are derived.

  An image can be uniquely identified by its full path. This must be checked before creating another image object.

  '''
  #connections
  experiment = models.ForeignKey(Experiment, related_name='images')
  bulk = models.ForeignKey(Bulk, related_name='images', null=True)

  #properties
  path = models.CharField(max_length=255)
  array = None

  type = models.CharField(max_length=255) #gfp, bf, mask
  timepoint = models.IntegerField(default=0)
  level = models.IntegerField(default=0)

  #methods
  def load(self):
    self.array = imread(os.path.join(self.path, self.filename))

class Chunk(models.Model):
  ''' Subdivisions of an image of constant size, say 16x16x16. '''
  #connections
  bulk = models.ForeignKey(Bulk, related_name='chunks')

  #properties
  ''' n-dimension parameter space for chunks. '''
  #1. coordinates of chunk origin
  row = models.IntegerField(default=0)
  column = models.IntegerField(default=0)
  level = models.IntegerField(default=0)
  timepoint = models.IntegerField(default=0)

  #2. values


  #methods

class Pixel(models.Model):
  ''' Stores the n-dimensional parameters of a pixel at a set of spacial coordinates. '''
  #connections
  bulk = models.ForeignKey(Bulk, related_name='pixels')
  source_image = models.ForeignKey(SourceImage, related_name='pixels')
  chunk = models.ForeignKey(Chunk, related_name='pixels')

  #properties
  ''' these paramters determine the location of the pixel in n-dimensional parameter space. '''

  #methods
