# woot.apps.img.models

# django
from django.db import models

# local
from apps.img.settings import *
from apps.img.data import experiments, series

# util
import os
import re

###### Models
### TOP LEVEL STRUCTURE #############################################
class Experiment(models.Model):
  # properties
  name = models.CharField(max_length=255)

  # 1. location
  base_path = models.CharField(max_length=255)
  img_path = models.CharField(max_length=255)

  # 2. scaling
  rmop = models.FloatField(default=0.0) # microns over pixel ratio
  cmop = models.FloatField(default=0.0)
  zmop = models.FloatField(default=0.0)
  tpf = models.FloatField(default=0.0) # minutes in a frame

  def __str__(self):
    return self.name

  def make_paths(self, base_path):
    # fetch default paths from settings
    self.base_path = base_path
    self.img_path = os.path.join(self.base_path, default_paths['img'])
    self.save()

  def prototype(self):
    return list(filter(lambda x: x.name==self.name, experiments))[0]

  def get_metadata(self):
    # data
    prototype = self.prototype()
    self.rmop = prototype.rmop
    self.cmop = prototype.cmop
    self.zmop = prototype.zmop
    self.tpf = prototype.tpf

    #templates
    for name, template in templates.items():
      self.templates.create(name=name, rx=template['rx'], rv=template['rv'])

    self.save()

  def allowed_series(self, series_name):
    return (series_name in [s.name for s in filter(lambda x: x.experiment_name==self.name, series)])

  def match_template(self, string):
    return list(filter(lambda x: x.match(string) is not None, self.templates.all()))[0]

class Series(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='series')

  # properties
  name = models.CharField(max_length=255)

  # extent
  rs = models.IntegerField(default=-1)
  cs = models.IntegerField(default=-1)
  zs = models.IntegerField(default=-1)
  ts = models.IntegerField(default=-1)

  # methods
  def __str__(self):
    return '%s > %s'%(self.experiment.name, self.name)

  def prototype(self):
    return filter(lambda x: x.name==self.name and x.experiment_name==self.experiment.name, series)[0]

class Channel(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='channels')
  series = models.ForeignKey(Series, related_name='channels')

  # properties
  name = models.CharField(max_length=255)

class Template(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='templates')

  # properties
  name = models.CharField(max_length=255)
  rx = models.CharField(max_length=255)
  rv = models.CharField(max_length=255)

  # methods
  def __str__(self):
    return '%s: %s' % (self.name, self.rx)

  def match(self, string):
    return re.match(self.rx, string)

  def dict(self, string):
    return self.match(string).groupdict()

  def get_or_create_path(self, root, string):
    # metadata
    metadata = self.dict(string)

    # series
    series, series_created = self.experiment.series.get_or_create(name=metadata['series'])

    # channel
    channel, channel_created = self.experiment.channels.get_or_create(series=series, name=metadata['channel'])

    # path
    path, created = self.paths.get_or_create(experiment=self.experiment, series=series, channel=channel, url=os.path.join(root, string), file_name=string)
    if created:
      path.channel = int(metadata['channel'])
      path.t = int(metadata['frame'])
      path.z=int(metadata['z'])
      path.save()

    return path, created

class Path(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='paths')
  series = models.ForeignKey(Series, related_name='paths')
  channel = models.ForeignKey(Channel, related_name='paths')
  template = models.ForeignKey(Template, related_name='paths')
  gon = models.ForeignKey('Gon', related_name='paths')

  # properties
  url = models.CharField(max_length=255)
  file_name = models.CharField(max_length=255)
  t = models.IntegerField(default=0)
  z = models.IntegerField(default=0)

  # methods
  def __str__(self):
    return '%s: %s' % (self.experiment.name, self.url)

  def load(self):
    return imread(self.url)
