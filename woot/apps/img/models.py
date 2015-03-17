# woot.apps.img.models

# django
from django.db import models
from django.utils import timezone as tz

# local
from apps.img.settings import *
from apps.img import algorithms

# util
import os
from scipy.misc import imread, imsave
import numpy as np

###### Models
### Top level structure ###
class Experiment(models.Model):
  # properties
  name = models.CharField(max_length=255)

  # 1. location
  base_path = models.CharField(max_length=255)
  img_path = models.CharField(max_length=255)
  composite_path = models.CharField(max_length=255)
  plot_path = models.CharField(max_length=255)
  track_path = models.CharField(max_length=255)
  out_path = models.CharField(max_length=255)

  # 2. scaling
  xmop = models.FloatField(default=0.0) # microns over pixel ratio
  ymop = models.FloatField(default=0.0)
  zmop = models.FloatField(default=0.0)
  tpf = models.FloatField(default=0.0) # minutes in a frame

  def __str__(self):
    return self.name

  def makedirs(self):
    for path in [self.composite_path, self.plot_path, self.track_path, self.out_path]:
      full_path = os.path.join(self.base_path, path)
      if not os.path.exists(full_path):
        os.makedirs(full_path)

  def gon_id_token(self):
    return generate_id_token(Gon)

class Series(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='series')

  # properties
  name = models.CharField(max_length=255)
  id_token = models.CharField(max_length=8)

  # methods
  def __str__(self):
    return '%s > %s'%(self.experiment.name, self.name)

  def compose(self):
    ''' Make a new composite using all currently available images. Each call will generate a new composite. '''
    # 1. composite
    composite = self.composites.create(experiment=self.experiment, series=self, id_token=generate_id_token(Composite))

    # 2. run through images
    ## Three tasks:
    ## 1. Create channels and frames
    ## 2. Create single bulk with a gon per channel for whole set
    ## 3. Create one bulk for each level slice with image gons.
    print('creating discontinuous coordinates from paths')
    for path in self.paths.all():
      channel, channel_created = self.channels.get_or_create(experiment=self.experiment, composite=composite, name=path.channel)
      if channel_created:
        print('created channel: %d'%path.channel_id)
        channel.index = path.channel_id
        channel.save()

      frame, frame_created = self.frames.get_or_create(experiment=self.experiment, composite=composite, index=path.frame)
      if frame_created:
        print('creating frame: %d'%path.frame)

      level, level_created = self.levels.get_or_create(experiment=self.experiment, composite=composite, index=path.level)
      if level_created:
        print('creating level: %d'%path.level)

    # great bulk for each frame
    for frame in composite.frames.all():
      great_bulk = composite.bulks.create(experiment=self.experiment, series=self, t=frame, great=True)
      for channel in composite.channels.all():
        great_bulk.channels.add(channel)
        channel.bulks.add(great_bulk)
        channel.save()
        great_bulk.save()

        # create gons
        print('creating great gon at t%d, ch-%s'%(frame.index, channel.name))
        great_gon = great_bulk.gons.create(experiment=self.experiment, series=self, composite=composite, t=frame, channel=channel, id_token=generate_id_token(Gon), great=True)
        paths = self.paths.filter(frame=frame.index, channel=channel.name)
        rows, columns = imread(paths[0].url).shape
        great_gon.rows = rows
        great_gon.columns = columns
        great_gon.levels = paths.count()

        great_bulk.rows = rows
        great_bulk.columns = columns
        great_bulk.levels = paths.count()

        for path in paths:
          print('creating gon: t%d, ch-%s, %s' % (frame.index, channel.name, path.url))
          # create one gon for each image and add each path to the great gon
          gon = great_bulk.gons.create(experiment=self.experiment, series=self, composite=composite, t=frame, channel=channel, id_token=generate_id_token(Gon), l=path.level)
          gon.rows = rows
          gon.columns = columns

          # paths
          gon_path = gon.paths.create(experiment=self.experiment, series=self, url=path.url)
          gon.save()
          great_gon.paths.create(experiment=self.experiment, series=self, url=path.url, level=path.level)

        great_gon.save()

      great_bulk.save()

