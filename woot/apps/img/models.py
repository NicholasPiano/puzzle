#woot.apps.img.models

#django
from django.db import models

#local
from apps.cell.models import Experiment
from apps.img.settings import generate_id_token

#util
import os
from scipy.misc import imread, imsave
import numpy as np

###### Models
### Discontinuous coordinates ###
class Channel(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='channels')

  #properties
  name = models.CharField(max_length='255')
  index = models.IntegerField(default=0)

class Timepoint(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='timepoints')

  #properties
  index = models.IntegerField(default=0)
  next = models.IntegerField(default=-1)
  previous = models.IntegerField(default=-1)

### Bulk pixel objects ###
class Composite(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='composites')
  channels = models.ManyToManyField(Channel, related_name='composites')
  timepoint = models.ForeignKey(Timepoint, related_name='composites')
  composite = models.ForeignKey(Composite, related_name='chunks')

  #properties
  id_token = models.CharField(max_length=255)
  abnormal_sizing = models.BooleanField(default=False)
  rows = models.IntegerField(default=0)
  columns = models.IntegerField(default=0)
  levels = models.IntegerField(default=0)
  array = None

  #methods
  def load(self):
    pass

  def chunkify(self, chunk_size=(8,8,5)):
    #load entire n-D stack
    for timepoint in self.timepoints.all():
      #get channel dictionary
      channel_dictionary = {}
      for channel in self.channels.all():
        image_stack = []
        for image in self.images.filter(channel=channel, timepoint=timepoint).order_by('level'):
          image.load()
          image_stack.append(image.array)
        channel_dictionary[channel.name] = np.array(image_stack)

      #create chunks
      chunk = self.chunks.create(id_token=generate_id_token(Bulk))
      for channel in channel_dictionary.keys():


### Image storage ###
class Image(models.Model):
  '''
  Stores original details about the images from which chunk objects are derived.
  An image can be uniquely identified by its full path. This must be checked before creating another image object.

  '''
  #connections
  experiment = models.ForeignKey(Experiment, related_name='images')
  channel = models.ForeignKey(Channel, related_name='images', null=True)
  timepoint = models.ForeignKey(Timepoint, related_name='images', null=True)

  #properties
  path = models.CharField(max_length=255)
  rows = models.IntegerField(default=0)
  columns = models.IntegerField(default=0)
  level = models.IntegerField(default=0)
  array = None

  #methods
  def load(self):
    self.array = imread(self.path)

class CompositeImage(Image):
  #connections
  composite = models.ForeignKey(Composite, related_name='images')

  #properties
  abnormal_sizing = models.BooleanField(default=False)

### Extensible parameters ###
class Parameter(models.Model):
  #connections
  composite = models.ForeignKey(Composite, related_name='parameters')

  #properties
  name = models.CharField(max_length='255')
  mean = models.FloatField(default=0.0)
  max = models.FloatField(default=0.0)

class ParameterInstance(models.Model):
  #connections
  composite = models.ForeignKey(Composite, related_name='parameter_instances')
  parameter = models.ForeignKey(Parameter, related_name='instances')
  chunk = models.ForeignKey(Chunk, related_name='parameter_instances')

  #properties
  value = models.IntegerField(default=0)
  float_value = models.FloatField(default=0.0)
  boolean_value = models.BooleanField(default=False)
