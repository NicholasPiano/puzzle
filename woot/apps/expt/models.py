# woot.apps.expt.models

# django
from django.db import models

# local
from apps.expt.data import *

# util


### Models
class Experiment(models.Model):
  # properties
  name = models.CharField(max_length=255)

  # 1. location
  base_path = models.CharField(max_length=255)
  img_path = models.CharField(max_length=255)
  composite_path = models.CharField(max_length=255)
  mask_path = models.CharField(max_length=255)
  cp_path = models.CharField(max_length=255)
  track_path = models.CharField(max_length=255)

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
    self.mask_path = os.path.join(self.base_path, default_paths['mask'])
    self.cp_path = os.path.join(self.base_path, default_paths['cp'])
    self.track_path = os.path.join(self.base_path, default_paths['track'])
    self.save()

    for path in [self.composite_path, self.cp_path, self.track_path, self.mask_path]:
      if not os.path.exists(path):
        os.makedirs(path)

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

  def compose(self):

    # composite
    composite = self.composites.create(experiment=self.experiment, id_token=self.generate_composite_id())

    # templates
    for template in self.experiment.templates.all():
      composite.templates.create(name=template.name, rx=template.rx, rv=template.rv)

    # iterate over paths
    for channel in self.experiment.channels.all():
      composite_channel = composite.channels.create(name=channel.name)

      for t in range(self.ts):

        # path set
        path_set = self.paths.filter(channel=channel, t=t)

        # gon
        gon = self.gons.create(experiment=self.experiment, composite=composite, channel=composite_channel)
        gon.set_origin(0,0,0,t)
        gon.set_extent(self.rs, self.cs, self.zs)

        for z in range(self.zs):
          print('processing %s, %d, %d' % (channel.name, t, z))

          # path
          path = path_set.get(channel=channel, t=t, z=z)
          template = composite.templates.get(name=path.template.name)
          gon.paths.create(composite=composite, channel=composite_channel, template=template, url=path.url, file_name=path.file_name, t=t, z=z)

          # sub gon
          sub_gon = self.gons.create(experiment=self.experiment, gon=gon, channel=composite_channel)
          sub_gon.set_origin(0,0,z,t)
          sub_gon.set_extent(self.rs, self.cs, 1)
          sub_gon.paths.create(composite=composite, channel=composite_channel, template=template, url=path.url, file_name=path.file_name, t=t, z=z)

          sub_gon.save()

        gon.save()

    composite.save()

  def generate_composite_id(self):
    chars = string.ascii_uppercase + string.digits

    def get_id_token():
      return ''.join([random.choice(chars) for _ in range(8)]) #8 character string

    id_token = get_id_token()
    while self.composites.filter(id_token=id_token).count()>0:
      id_token = get_id_token()

    return id_token

class Channel(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='channels')

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
    channel, channel_created = self.experiment.channels.get_or_create(name=metadata['channel'])

    if metadata['channel_suffix']:
      # composite
      composite, composite_created = self.composites.get_or_create(experiment=self.experiment, id_token=metadata['composite_id'])

      # mod
      mod, mod_created = composite.mods.get_or_create(algorithm=metadata['mod'], id_token=metadata['mod_id'])

    # path
    path, created = self.paths.get_or_create(experiment=self.experiment, series=series, channel=channel, url=os.path.join(root, string), file_name=string)
    if created:
      path.t = int(metadata['t'])
      path.z=int(metadata['z'])
      path.save()

    return path, created

class Path(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='paths')
  series = models.ForeignKey(Series, related_name='paths')
  channel = models.ForeignKey(Channel, related_name='paths')
  template = models.ForeignKey(Template, related_name='paths')

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
