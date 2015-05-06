# woot.apps.cell.models

# django
from django.db import models

# local
from apps.expt.models import Experiment, Series
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
    return ((self.vr * self.experiment.rmop)**2 + (self.vc * self.experiment.cmop)**2)**0.5 / self.experiment.tpf

  def area(self):
    return self.a * self.experiment.rmop * self.experiment.cmop

  def line(self):
    return '%d,%d,%d,%d,%d,%f,%f,%d' % (self.cell.cell_id, self.t * self.experiment.tpf, self.r * self.experiment.rmop, self.c * self.experiment.cmop, self.z * self.experiment.zmop, self.velocity(), self.area(), self.region)

  def raw_line(self):
    return '%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n' % (self.cell.cell_id, self.t, self.r, self.c, self.z, self.vr, self.vc, self.vz, self.a, self.region)

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

  def create_cell(self):
    print(self.markers.count())

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

    # 2. get masks
    pmod_mask_overlap = pmod_mask_channel.masks_overlap_with_marker(self)
    bf_mask_overlap = bf_mask_channel.masks_overlap_with_marker(self)

    # 3. return complete set
    return pmod_mask_overlap + bf_mask_overlap

  def secondary_mask_set(self):

    # 1. primary masks
    primary_mask_set = self.primary_mask_set()

    print('getting secondary mask set for marker %d' % self.pk)

    # 2. get channels
    pmod_mask_channel = self.composite.channels.get(name='pmodreduced')
    bf_mask_channel = self.composite.channels.get(name='bfreduced')

    # 3. for each mask, find the list of masks that it overlaps, excluding the ones currently in the primary set
    secondary_mask_set = []
    for i, mask in enumerate(primary_mask_set):
      print('getting secondary masks for %d out of %d masks' % (i+1, len(primary_mask_set)))
      pmod_mask_overlap = pmod_mask_channel.masks_overlap_with_mask(mask)
      bf_mask_overlap = bf_mask_channel.masks_overlap_with_mask(mask)

      secondary_mask_set += pmod_mask_overlap + bf_mask_overlap

      # print('%d/%d - pmod: %d, bf: %d, total: %d' % (i+1, len(primary_mask_set), len(pmod_mask_overlap), len(bf_mask_overlap), len(pmod_mask_overlap + bf_mask_overlap)))

    return secondary_mask_set

  # def combined_mask(self):
  #   # make zeros
  #   black = np.zeros((self.series.rs,self.series.cs), dtype=float)
  #
  #   # add each mask based on its z compared to that of the marker
  #   for mask in self.secondary_mask_set():
  #     black += mask.load().astype(float) * 1.0/(1.0 + abs(self.z - mask.gon.z))
  #
  #   # add marker
  #   black[self.r, self.c] = 1.0
  #
  #   # non-zero mean threshold
  #   black[black<np.ma.array(black, mask=black==0).mean()] = 0
  #
  #   return black

  def combined_mask(self):
    # blank image
    black = np.zeros((self.series.rs,self.series.cs), dtype=float)

    # get bf and pmod from cp
    pmod_mask_set = self.composite.gons.filter(channel__name='pmodreduced', t=self.t)
    bf_mask_set = self.composite.gons.filter(channel__name='bfreduced', t=self.t)

    # iterate through z, loading images
    for z in [pmod.z for pmod in pmod_mask_set.order_by('z')]:

      z_black = np.zeros((self.series.rs,self.series.cs), dtype=float)

      # load images
      pmod = pmod_mask_set.get(z=z)
      p = pmod.load()

      bf = bf_mask_set.get(z=z)
      b = bf.load()

      # loop through masks, get mask id, and overlap marker with box
      for pmod_mask in pmod.masks.all():
        if box_overlaps_marker(pmod_mask, self):
          if mask_overlaps_marker(p==pmod_mask.mask_id, self):
            z_black += 10 * (p==pmod_mask.mask_id).astype(int)

      for bf_mask in bf.masks.all():
        if box_overlaps_marker(bf_mask, self):
          if mask_overlaps_marker(b==bf_mask.mask_id, self):
            z_black += 10 * (b==bf_mask.mask_id).astype(int)

      # add all masks that overlap with new combined mask
      combined_mask = (z_black > 0).copy()

      for pmod_mask in pmod.masks.all():
        if box_overlaps_mask(pmod_mask, combined_mask):
          if mask_overlaps_mask(p==pmod_mask.mask_id, combined_mask):
            z_black += p==pmod_mask.mask_id

      for bf_mask in bf.masks.all():
        if box_overlaps_mask(bf_mask, combined_mask):
          if mask_overlaps_mask(b==bf_mask.mask_id, combined_mask):
            z_black += b==bf_mask.mask_id

      black += z_black

    black[black<nonzero_mean(black)] = 0

    plt.imshow(black)
    plt.show()

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
  # 1. methods to deal with properties
  def property_dict(self):
    return {p.name:p.value for p in self.properties.all()}

  # 2. load
  def load(self):
    # load gon
    array = self.gon.load()
    array = (array / array.max() * (len(np.unique(array))-1)).astype(int) # rescale
    return self.from_image(array)

  def from_image(self, image):
    mask = np.zeros(image.shape, dtype=bool)
    mask[image==self.mask_id] = True
    return mask

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
