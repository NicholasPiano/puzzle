# woot.apps.cell.models

# django
from django.db import models

# local
from apps.expt.models import Experiment, Series
from apps.img.models import Composite, Channel, Gon

# util
import numpy as np
from scipy.ndimage.morphology import binary_dilation as dilate
from scipy.signal import find_peaks_cwt as find_peaks

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
  composite = models.ForeignKey(Composite, related_name='tracks')
  channel = models.ForeignKey(Channel, related_name='tracks')

  # properties
  track_id = models.IntegerField(default=0)
  index = models.IntegerField(default=0)

class Marker(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='markers')
  series = models.ForeignKey(Series, related_name='markers')
  composite = models.ForeignKey(Composite, related_name='markers')
  channel = models.ForeignKey(Channel, related_name='markers')
  track = models.ForeignKey(Track, related_name='markers')

  # properties
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
  t = models.IntegerField(default=0)

  #- categorisation
  confidence = models.FloatField(default=0.0) # value between -1.0 and 1.0

  # methods
  def centre(self):
    return (self.r, self.c)

  def primary_mask_set(self):
    print('getting primary mask set for marker %d' % self.pk)

    # 1. channels
    pmod_mask_channel = self.composite.channels.get(name='pmodreduced')
    bf_mask_channel = self.composite.channels.get(name='bfreduced')
    # bf_mini_mask_channel = self.composite.channels.get(name='bfreducedmini')

    # 2. get masks
    pmod_mask_overlap = pmod_mask_channel.masks_overlap_with_marker(self)
    bf_mask_overlap = bf_mask_channel.masks_overlap_with_marker(self)
    # bf_mini_mask_overlap = bf_mini_mask_channel.masks_overlap_with_marker(self)

    # 3. return complete set
    return pmod_mask_overlap + bf_mask_overlap# + bf_mini_mask_overlap

  def secondary_mask_set(self):

    # 1. primary masks
    primary_mask_set = self.primary_mask_set()

    print('getting secondary mask set for marker %d' % self.pk)

    # 2. get channels
    pmod_mask_channel = self.composite.channels.get(name='pmodreduced')
    bf_mask_channel = self.composite.channels.get(name='bfreduced')
    # bf_mini_mask_channel = self.composite.channels.get(name='bfreducedmini')

    # 3. for each mask, find the list of masks that it overlaps, excluding the ones currently in the primary set
    secondary_mask_set = []
    for i, mask in enumerate(primary_mask_set):
      print('getting secondary masks for %d out of %d masks' % (i+1, len(primary_mask_set)))
      pmod_mask_overlap = pmod_mask_channel.masks_overlap_with_mask(mask)
      bf_mask_overlap = bf_mask_channel.masks_overlap_with_mask(mask)
      # bf_mini_mask_overlap = bf_mini_mask_channel.masks_overlap_with_mask(mask)

      secondary_mask_set += pmod_mask_overlap + bf_mask_overlap# + bf_mini_mask_overlap

      # print('%d/%d - pmod: %d, bf: %d, bf_mini: %d, total: %d' % (i, len(primary_mask_set), len(pmod_mask_overlap), len(bf_mask_overlap), len(bf_mini_mask_overlap), len(pmod_mask_overlap + bf_mask_overlap + bf_mini_mask_overlap)))
      print('%d/%d - pmod: %d, bf: %d, total: %d' % (i, len(primary_mask_set), len(pmod_mask_overlap), len(bf_mask_overlap), len(pmod_mask_overlap + bf_mask_overlap)))

    return secondary_mask_set

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

  # 2. extent
  rs = models.IntegerField(default=-1)
  cs = models.IntegerField(default=-1)

  # methods
  # 1. methods to deal with properties
  def property_dict(self):
    return {p.name:p.value for p in self.properties.all()}

  # 2. load
  def load(self):
    # load gon
    array = self.gon.load()
    return self.from_image(array)

  def from_image(self, image):
    mask = np.zeros(image.shape, dtype=bool)
    mask[image==self.mask_id] = True
    return mask

  # 3. tests
  def box_overlaps_marker(self, marker):
    # box boundaries a0, a1
    # marker coordinate b
    # test a0 < b < a1
    return self.r < marker.r and self.r + self.rs > marker.r and self.c < marker.c and self.c + self.cs > marker.c

  def self_overlaps_marker(self, marker):
    # test marker point is true in loaded mask
    return self.load()[marker.r, marker.c]

  def box_overlaps_box(self, mask):
    # one of the corners of one of the boxes must be within the other box, so test all 8 corners
    edge1 = self.r < mask.r
    edge2 = self.r + self.rs > mask.r + mask.rs
    edge3 = self.c < mask.c
    edge4 = self.c + self.cs > mask.c + mask.cs

    return not edge1 and not edge2 and not edge3 and not edge4

  def self_overlaps_mask(self, mask):
    self_int_array = self.load().astype(int)
    mask_int_array = mask.load().astype(int)

    s = self_int_array + mask_int_array
    return np.any(s==2) # doubled up areas of overlap

  def self_is_adjacent_to_mask(self, mask):
    # test for overlap of dilated masks
    self_dilated_int_array = dilate(self.load().astype(int))
    mask_dilated_int_array = dilate(mask.load().astype(int))

    s = self_int_array + mask_int_array
    return np.any(s==2) # doubled up areas of overlap

  def find_z_from_image(self, image, z_select=None): # image will most likely be smoothed gfp
    # 1. load self
    mask = np.invert(self.load())

    # 2. mask each level and get sum
    intensities = []
    for level in range(image.shape[2]):
      level_array = image[:,:,level]
      masked_level = np.ma.array(level_array, mask=mask, fill_value=0)
      intensities.append(masked_level.sum())

    # 3. get peaks and choose one closest to z_select or return array or return single if array length is 1
    peaks = find_peaks(intensities, np.arange(10,20)) # peaks within a 10-20 vertical pixel range

    if z_select is not None:
      index = np.argmin(np.abs(np.array(peaks) - z_select))
      return [peaks[index]]
    else:
      return peaks

class MaskProperty(models.Model):
  # connections
  mask = models.ForeignKey(Mask, related_name='properties')

  # properties
  name = models.CharField(max_length=255)
  value = models.FloatField(default=0.0)