class Composite(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='composites')
  series = models.ForeignKey(Series, related_name='composites')

  # properties
  id_token = models.CharField(max_length=8)

  # methods
  def get_max_channel_index(self):
    return max([channel.index for channel in self.channels.all()])

  def get_max_frame_index(self):
    return max([frame.index for frame in self.frames.all()])

### Discontinuous coordinates ###
class Channel(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='channels')
  series = models.ForeignKey(Series, related_name='channels')
  composite = models.ForeignKey(Composite, related_name='channels')

  # properties
  name = models.CharField(max_length='255')
  index = models.IntegerField(default=0)

class Frame(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='frames')
  series = models.ForeignKey(Series, related_name='frames')
  composite = models.ForeignKey(Composite, related_name='frames')

  # properties
  index = models.IntegerField(default=0)
  next = models.IntegerField(default=-1)
  previous = models.IntegerField(default=-1)

  # methods
  def __str__(self):
    max_frame = self.composite.get_max_frame_index()
    max_digits = len(str(max_frame))
    digits = len(str(self.index))
    return str('0'*(max_digits-digits) + str(self.index))

class Level(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='levels')
  series = models.ForeignKey(Series, related_name='levels')
  composite = models.ForeignKey(Composite, related_name='levels')

  # properties
  index = models.IntegerField(default=0)
  next = models.IntegerField(default=-1)
  previous = models.IntegerField(default=-1)

