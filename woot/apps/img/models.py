#woot.apps.img.models

#django
from django.db import models

#local
from apps.cell.models import Experiment

#util
import os
from scipy.misc import imread, imsave

### Models
class Composite(models.Model):
  ''' A 3D collection of chunks. '''
  #connections
  experiment = models.ForeignKey(Experiment, related_name='composites')

  #properties
  rows = models.IntegerField(default=0)
  columns = models.IntegerField(default=0)
  levels = models.IntegerField(default=0)
  timepoints = models.IntegerField(default=0)

  #methods
  def chunkify(self, chunk_size=(5,5,5)):
    #create chunk objects using dimensions of images
    pass

class Channel(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='channels')

  #properties
  name = models.CharField(max_length='255')

class SourceImage(models.Model):
  '''
  Stores original details about the source images from which pixel objects and chunk objects are derived.

  An image can be uniquely identified by its full path. This must be checked before creating another image object.

  '''
  #connections
  experiment = models.ForeignKey(Experiment, related_name='images')
  composite = models.ForeignKey(Composite, related_name='images', null=True)
  channel = models.ForeignKey(Channel, related_name='images', null=True)

  #properties
  path = models.CharField(max_length=255)
  array = None

  timepoint = models.IntegerField(default=0)
  level = models.IntegerField(default=0)

  #methods
  def load(self):
    self.array = imread(self.path)

class Chunk(models.Model):
  ''' Subdivisions of an image of constant size, say 16x16x16. '''
  #connections
  composite = models.ForeignKey(Composite, related_name='chunks')

  #properties
  ''' n-dimension parameter space for chunks. '''
  #1. coordinates of chunk origin
  row = models.IntegerField(default=0)
  column = models.IntegerField(default=0)
  level = models.IntegerField(default=0)
  timepoint = models.IntegerField(default=0)

  #2. extent of the chunk boundaries
  rows = models.IntegerField(default=0)
  columns = models.IntegerField(default=0)
  levels = models.IntegerField(default=0)

  #methods
  def load(self): #will be quite expensive
    pass

class ChunkImage(models.Model):
  #connections
  

  #properties

class Parameter(models.Model):
  #connections
  composite = models.ForeignKey(Composite, related_name='parameters')

  #properties
  name = models.CharField(max_length='255')

class ParameterInstance(models.Model):
  #connections
  composite = models.ForeignKey(Composite, related_name='parameter_instances')
  parameter = models.ForeignKey(Parameter, related_name='instances')

  #properties
  value = models.IntegerField(default=0)
  float_value = models.FloatField(default=0.0)
  boolean_value = models.BooleanField(default=False)
