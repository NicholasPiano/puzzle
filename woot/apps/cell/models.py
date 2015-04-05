# woot.apps.cell.models

# django
from django.db import models

# local
from apps.expt.models import Experiment, Series
from apps.img.models import Composite, Channel, Gon

# util

### Models
### REALITY
class Cell(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cells')
  series = models.ForeignKey(Series, related_name='cells')

  # properties
  cell_id = models.IntegerField(default=0)

  # methods
  def velocities(self):
    frames = [ci.t for ci in self.cell_instances.all()]
    for frame in sorted(frames):
      ci = self.cell_instances.get(t=frame)

      prev_ci = self.cell_instances.get(t=(frame-1 if frame>0 else 0))

      ci.vr = ci.r - prev_ci.r
      ci.vc = ci.c - prev_ci.c
      ci.vz = ci.z - prev_ci.z

      ci.save()

class CellInstance(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_instances')
  series = models.ForeignKey(Series, related_name='cell_instances')
  cell = models.ForeignKey(Cell, related_name='cell_instances')

  # properties
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
  t = models.IntegerField(default=0)

  a = models.IntegerField(default=0)
  region = models.IntegerField(default=0)

  vr = models.IntegerField(default=0)
  vc = models.IntegerField(default=0)
  vz = models.IntegerField(default=0)

  def velocity(self):
    return ((self.vr * self.experiment.rmop)**2 + (self.vc * self.experiment.cmop)**2 + (self.vz * self.experiment.zmop)**2)**0.5 / self.experiment.tpf

  def area(self):
    return self.a * self.experiment.rmop * self.experiment.cmop

  def line(self):
    return '%d,%d,%d,%d,%d,%f,%f,%d' % (self.cell.cell_id, self.t * self.experiment.tpf, self.r * self.experiment.rmop, self.c * self.experiment.cmop, self.z * self.experiment.zmop, self.velocity(), self.area(), self.region)

### MARKERS
class Track(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='tracks')
  series = models.ForeignKey(Series, related_name='tracks')

  # properties
  track_id = models.IntegerField(default=0)
  index = models.IntegerField(default=0)

class Marker(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='markers')
  series = models.ForeignKey(Series, related_name='markers')
  track = models.ForeignKey(Track, related_name='markers')

  # properties
  channel = models.CharField(max_length=255)
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
  t = models.IntegerField(default=0)

class Mask(models.Model):
  # connections
  composite = models.ForeignKey(Composite, related_name='masks')
  channel = models.ForeignKey(Channel, related_name='masks')
  gon = models.ForeignKey(Gon, related_name='masks')

  # properties
  mask_id = models.IntegerField(default=0)

  array = None

  def load(self):
    array = self.gon.load()
    array[array!=self.mask_id] = 0
    self.array = array==self.mask_id
    return self.array

class MaskPath(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='mask_paths')
  series = models.ForeignKey(Series, related_name='mask_paths')

  # properties
  url = models.CharField(max_length=255)
  file_name = models.CharField(max_length=255)
  t = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
