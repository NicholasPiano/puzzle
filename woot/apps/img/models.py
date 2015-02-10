#woot.apps.img.models

#django
from django.db import models
from django.utils import timezone as tz

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
  name = models.CharField(max_length=255)

  #1. location
  base_path = models.CharField(max_length=255)
  composite_path = models.CharField(max_length=255)

  #2. scaling
  xmop = models.FloatField(default=0.0) #microns over pixel ratio
  ymop = models.FloatField(default=0.0)
  zmop = models.FloatField(default=0.0)
  tpf = models.FloatField(default=0.0) #minutes in a timepoint

class Composite(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='composites')

  #properties
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
  composite = models.ForeignKey(Composite, related_name='timepoints')

  #properties
  index = models.IntegerField(default=0)
  next = models.IntegerField(default=-1)
  previous = models.IntegerField(default=-1)

### Cells ###
class Cell(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='cells')
  composite = models.ForeignKey(Composite, related_name='cells')

  #properties
  #1. id
  id_token = models.CharField(max_length=8)

class CellInstance(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='cell_instances')
  composite = models.ForeignKey(Composite, related_name='cell_instances')
  cell = models.ForeignKey(Cell, related_name='cell_instances')

  #properties
  #1. id
  id_token = models.CharField(max_length=8)

  #2. origin
  t = models.ForeignKey(Timepoint, related_name='cell_instances')
  r = models.IntegerField(default=0) #center coordinates
  c = models.IntegerField(default=0)
  l = models.IntegerField(default=0)

  #3. dimensions
  rows = models.IntegerField(default=1)
  columns = models.IntegerField(default=1)
  levels = models.IntegerField(default=1)
  area = models.FloatField(default=0.0)
  volume = models.FloatField(default=0.0)

  #4. movement
  rpt = models.FloatField(default=0.0)
  cpt = models.FloatField(default=0.0)
  lpt = models.FloatField(default=0.0)

### Bulk pixel objects ###
class Bulk(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='bulks')
  composite = models.ForeignKey(Composite, related_name='bulks')
  channels = models.ManyToManyField(Channel, related_name='bulks')
  cell_instance = models.ForeignKey(CellInstance, related_name='bulks', null=True)
  bulk = models.ForeignKey('self', related_name='bulks', null=True)

  #properties
  #1. origin
  t = models.ForeignKey(Timepoint, related_name='bulks')
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  l = models.IntegerField(default=0)

  #2. dimensions
  rows = models.IntegerField(default=1)
  columns = models.IntegerField(default=1)
  levels = models.IntegerField(default=1)

class Gon(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='gons')
  composite = models.ForeignKey(Composite, related_name='gons')
  channel = models.ForeignKey(Channel, related_name='gons')
  bulk = models.ForeignKey(Bulk, related_name='gons')

  #properties
  #1. identification
  id_token = models.CharField(max_length=8)

  #2. origin
  t = models.ForeignKey(Timepoint, related_name='gons')
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  l = models.IntegerField(default=0)

  #3. dimensions
  rows = models.IntegerField(default=1)
  columns = models.IntegerField(default=1)
  levels = models.IntegerField(default=1)

  #4. data
  array = None

### Path objects
class Path(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='paths')
  gon = models.ForeignKey(Gon, related_name='paths', null=True)

  #properties
  url = models.CharField(max_length=255)
  channel = models.CharField(max_length=255)
  channel_id = models.IntegerField(default=0)
  timepoint = models.IntegerField(default=0)
  level = models.IntegerField(default=0)

### Extensible parameters ###
class Parameter(models.Model):
  #connections
  channel = models.ForeignKey(Channel, related_name='instances')
  bulk = models.ForeignKey(Bulk, related_name='parameters', null=True)
  gon = models.ForeignKey(Gon, related_name='parameters')

  #properties
  name = models.CharField(max_length='255')
  value = models.FloatField(default=0.0)
