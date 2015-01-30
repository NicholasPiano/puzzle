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
  name = models.CharField(max_length=255)
  pending_composite_creation = models.BooleanField(default=False)

  #1. location
  path = models.CharField(max_length=255)

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

  #methods
  def bulkify(self, timepoint_index=None, origin=(0,0,0), shape=(8,8,5)):
    print('cutting %d,%d,%d at %d,%d,%d from composite of experiment %s' % tuple(shape + origin + tuple([self.experiment.name])))
    if timepoint_index is not None:
      #coords
      row0, row1 = (origin[0], origin[0]+shape[0])
      column0, column1 = (origin[1], origin[1]+shape[1])
      level0, level1 = (origin[2], origin[2]+shape[2])

      #1. load great bulk
      great_bulk = self.bulks.get(great=True, timepoint=self.timepoints.get(index=timepoint_index))
      sub_bulk = self.bulks.create(experiment=self.experiment, timepoint=self.timepoints.get(index=timepoint_index))

      #2. load great gons for each channel
      for channel in great_bulk.channels.all():
        print('cutting channel %s...' % channel.name)
        #add channels
        sub_bulk.channels.add(channel)
        channel.bulks.add(sub_bulk)
        channel.save()

        #coords
        sub_gon = sub_bulk.gons.create(experiment=self.experiment, composite=self, channel=channel, timepoint=great_bulk.timepoint, id_token=generate_id_token(Gon))
        sub_gon.row = origin[0]
        sub_gon.column = origin[1]
        sub_gon.level = origin[2]
        sub_gon.rows = shape[0]
        sub_gon.columns = shape[1]
        sub_gon.levels = shape[2]

        #cut array
        great_gon = great_bulk.gons.get(channel=channel, great=True)
        great_gon.load()
        new_array = great_gon.array[row0:row1,column0:column1,level0:level1]

        #save images and create paths
        for level, image in enumerate(np.rollaxis(new_array, 2)): #down through levels
          path_url = self.experiment.path + '%s_%d.tiff' % (sub_gon.id_token, level)
          sub_gon.paths.create(experiment=self.experiment, url=path_url, level=level)
          print('saving %s...' % path_url)
          imsave(path_url, image)

        sub_gon.save()
        print('channel %s done.' % channel.name)

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

  #properties
  great = models.BooleanField(default=False)

class Gon(models.Model):
  #connections
  experiment = models.ForeignKey(Experiment, related_name='gons')
  composite = models.ForeignKey(Composite, related_name='gons')
  channel = models.ForeignKey(Channel, related_name='gons')
  timepoint = models.ForeignKey(Timepoint, related_name='gons')
  bulk = models.ForeignKey(Bulk, related_name='gons')

  #properties
  #1. identification
  great = models.BooleanField(default=False)
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
