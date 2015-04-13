# woot.apps.img.models

# django
from django.db import models

# local
from apps.expt.models import Experiment, Series
from apps.expt.util import generate_id_token
from apps.img import algorithms

# util
import os
import re
from scipy.misc import imread, imsave
import numpy as np

### Models
class Composite(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='composites')
  series = models.ForeignKey(Series, related_name='composites')

  # properties
  id_token = models.CharField(max_length=8)

  # methods
  def __str__(self):
    return '%s, %s > %s' % (self.experiment.name, self.series.name, self.id_token)

class Gon(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='gons')
  series = models.ForeignKey(Series, related_name='gons')
  composite = models.ForeignKey(Composite, related_name='gons', null=True)
  channel = models.ForeignKey('Channel', related_name='gons')
  gon = models.ForeignKey('self', related_name='gons', null=True)

  # properties
  id_token = models.CharField(max_length=8, default='')

  # 1. origin
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
  t = models.IntegerField(default=-1)

  # 2. extent
  rs = models.IntegerField(default=-1)
  cs = models.IntegerField(default=-1)
  zs = models.IntegerField(default=1)

  # 3. data
  array = None

  # methods
  def __str__(self):
    return '%s > (%s, %d, %d, %d, %d),(%d, %d, %d)' % (self.composite.id_token, self.channel.name, self.r, self.c ,self.z, self.t, self.rs, self.cs, self.zs)

  def set_origin(self, r, c, z, t):
    self.r = r
    self.c = c
    self.z = z
    self.t = t
    self.save()

  def set_extent(self, rs, cs, zs):
    self.rs = rs
    self.cs = cs
    self.zs = zs
    self.save()

  def shape(self):
    if self.zs==1:
      return (self.rs, self.cs)
    else:
      return (self.rs, self.cs, self.zs)

  def t_str(self):
    return str('0'*(len(str(self.series.ts)) - len(str(self.t))) + str(self.t))

  def z_str(self, z=None):
    return str('0'*(len(str(self.series.zs)) - len(str(self.z if z is None else z))) + str(self.z if z is None else z))

  def load(self):
    self.array = []
    for path in self.paths.order_by('z'):
      array = imread(path.url)
      self.array.append(array)
    self.array = np.dstack(self.array).squeeze() # remove unnecessary dimensions
    return self.array

  def save_paths(self, url, template):
    if self.array is not None and len(self.array.shape)==3:
      for z in range(self.zs):
        # array
        array = self.array[:,:,z]

        # path
        path_url = url % (self.experiment.name, self.series.name, self.channel.name, self.t_str(), self.z_str(z))
        file_name = template.rv % (self.experiment.name, self.series.name, self.channel.name, self.t_str(), self.z_str(z))
        self.paths.create(composite=self.composite, channel=self.channel, template=template, url=path_url, file_name=file_name, t=self.t, z=z)

        # save
        imsave(path_url, array)

  def save_single(self, url, template, z):
    if self.array is not None:

      # path
      path_url = url % (self.experiment.name, self.series.name, self.channel.name, self.t_str(), self.z_str(z))
      file_name = template.rv % (self.experiment.name, self.series.name, self.channel.name, self.t_str(), self.z_str(z))
      self.paths.create(composite=self.composite, channel=self.channel, template=template, url=path_url, file_name=file_name, t=self.t, z=z)

      # save
      imsave(path_url, self.array)

  def split(self):
    ''' If the gon is 3D, make 2D slices into gons. '''

    if self.zs>1 and self.gons.count()==0:
      for path in self.paths.all():
        # gon
        gon = self.gons.create(experiment=self.experiment, series=self.series, channel=self.channel)
        gon.set_origin(0,0,path.z,path.t)
        gon.set_extent(self.rs, self.cs, 1)
        gon.paths.create(composite=path.composite, channel=path.channel, template=path.template, url=path.url, file_name=path.file_name, t=path.t, z=path.z)

  def duplicate(self):
    ''' If the gon is 2D, make a 3D gon with paths along with 2D slices. '''
    pass

class Channel(models.Model):
  # connections
  composite = models.ForeignKey(Composite, related_name='channels')

  # properties
  name = models.CharField(max_length=255)

  # methods
  def __str__(self):
    return '%s > %s' % (self.composite.id_token, self.name)

  def masks_overlap_with_marker(self, marker):
    box_overlap = []
    for mask in self.masks.filter(gon__t=marker.t):
      if mask.box_overlaps_marker(marker):
        box_overlap.append(mask)

    mask_overlap = []
    for mask in box_overlap:
      if mask.self_overlaps_marker(marker):
        mask_overlap.append(mask)

    return mask_overlap

  def masks_overlap_with_mask(self, query_mask):
    box_overlap = []
    for mask in self.masks.filter(gon__t=query_mask.gon.t):
      if mask.box_overlaps_box(query_mask):
        box_overlap.append(mask)

    mask_overlap = []
    for mask in box_overlap:
      if mask.self_overlaps_mask(query_mask):
        mask_overlap.append(mask)

    print('channel: %s - boxes: %d/%d, masks: %d/%d' % (str(self), len(box_overlap), self.masks.filter(gon__t=query_mask.gon.t).count(), len(mask_overlap), len(box_overlap)))

    return mask_overlap

class Template(models.Model):
  # connections
  composite = models.ForeignKey(Composite, related_name='templates')

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

class Path(models.Model):
  # connections
  composite = models.ForeignKey(Composite, related_name='paths')
  gon = models.ForeignKey(Gon, related_name='paths')
  channel = models.ForeignKey(Channel, related_name='paths')
  template = models.ForeignKey(Template, related_name='paths')

  # properties
  url = models.CharField(max_length=255)
  file_name = models.CharField(max_length=255)
  t = models.IntegerField(default=0)
  z = models.IntegerField(default=0)

  # methods
  def __str__(self):
    return '%s: %s' % (self.composite.id_token, self.file_name)

  def load(self):
    return imread(self.url)

class Mod(models.Model):
  # connections
  composite = models.ForeignKey(Composite, related_name='mods')

  # properties
  id_token = models.CharField(max_length=8)
  algorithm = models.CharField(max_length=255)
  date_created = models.DateTimeField(auto_now_add=True)

  # methods
  def run(self):
    ''' Runs associated algorithm to produce a new channel. '''
    algorithm = getattr(algorithms, self.algorithm)

    algorithm(self.composite, self.id_token, self.algorithm)