### Cells ###
class Cell(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cells')
  series = models.ForeignKey(Series, related_name='cells')
  composite = models.ForeignKey(Composite, related_name='cells')

  # properties
  id_token = models.CharField(max_length=8)

class CellInstance(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_instances')
  series = models.ForeignKey(Series, related_name='cell_instances')
  composite = models.ForeignKey(Composite, related_name='cell_instances')
  cell = models.ForeignKey(Cell, related_name='cell_instances')

  # properties
  # 1. id
  id_token = models.CharField(max_length=8)

  # 2. origin
  t = models.ForeignKey(Frame, related_name='cell_instances')
  r = models.IntegerField(default=0) # center coordinates
  c = models.IntegerField(default=0)
  l = models.ForeignKey(Level, related_name='cell_instances')

  # 3. dimensions
  rows = models.IntegerField(default=1)
  columns = models.IntegerField(default=1)
  levels = models.IntegerField(default=1)
  area = models.FloatField(default=0.0)
  volume = models.FloatField(default=0.0)

  # 4. movement
  rpt = models.FloatField(default=0.0)
  cpt = models.FloatField(default=0.0)
  lpt = models.FloatField(default=0.0)

  # methods
  def __str__(self):
    return '%d %d: [%d %d %d]'%(self.cell.pk, self.pk, self.r, self.c, self.l)

class CellTrack(models.Model):
  '''
  A way of associating individual cell markers in a series that is separate from a cell.
  '''
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_tracks')
  series = models.ForeignKey(Series, related_name='cell_tracks')
  cell = models.ForeignKey(Cell, related_name='cell_tracks', null=True)

  # properties
  # 1. id
  id_token = models.CharField(max_length=8)
  filename = models.CharField(max_length=255)

class CellMarker(models.Model):
  '''
  The result of manual tracking. Markers are assigned to cell instances when segmenting a track.
  '''

  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_markers')
  series = models.ForeignKey(Series, related_name='cell_markers')
  cell = models.ForeignKey(Cell, related_name='cell_markers', null=True)
  cell_instance = models.ForeignKey(CellInstance, related_name='cell_markers', null=True)
  cell_track = models.ForeignKey(CellTrack, related_name='cell_markers')

  # properties
  line = models.IntegerField(default=0)
  t = models.ForeignKey(Frame, related_name='cell_markers')
  r = models.IntegerField(default=0) # center coordinates
  c = models.IntegerField(default=0)

  # methods
  def __str__(self):
    return '%d %d: [%d %d %d]'%(self.cell.pk, self.cell_instance.pk, self.r, self.c, self.l)

### Bulk pixel objects ###
class Bulk(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='bulks')
  series = models.ForeignKey(Series, related_name='bulks')
  composite = models.ForeignKey(Composite, related_name='bulks')
  channels = models.ManyToManyField(Channel, related_name='bulks')
  cell_instances = models.ManyToManyField(CellInstance, related_name='bulks')
  bulk = models.ForeignKey('self', related_name='bulks', null=True)

  # properties
  great = models.BooleanField(default=False) # represents entire extent of parent

  # 1. origin
  t = models.ForeignKey(Frame, related_name='bulks')
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  l = models.IntegerField(default=0)

  # 2. dimensions
  rows = models.IntegerField(default=1)
  columns = models.IntegerField(default=1)
  levels = models.IntegerField(default=1)

class Gon(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='gons')
  series = models.ForeignKey(Series, related_name='gons')
  composite = models.ForeignKey(Composite, related_name='gons')
  channel = models.ForeignKey(Channel, related_name='gons')
  bulk = models.ForeignKey(Bulk, related_name='gons')

  # properties
  great = models.BooleanField(default=False) # represents entire extent of parent

  # 1. identification
  id_token = models.CharField(max_length=8)

  # 2. origin
  t = models.ForeignKey(Frame, related_name='gons')
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  l = models.IntegerField(default=0)

  # 3. dimensions
  rows = models.IntegerField(default=1)
  columns = models.IntegerField(default=1)
  levels = models.IntegerField(default=1)

  # 4. data
  array = None

  # methods
  def shape(self):
    return (self.rows, self.columns, self.levels)

  def load(self):
    self.array = []
    for path in self.paths.order_by('level'):
      array = imread(path.url)
      self.array.append(array)
    self.array = np.dstack(self.array).squeeze() # remove unnecessary dimensions
    return self.array

  def split(self, id_token):
    ''' Take a multi-leveled gon and split into levels '''
    if self.paths.count()==0 and self.great and self.array is not None:
      for level in range(self.levels):
        print('saving level %d' % level)

        # get array
        plane = np.array(self.array[:,:,level])

        # make gon
        gon = self.bulk.gons.create(experiment=self.experiment, series=self.series, composite=self.composite, channel=self.channel, id_token=generate_id_token(Gon), t=self.t, l=self.l, rows=self.rows, columns=self.columns)

        # make path
        img_url = os.path.join(self.experiment.base_path, self.experiment.composite_path, composite_img_reverse % (self.experiment.name, self.series.name, self.channel.name, str(self.t), str(level), id_token))

        # make path object
        self.paths.create(experiment=self.experiment, series=self.series, url=img_url, channel=self.channel.name, frame=self.t.index, level=self.l)
        gon.paths.create(experiment=self.experiment, series=self.series, url=img_url, channel=self.channel.name, channel_id=self.channel.index, frame=self.t.index, level=level)

        # save image
        imsave(img_url, plane)

### Path objects
class Path(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='paths')
  series = models.ForeignKey(Series, related_name='paths')
  gon = models.ForeignKey(Gon, related_name='paths', null=True)

  # properties
  url = models.CharField(max_length=255)
  channel = models.CharField(max_length=255)
  channel_id = models.IntegerField(default=0)
  frame = models.IntegerField(default=0)
  level = models.IntegerField(default=0)

### Extensible parameters ###
class Parameter(models.Model):
  # connections
  channel = models.ForeignKey(Channel, related_name='instances')
  bulk = models.ForeignKey(Bulk, related_name='parameters', null=True)
  gon = models.ForeignKey(Gon, related_name='parameters')

  # properties
  name = models.CharField(max_length=255)
  value = models.FloatField(default=0.0)

### Mod objects
class Mod(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='mods')
  series = models.ForeignKey(Series, related_name='mods')
  composite = models.ForeignKey(Composite, related_name='mods')

  # properties
  id_token = models.CharField(max_length=255)
  date_created = models.DateTimeField(auto_now_add=True)
  algorithm = models.CharField(max_length=255)

  # methods
  def run(self):
    ''' Runs associated algorithm to produce a new channel. '''
    algorithm = getattr(algorithms, self.algorithm)

    algorithm(self.composite, self.id_token)
