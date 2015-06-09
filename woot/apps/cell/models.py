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
  def calculate_velocities(self):
    previous_cell_instance = None
    for cell_instance in self.cell_instances.order_by('t'):
      if previous_cell_instance is None:
        cell_instance.vr = 0
        cell_instance.vc = 0
        cell_instance.vz = 0
      else:
        cell_instance.vr = cell_instance.r - previous_cell_instance.r
        cell_instance.vc = cell_instance.c - previous_cell_instance.c
        cell_instance.vz = cell_instance.z - previous_cell_instance.z

      cell_instance.save()
      previous_cell_instance = cell_instance

class CellInstance(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_instances')
  series = models.ForeignKey(Series, related_name='cell_instances')
  cell = models.ForeignKey(Cell, related_name='cell_instances')
  region = models.ForeignKey(Region, related_name='cell_instances', null=True)
  gon = models.OneToOneField(Gon, related_name='cell_instance', null=True)

  # properties
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
  t = models.IntegerField(default=0)

  vr = models.IntegerField(default=0)
  vc = models.IntegerField(default=0)
  vz = models.IntegerField(default=0)

  # 4. cell profiler
  AreaShape_Area = models.IntegerField(default=0)
  AreaShape_Compactness = models.FloatField(default=0.0)
  AreaShape_Eccentricity = models.FloatField(default=0.0)
  AreaShape_EulerNumber = models.FloatField(default=0.0)
  AreaShape_Extent = models.FloatField(default=0.0)
  AreaShape_FormFactor = models.FloatField(default=0.0)
  AreaShape_MajorAxisLength = models.FloatField(default=0.0)
  AreaShape_MaximumRadius = models.FloatField(default=0.0)
  AreaShape_MeanRadius = models.FloatField(default=0.0)
  AreaShape_MedianRadius = models.FloatField(default=0.0)
  AreaShape_MinorAxisLength = models.FloatField(default=0.0)
  AreaShape_Orientation = models.FloatField(default=0.0)
  AreaShape_Perimeter = models.FloatField(default=0.0)
  AreaShape_Solidity = models.FloatField(default=0.0)
  Location_Center_X = models.FloatField(default=0.0)
  Location_Center_Y = models.FloatField(default=0.0)

  # methods
  def R(self):
    return self.r*self.experiment.rmop

  def C(self):
    return self.c*self.experiment.cmop

  def Z(self):
    return self.z*self.experiment.zmop

  def T(self):
    return self.t*self.experiment.tpf

  def V(self):
    return np.sqrt(self.VR()**2 + self.VC()**2)

  def VR(self):
    return self.vr*self.experiment.rmop / self.experiment.tpf

  def VC(self):
    return self.vc*self.experiment.cmop / self.experiment.tpf

  def VZ(self):
    return self.vz*self.experiment.zmop / self.experiment.tpf

  def A(self):
    return self.AreaShape_Area*self.experiment.rmop*self.experiment.cmop

  def raw_line(self):
    return '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{} \n'.format(self.experiment.name,
                                                                                                  self.series.name,
                                                                                                  self.cell.pk,
                                                                                                  self.r,
                                                                                                  self.c,
                                                                                                  self.z,
                                                                                                  self.t,
                                                                                                  self.vr,
                                                                                                  self.vc,
                                                                                                  self.vz,
                                                                                                  self.region.index,
                                                                                                  self.AreaShape_Area,
                                                                                                  self.AreaShape_Compactness,
                                                                                                  self.AreaShape_Eccentricity,
                                                                                                  self.AreaShape_EulerNumber,
                                                                                                  self.AreaShape_Extent,
                                                                                                  self.AreaShape_FormFactor,
                                                                                                  self.AreaShape_MajorAxisLength,
                                                                                                  self.AreaShape_MaximumRadius,
                                                                                                  self.AreaShape_MeanRadius,
                                                                                                  self.AreaShape_MedianRadius,
                                                                                                  self.AreaShape_MinorAxisLength,
                                                                                                  self.AreaShape_Orientation,
                                                                                                  self.AreaShape_Perimeter,
                                                                                                  self.AreaShape_Solidity)
  def line(self):
    return '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(self.experiment.name,
                                                                                                    self.series.name,
                                                                                                    self.cell.pk,
                                                                                                    self.R(),
                                                                                                    self.C(),
                                                                                                    self.Z(),
                                                                                                    self.t,
                                                                                                    self.T(),
                                                                                                    self.VR(),
                                                                                                    self.VC(),
                                                                                                    self.VZ(),
                                                                                                    self.region.index,
                                                                                                    self.A(),
                                                                                                    self.AreaShape_Compactness,
                                                                                                    self.AreaShape_Eccentricity,
                                                                                                    self.AreaShape_EulerNumber,
                                                                                                    self.AreaShape_Extent,
                                                                                                    self.AreaShape_FormFactor,
                                                                                                    self.AreaShape_MajorAxisLength,
                                                                                                    self.AreaShape_MaximumRadius,
                                                                                                    self.AreaShape_MeanRadius,
                                                                                                    self.AreaShape_MedianRadius,
                                                                                                    self.AreaShape_MinorAxisLength,
                                                                                                    self.AreaShape_Orientation,
                                                                                                    self.AreaShape_Perimeter,
                                                                                                    self.AreaShape_Solidity)

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
  gon = models.OneToOneField(Gon, related_name='marker', null=True)

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

  # 3. gfp
  max_z = models.IntegerField(default=0)
  mean = models.FloatField(default=0.0)
  std = models.FloatField(default=0.0)

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

  def set_gfp(self, max_z, mean, std):
    self.max_z = max_z
    self.mean = mean
    self.std = std
    self.save()
