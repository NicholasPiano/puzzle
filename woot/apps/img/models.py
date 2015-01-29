#woot.apps.img.models

#django
from django.db import models

#local
from apps.cell.models import Experiment

#util
import os
from scipy.misc import imread, imsave
import numpy as np

###### Models
### Bulk pixel objects ###
class Bulk(models.Model):
  #properties
  rows = models.IntegerField(default=0)
  columns = models.IntegerField(default=0)
  levels = models.IntegerField(default=0)
  array = None

  #methods
  def load(self):
    pass

class Composite(Bulk):
  ''' A 3D collection of chunks. '''
  #connections
  experiment = models.ForeignKey(Experiment, related_name='composites')

  #properties
  timepoints = models.IntegerField(default=0)

  #methods
  def chunkify(self, chunk_size=(4,4,5)):
    #1. load entire n-D stack
    nd_stack = []
    for channel in self.channels.all():
      channel_stack = []
      print(self.timepoints)
      for timepoint in range(self.timepoints):
        timepoint_stack = []
        for image in self.images.filter(channel=channel, timepoint=timepoint).order_by('level'):
          image.load()
          timepoint_stack.append(image.array)
        timepoint_stack = np.array(timepoint_stack)
        channel_stack.append(timepoint_stack)
        print(timepoint_stack.shape)
      nd_stack.append(np.array(channel_stack))
    nd_stack = np.array(nd_stack)

    # print(nd_stack.shape)
    # print(nd_stack)

    #2. calculate appropriate chunk size


    #3. iterate over stack by chunk size and channel
    #4. create chunk at each instance and set parameters

class Chunk(Bulk):
  ''' Subdivisions of an image of constant size, say 16x16x16. '''
  #connections
  composite = models.ForeignKey(Composite, related_name='chunks')
  timepoint = models.ForeignKey(Timepoint, related_name='chunks')

  #properties
  ''' n-dimension parameter space for chunks. '''
  #1. coordinates of chunk origin
  row = models.IntegerField(default=0)
  column = models.IntegerField(default=0)
  level = models.IntegerField(default=0)

### Discontinuous coordinates ###
class Channel(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='channels')
  composite = models.ForeignKey(Composite, related_name='channels', null=True)

  #properties
  name = models.CharField(max_length='255')
  index = models.IntegerField(default=0)
  mean = models.FloatField(default=0.0)
  max = models.FloatField(default=0.0)
  background = models.FloatField(default=0.0)

class Timepoint(models.Model):
  #connections
  composite = models.ForeignKey(Composite, related_name='timepoints')

  #properties
  index = models.IntegerField(default=0)

### Image storage ###
class Image(models.Model):
  '''
  Stores original details about the images from which chunk objects are derived.
  An image can be uniquely identified by its full path. This must be checked before creating another image object.

  '''
  #connections
  channel = models.ForeignKey(Channel, related_name='images', null=True)
  timepoint = models.ForeignKey(Timepoint, related_name='images', null=True)

  #properties
  array = None
  path = models.CharField(max_length=255)
  rows = models.IntegerField(default=0)
  columns = models.IntegerField(default=0)
  level = models.IntegerField(default=0)

  #methods
  def load(self):
    self.array = imread(self.path)

class SourceImage(Image):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='images')

class ChunkImage(Image):
  #connections
  composite = models.ForeignKey(Composite, related_name='chunk_images', null=True)
  chunk = models.ForeignKey(Chunk, related_name='images')

### Extensible parameters ###
class Parameter(models.Model):
  #connections
  composite = models.ForeignKey(Composite, related_name='parameters')

  #properties
  name = models.CharField(max_length='255')

class ParameterInstance(models.Model):
  #connections
  composite = models.ForeignKey(Composite, related_name='parameter_instances')
  parameter = models.ForeignKey(Parameter, related_name='instances')
  chunk = models.ForeignKey(Chunk, related_name='parameter_instances')

  #properties
  value = models.IntegerField(default=0)
  float_value = models.FloatField(default=0.0)
  boolean_value = models.BooleanField(default=False)
