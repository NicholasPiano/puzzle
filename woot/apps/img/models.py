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
  composite_path = models.CharField(max_length=255)
  plot_path = models.CharField(max_length=255)
  track_path = models.CharField(max_length=255)
  output_path = models.CharField(max_length=255)

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
    self.output_path = os.path.join(self.base_path, default_paths['out'])

    # create directories on file system if they do not exist
    for path in [self.composite_path, self.plot_path, self.track_path, self.output_path]:
      if not os.path.exists(path):
        os.makedirs(path)

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
  id_token = models.CharField(max_length=8)

  # methods
  def __str__(self):
    return '%s > %s'%(self.experiment.name, self.name)

  def prototype(self):
    return filter(lambda x: x.name==self.name and x.experiment_name==self.experiment.name, series)[0]

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

  def get_or_create_path(self, string):
    # metadata
    metadata = self.dict(string)

    # series
    series, series_created = self.experiment.series.get_or_create(name=metadata['series'])
    if series_created:
      series.id_token = generate_id_token(Series)
      series.save()

    # path
    path, created = self.paths.get_or_create(experiment=self.experiment, series=series, url=string)
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
  template = models.ForeignKey(Template, related_name='paths')
  gons = models.ManyToManyField('Gon')

  # properties
  url = models.CharField(max_length=255)
  channel = models.IntegerField(default=0)
  t = models.IntegerField(default=0)
  z = models.IntegerField(default=0)

  # methods
  def __str__(self):
    return '%s: %s' % (self.experiment.name, self.url)

### SECONDARY STRUCTURE #############################################
### Bulk pixel objects ###
class Composite(models.Model):
  '''
  A composite holds a version of a times series. It contains all channels (original and created), frames, and paths from a single series. Many composites of
  one series may exist at one time.
  '''

  # connections
  experiment = models.ForeignKey(Experiment, related_name='composites')
  series = models.ForeignKey(Series, related_name='composites')

  # properties
  id_token = models.CharField(max_length=8)
  max_t = models.IntegerField(default=0)
  max_z = models.IntegerField(default=0)

class Gon(models.Model):
  '''
  A gon is a box of pixels. This may extend over several levels, but contains information unique to a single channel.
  It contain smaller gon instances.
  '''

  # connections
  experiment = models.ForeignKey(Experiment, related_name='gons')
  series = models.ForeignKey(Series, related_name='gons')
  gon = models.ForeignKey('self', related_name='gons')

  # properties
  # 1. origin
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  z = models.IntegerField(default=0)
  t = models.IntegerField(default=0)

  # 2. extent
  rs = models.IntegerField(default=1)
  cs = models.IntegerField(default=1)
  zs = models.IntegerField(default=1)

  # 3. id
  id_token = models.CharField(max_length=8)
  channel = models.CharField(max_length=255)

  # 4. data
  array = None

  # methods
  # 1. get and set
  def shape(self):
    return (self.rs, self.cs, self.zs)

  def load(self):
    self.array = []
    for path in self.paths.order_by('z'):
      array = imread(path.url)
      self.array.append(array)
    self.array = np.dstack(self.array).squeeze() # remove unnecessary dimensions
    return self.array

  def set_location(self, r, c, z, t):
    if self.paths.count()==0: #can only set if the images have not been saved
      self.r = r
      self.c = c
      self.z = z
      self.t = t
      self.save()

  def set_extent(self, rs, cs, zs):
    if self.paths.count()==0: #can only set if the images have not been saved
      self.rs = rs
      self.cs = cs
      self.zs = zs
      self.save()

  def t_str(self):
    return str('0'*(len(str(self.composite.max_t)) - len(str(self.t))) + str(self.t))

  def z_str(self):
    return str('0'*(len(str(self.composite.max_z)) - len(str(self.z))) + str(self.z))

  # 2. saving -> stage 3: segmentation and external processing
  def save_composite_paths(self, mod_id_token, mod_name):
    '''
    Split 'self.array' into as many paths as necessary and save to composite directory.
    Intended for storage.

    '''
    for level in range(self.array.shape[2] if len(self.array.shape)==3 else 0):
      # array
      array = self.array[:,:,level] if len(self.array.shape)==3 else self.array

      # new gon
      gon = self.gons.create(experiment=self.experiment, series=self.series, id_token=generate_id_token('self'), channel=self.channel)

      # origin
      gon.set_location(self.r, self.c, level, self.t)

      # extent
      gon.set_extent(self.rs, self.cs, 1)

      # path
      # path = self.experiment.paths.create(series=self.series, )

      # save

  def save_output_paths(self, mod_id_token, mod_name):
    '''
    Split 'self.array' into as many paths as necessary and save to output directory.
    Intended for external use.

    '''
    pass

class Mod(models.Model):
  '''
  A record of an algorithm used to generate a new channel. Algorithms are stored by the appropriate script, but are called by the mod object.
  '''

  # connections
  experiment = models.ForeignKey(Experiment, related_name='mods')
  series = models.ForeignKey(Series, related_name='mods')

  # properties
  id_token = models.CharField(max_length=8)
  algorithm = models.CharField(max_length=255)
  date_created = models.DateTimeField(auto_now_add=True)

  # methods
  def __str__(self):
    return '%s, %s' % (self.id_token, self.algorithm)

  def run(self):
    ''' Runs associated algorithm to produce a new channel. '''
    algorithm = getattr(algorithms, self.algorithm)

    algorithm(self.composite, self.id_token)
