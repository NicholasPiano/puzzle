# woot.apps.cell.models

# django
from django.db import models

# local
from apps.img.models import Experiment, Series
from apps.pix.models import Composite, Channel, Gon

# util

### RECOGNITION STAGE
class CellTrack(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_tracks')
  series = models.ForeignKey(Series, related_name='cell_tracks')

  # properties
  track_id = models.IntegerField(default=0)
  index = models.IntegerField(default=0)

class CellMarker(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_markers')
  series = models.ForeignKey(Series, related_name='cell_markers')
  track = models.ForeignKey(CellTrack, related_name='markers')

  # properties
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  t = models.IntegerField(default=0)

class Mask(models.Model): # cell mask is composite and channel dependent
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

### DATA STAGE #####
class Cell(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cells')
  series = models.ForeignKey(Series, related_name='cells')

  # properties
  cell_id = models.IntegerField(default=0)

  # methods
  def velocities(self):
    pass

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
