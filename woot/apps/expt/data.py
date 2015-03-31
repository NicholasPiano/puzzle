# apps.img.data

'''
Specific experiment and series information in the form of lists of prototype objects
'''
import os

### Classes
class _Experiment():
  def __init__(self, name, rmop, cmop, zmop, tpf):
    self.name = name
    self.rmop = rmop
    self.cmop = cmop
    self.zmop = zmop
    self.tpf = tpf

class _Series():
  def __init__(self, experiment_name, name):
    self.experiment_name = experiment_name
    self.name = name

### Data
experiments = [
  _Experiment(name='050714', rmop=0.5369, cmop=0.5369, zmop=1.482, tpf=10.7003),
  _Experiment(name='050714-test', rmop=0.5369, cmop=0.5369, zmop=1.482, tpf=10.7003),
  _Experiment(name='190714', rmop=0.501, cmop=0.5015, zmop=1.482, tpf=9.7408),
  _Experiment(name='260714', rmop=0.5696074, cmop=0.5701647, zmop=1.482, tpf=7.6807),
]

series = [
  # 050714
  _Series(experiment_name='050714', name='13'),

  # 050714-test
  _Series(experiment_name='050714-test', name='13'),

  # 190714
  _Series(experiment_name='190714', name='12'),

  # 260714
  _Series(experiment_name='260714', name='12'),
  _Series(experiment_name='260714', name='13'),
  _Series(experiment_name='260714', name='14'),
  _Series(experiment_name='260714', name='15'),
]

### Image file extensions
allowed_img_extensions = (
  '.tiff',
)

allowed_data_extensions = (
  '.csv',
  '.xls',
)

### image filename templates
templates = {
  'source':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>(?P<channel_base>[a-z0-9]+)(?P<channel_suffix>-(?P<composite_id>[0-9A-Z]+)-(?P<mod>[a-z]+)-(?P<mod_id>[0-9A-Z]+)){0,1})_t(?P<t>[0-9]+)_z(?P<z>[0-9]+)\.(?P<extension>.+)$',
    'rv':r'%s_s%s_ch%s_t%s_z%s.tiff',
  },
  'mask':{
    'rx':r'^(?P<id_token>[A-Z0-9]{8})\.(?P<extension>.+)$',
    'rv':r'%s.tiff',
  },
  'track':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_(?P<index>[0-9]+)\.(?P<extension>.+)$',
    'rv':r'%s_s%s_%s.xls',
  },
  'measure':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_(?P<index>[0-9]+)\.(?P<extension>.+)$',
    'rv':r'%s_s%s_%s.csv',
  }
}

### Default paths
default_paths = {
  'img':'img/storage/',
  'composite':'img/composite/',
  'cp':'cp/',
  'plot':'plot/',
  'track':'track/',
  'output':'output/',
  'mask':'img/mask/',
}
