# woot.apps.cell.models

# django
from django.db import models

# local
from apps.expt.models import Experiment, Series, Region
from apps.img.models import Composite, Channel, Gon
from apps.img.util import *

# util
import numpy as np
from scipy.ndimage.morphology import binary_dilation as dilate
from scipy.signal import find_peaks_cwt as find_peaks
import matplotlib.pyplot as plt

### Models
### REALITY
class Cell(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cells')
  series = models.ForeignKey(Series, related_name='cells')

  # properties
  cell_id = models.IntegerField(default=0)
  cell_index = models.IntegerField(default=0)

  # methods

class CellInstance(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_instances')
  series = models.ForeignKey(Series, related_name='cell_instances')
  cell = models.ForeignKey(Cell, related_name='cell_instances')
  region = models.ForeignKey(Region, related_name='cell_instances', null=True)

  # properties
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
  t = models.IntegerField(default=0)

  a = models.IntegerField(default=0)

  vr = models.IntegerField(default=0)
  vc = models.IntegerField(default=0)
  vz = models.IntegerField(default=0)

  # methods

### MARKERS
class Track(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='tracks')
  series = models.ForeignKey(Series, related_name='tracks')

  # properties
  track_id = models.IntegerField(default=0)
  index = models.IntegerField(default=0)

  # methods

class Marker(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='markers')
  series = models.ForeignKey(Series, related_name='markers')
  track = models.ForeignKey(Track, related_name='markers')
  region = models.ForeignKey(Region, related_name='markers', null=True)

  # properties
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
  t = models.IntegerField(default=0)

  #- categorisation
  confidence = models.FloatField(default=0.0) # value between -1.0 and 1.0

  # methods

class Mask(models.Model):
  # connections
  composite = models.ForeignKey(Composite, related_name='masks')
  channel = models.ForeignKey(Channel, related_name='masks')
  gon = models.ForeignKey(Gon, related_name='masks')

  # properties
  mask_id = models.IntegerField(default=0)

  # 1. origin
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)

  # 2. extent
  rs = models.IntegerField(default=-1)
  cs = models.IntegerField(default=-1)

  # methods
  def set_origin(self, r, c, z):
    self.r = r
    self.c = c
    self.z = z
    self.save()

  def set_extent(self, rs, cs):
    self.rs = rs
    self.cs = cs
    self.save()
