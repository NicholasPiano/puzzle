#woot.apps.img.models

#django
from django.db import models

#local
from apps.img.settings import generate_id_token

#util
import os
from scipy.misc import imread, imsave
import numpy as np

###### Models
### Top level structure ###
class Experiment(models.Model):
  #properties
  #1. location
  path = models.CharField(max_length=255)

  #2. scaling
  xmop = models.FloatField(default=0.0) #microns over pixel ratio
  ymop = models.FloatField(default=0.0)
  zmop = models.FloatField(default=0.0)
  tpf = models.FloatField(default=0.0) #minutes in a timepoint

class Composite(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='composites')

  #properties
  name = models.CharField(max_length=255, default='New composite')
  id_token = models.CharField(max_length=8)

### Discontinuous coordinates ###
class Channel(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='channels')
  composite = models.ForeignKey(Composite, related_name='channels')

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
class Bulk(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='bulks')
  composite = models.ForeignKey(Composite, related_name='bulks')
  channels = models.ManyToManyField(Channel, related_name='bulks')
  timepoint = models.ForeignKey(Timepoint, related_name='bulks')

class Gon(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='gons')
  composite = models.ForeignKey(Composite, related_name='gons')
  channel = models.ForeignKey(Channel, related_name='gons')
  timepoint = models.ForeignKey(Timepoint, related_name='gons')
  bulk = models.ForeignKey(Bulk, related_name='gons')
  gon = models.ForeignKey(Gon, related_name='gons')

  #properties
  #1. identification
  id_token = models.CharField(max_length=8)
  abnormal_sizing = models.BooleanField(default=False)

  #2. size
  rows = models.IntegerField(default=1)
  columns = models.IntegerField(default=1)
  levels = models.IntegerField(default=1)

  #3. origin
  row = models.IntegerField(default=0)
  column = models.IntegerField(default=0)
  level = models.IntegerField(default=0)

  #4. data
  array = None

  #methods
  def load(self):
    array = []
    for path in self.paths.order_by('level'):
      array.append(imread(path))
    self.array = np.array(array)

### Path objects
class Path(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='paths')
  gon = models.ForeignKey(Gon, related_name='paths', null=True)

  #properties
  url = models.CharField(max_length=255)
  level = models.IntegerField(default=0)

### Extensible parameters ###
class Parameter(models.Model):
  #connections
  channel = models.ForeignKey(Channel, related_name='instances')
  bulk = models.ForeignKey(Bulk, related_name='parameters', null=True)
  gon = models.ForeignKey(Gon, related_name='parameters')

  #properties
  name = models.CharField(max_length='255')
  value = models.IntegerField(default=0)
  float_value = models.FloatField(default=0.0)
  boolean_value = models.BooleanField(default=False)
