# woot.apps.img.models

# django
from django.db import models

# local
from apps.img.settings import *
from apps.img.data import experiments, series

# util
import os

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
    self.composite_path = os.path.join(self.base_path, default_paths['composite'])
    self.plot_path = os.path.join(self.base_path, default_paths['plot'])
    self.track_path = os.path.join(self.base_path, default_paths['track'])
    self.out_path = os.path.join(self.base_path, default_paths['out'])

    # create directories on file system if they do not exist
    for path in [self.composite_path, self.plot_path, self.track_path, self.out_path]:
      if not os.path.exists(path):
        os.makedirs(path)

    self.save()

  def prototype(self):
    return list(filter(lambda x: x.name==self.name, experiments))[0]

  def get_metadata(self):
    prototype = self.prototype()
    self.rmop = prototype.rmop
    self.cmop = prototype.cmop
    self.zmop = prototype.zmop
    self.tpf = prototype.tpf
    self.save()

  def allowed_series(self, series_name):
    return (series_name in [s.name for s in filter(lambda x: x.experiment_name==self.name, series)])

class Series(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='series')

  # properties
  name = models.CharField(max_length=255)
  id_token = models.CharField(max_length=8)

  # methods
  def __str__(self):
    return '%s > %s'%(self.experiment.name, self.name)

  def prototype(self):
    return filter(lambda x: x.name==self.name and x.experiment_name==self.experiment.name, series)[0]

### Path objects
class Template(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='path_templates')
  series = models.ForeignKey(Series, related_name='path_templates')

  # properties
  name = models.CharField(max_length=255)
  rx = models.CharField(max_length=255)
  rv = models.CharField(max_length=255)

class Path(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='paths')
  series = models.ForeignKey(Series, related_name='paths')
  template = models.ForeignKey(Template, related_name='paths')

  # properties
  url = models.CharField(max_length=255)
  channel_id = models.IntegerField(default=0)
  frame = models.IntegerField(default=0)
  level = models.IntegerField(default=0)
