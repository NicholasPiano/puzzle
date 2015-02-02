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
  path = models.CharField(max_length=255)
  composite_path = models.CharField(max_length=255)

  #2. scaling
  xmop = models.FloatField(default=0.0) #microns over pixel ratio
  ymop = models.FloatField(default=0.0)
  zmop = models.FloatField(default=0.0)
  tpf = models.FloatField(default=0.0) #minutes in a timepoint

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
      great_bulk = composite.bulks.create(experiment=self, timepoint=timepoint, great=True)
      for channel in composite.channels.all():
        great_bulk.channels.add(channel)
        channel.bulks.add(great_bulk)
        channel.save()
        great_bulk.save()

        #create gons
        print('creating great gon at t%d, ch-%s'%(timepoint.index, channel.name))
        great_gon = great_bulk.gons.create(experiment=self, composite=composite, timepoint=timepoint, channel=channel, id_token=generate_id_token(Gon), great=True)
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
          gon = great_bulk.gons.create(experiment=self, composite=composite, timepoint=timepoint, channel=channel, id_token=generate_id_token(Gon), level=path.level)
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

### Bulk pixel objects ###
class Bulk(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='bulks')
  composite = models.ForeignKey(Composite, related_name='bulks')
  channels = models.ManyToManyField(Channel, related_name='bulks')
  timepoint = models.ForeignKey(Timepoint, related_name='bulks')
  bulk = models.ForeignKey('self', related_name='sub_bulks', null=True)

  #properties
  great = models.BooleanField(default=False) #originally created by composite

  #1. coords
  row = models.IntegerField(default=0)
  column = models.IntegerField(default=0)
  level = models.IntegerField(default=0)
  rows = models.IntegerField(default=1)
  columns = models.IntegerField(default=1)
  levels = models.IntegerField(default=1)

  #methods
  def new_bulk(self, origin=(0,0,0), shape=(8,8,5)):
    ''' Makes a sub bulk given dimensions '''
    if not os.path.exists(self.experiment.composite_path):
      os.mkdir(self.experiment.composite_path)

    print('cutting %d,%d,%d at %d,%d,%d from composite %d of experiment %s' % tuple(shape + origin + tuple([self.composite.pk, self.experiment.name])))
    #coords
    great = shape==(self.rows, self.columns, self.levels)

    #1. load
    sub_bulk = self.sub_bulks.create(experiment=self.experiment, composite=self.composite, timepoint=self.timepoint, great=great)
    sub_bulk.row = origin[0]
    sub_bulk.column = origin[1]
    sub_bulk.level = origin[2]
    sub_bulk.rows = shape[0]
    sub_bulk.columns = shape[1]
    sub_bulk.levels = shape[2]

    for channel in self.channels.all():
      print('cutting channel %s...' % channel.name)
      #add channels
      sub_bulk.channels.add(channel)
      channel.bulks.add(sub_bulk)
      channel.save()
      sub_bulk.save()

    return sub_bulk

  def new_great_gon(self, channel, gon_array):
    #coords
    sub_gon = self.gons.create(experiment=self.experiment, composite=self.composite, channel=channel, timepoint=self.timepoint, id_token=generate_id_token(Gon), great=True)
    sub_gon.row = self.row
    sub_gon.column = self.column
    sub_gon.level = self.level
    sub_gon.rows = self.rows
    sub_gon.columns = self.columns
    sub_gon.levels = self.levels

    #save array
    for level, image in enumerate(np.rollaxis(gon_array, 2)): #down through levels
      path_url = os.path.join(self.experiment.composite_path, '%s_%d.tiff' % (sub_gon.id_token, level))
      sub_gon.paths.create(experiment=self.experiment, url=path_url, level=level)
      print('saving %s...' % path_url)
      imsave(path_url, image)

    sub_gon.save()

  def tile(self, shape=(8,8,5)):
    print('tiling bulk %d from composite %d with shape (%d,%d,%d)...' % tuple((self.pk, self.composite.pk) + shape))
    #1. load great gon from each channel
    print('loading channel gons...')
    channel_gons = {}
    for channel in self.channels.all():
      print('...%s' % channel.name)
      channel_gon = self.gons.get(channel=channel, great=True)
      channel_gon.load()
      channel_gons.update({channel.name:channel_gon.array})

    #2. run a loop that generates a set of coordinates.
    print('tiling...')
    count = 0
    for row in range(0,self.rows,shape[0]):
      for column in range(0,self.columns,shape[1]):
        for level in range(0,self.levels,shape[2]):
          #coords
          row0, row1 = row, row+shape[0]
          column0, column1 = column, column+shape[1]
          level0, level1 = level, level+shape[2]

          #make new bulk
          sub_bulk = self.new_bulk(origin=(row0,column0,level0), shape=shape)

          #make gon for each channel and add to bulk
          for channel in self.channels.all():
            channel_gon = channel_gons[channel.name]
            sub_channel_gon = channel_gon[row0:row1,column0:column1,level0:level1]
            sub_bulk.new_great_gon(channel, sub_channel_gon)

          #save
          sub_bulk.save()

          print([row,column,level,count,tz.now()])
          count += 1

    self.save()

    #3. Give the coordinates to a newly created set of gons.
    #4. Create a bulk from each set of gons.
    #5. Save images and stores paths in gons.

  def standard_parameters(self):
    ''' For all sub_bulks, calculate the mean, max, and median of each channel. Add these as parameters of the bulk. '''
    for sub_bulk in self.sub_bulks.all():
      print('calculating standard parameters for sub_bulk %d with coordinates (%d,%d,%d) in bulk %d, composite %d, experiment %s: %s'%(sub_bulk.pk, self.row, self.column, self.level, self.pk, self.composite.pk, self.experiment.name, str(tz.now())))
      for channel in sub_bulk.channels.all():
        channel_gon = sub_bulk.gons.get(channel=channel, great=True)
        channel_gon.load()

        array = channel_gon.array
        #parameters - add one for each
        for name,function in {'mean':np.mean, 'max':np.max, 'median':np.median}.items():
          value = function(array)
          sub_bulk.parameters.create(channel=channel, gon=channel_gon, name=name, float_value=value)
      sub_bulk.save()

class Gon(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='gons')
  composite = models.ForeignKey(Composite, related_name='gons')
  channel = models.ForeignKey(Channel, related_name='gons')
  timepoint = models.ForeignKey(Timepoint, related_name='gons')
  bulk = models.ForeignKey(Bulk, related_name='gons')

  #properties
  #1. identification
  great = models.BooleanField(default=False) #represents entire volume of bulk
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
    if self.array is None:
      array = []
      for path in self.paths.order_by('level'):
        array.append(imread(path.url))
      self.array = np.transpose(np.array(array), (1,2,0))

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
  value = models.IntegerField(default=0)
  float_value = models.FloatField(default=0.0)
  boolean_value = models.BooleanField(default=False)
