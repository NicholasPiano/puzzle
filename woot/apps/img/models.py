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
  pending_composite_creation = models.BooleanField(default=False)

  #1. location
  base_path = models.CharField(max_length=255)
  composite_path = models.CharField(max_length=255)

  #2. scaling
  xmop = models.FloatField(default=0.0) #microns over pixel ratio
  ymop = models.FloatField(default=0.0)
  zmop = models.FloatField(default=0.0)
  tpf = models.FloatField(default=0.0) #minutes in a timepoint

  def __str__(self):
    return self.name

  #methods
  def compose(self):
    ''' Make a new composite using all currently available images. Each call will generate a new composite. '''
    #1. composite
    composite = self.composites.create(id_token=generate_id_token(Composite))

    #2. run through images
    ## Three tasks:
    ## 1. Create channels and timepoints
    ## 2. Create single bulk with a gon per channel for whole set
    ## 3. Create one bulk for each level slice with image gons.
    for path in self.paths.all():
      channel, channel_created = self.channels.get_or_create(composite=composite, name=path.channel)
      if channel_created:
        channel.index = path.channel_id
        channel.save()

      timepoint, timepoint_created = self.timepoints.get_or_create(composite=composite, index=path.timepoint)

    # great bulk for each timepoint
    for timepoint in composite.timepoints.all():
      great_bulk = composite.bulks.create(experiment=self, t=timepoint, great=True)
      for channel in composite.channels.all():
        great_bulk.channels.add(channel)
        channel.bulks.add(great_bulk)
        channel.save()
        great_bulk.save()

        #create gons
        print('creating great gon at t%d, ch-%s'%(timepoint.index, channel.name))
        great_gon = great_bulk.gons.create(experiment=self, composite=composite, t=timepoint, channel=channel, id_token=generate_id_token(Gon), great=True)
        paths = self.paths.filter(timepoint=timepoint.index, channel=channel.name)
        rows, columns = imread(paths[0].url).shape
        great_gon.rows = rows
        great_gon.columns = columns
        great_gon.levels = paths.count()

        great_bulk.rows = rows
        great_bulk.columns = columns
        great_bulk.levels = paths.count()

        for path in paths:
          print('creating gon: t%d, ch-%s, %s' % (timepoint.index, channel.name, path.url))
          #create one gon for each image and add each path to the great gon
          gon = great_bulk.gons.create(experiment=self, composite=composite, t=timepoint, channel=channel, id_token=generate_id_token(Gon), l=path.level)
          gon.rows = rows
          gon.columns = columns

          #paths
          gon_path = gon.paths.create(experiment=self, url=path.url)
          gon.save()
          great_gon.paths.create(experiment=self, url=path.url, level=path.level)

        great_gon.save()

      great_bulk.save()

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
  great = models.BooleanField(default=False) #represents entire extent of parent

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
  great = models.BooleanField(default=False) #represents entire extent of parent

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
