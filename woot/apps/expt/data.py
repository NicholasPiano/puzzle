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
  def __init__(self, experiment, name):
    self.experiment = experiment
    self.name = name

class _Region():
  def __init__(self, experiment, series, name, description, index, vertical_sort_index):
    self.experiment = experiment
    self.series = series
    self.name = name
    self.description = description
    self.index = index
    self.vertical_sort_index = vertical_sort_index

### Data
experiments = (
  _Experiment(name='050714', rmop=0.5369, cmop=0.5369, zmop=1.482, tpf=10.7003),
  _Experiment(name='050714-test', rmop=0.5369, cmop=0.5369, zmop=1.482, tpf=10.7003),
  _Experiment(name='190714', rmop=0.501, cmop=0.5015, zmop=1.482, tpf=9.7408),
  _Experiment(name='260714', rmop=0.5696074, cmop=0.5701647, zmop=1.482, tpf=7.6807),
)

series = (
  # 050714
  _Series(experiment='050714', name='13'),

  # 050714-test
  _Series(experiment='050714-test', name='13'),

  # 190714
  _Series(experiment='190714', name='12'),

  # 260714
  _Series(experiment='260714', name='12'),
  _Series(experiment='260714', name='13'),
  _Series(experiment='260714', name='14'),
  _Series(experiment='260714', name='15'),
)

regions = (
  # 050714
  _Region(experiment='050714', series='13', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='050714', series='13', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='050714', series='13', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='050714', series='13', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

  # 050714-test
  _Region(experiment='050714-test', series='13', name='medium', description='Bottom of the environment in the medium', index=1, vertical_sort_index=4),
  _Region(experiment='050714-test', series='13', name='barrier-edge', description='Within one cell diameter of the barrier', index=2, vertical_sort_index=3),
  _Region(experiment='050714-test', series='13', name='barrier', description='Within the barrier', index=3, vertical_sort_index=2),
  _Region(experiment='050714-test', series='13', name='gel', description='Through the barrier in the gel region', index=4, vertical_sort_index=1),

  # 190714
  # _Region(experiment='', series='', name='', description='', index=, vertical_sort_index=)
  # _Region(experiment='', series='', name='', description='', index=, vertical_sort_index=)
  # _Region(experiment='', series='', name='', description='', index=, vertical_sort_index=)
  # _Region(experiment='', series='', name='', description='', index=, vertical_sort_index=)
)

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
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>.+)_t(?P<t>[0-9]+)_z(?P<z>[0-9]+)\.(?P<extension>.+)$',
    'rv':r'%s_s%s_ch%s_t%s_z%s.tiff',
  },
  'composite':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>(?P<composite_id>[0-9A-Z]+)-(?P<mod>[a-z]+)-(?P<mod_id>[0-9A-Z]+))_t(?P<t>[0-9]+)_z(?P<z>[0-9]+)\.(?P<extension>.+)$',
    'rv':r'%s_s%s_ch-%s_t%s_z%s.tiff',
  }
  'cp':{
    'rx':r'^cp_(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>.+)_t(?P<t>[0-9]+)_z(?P<z>[0-9]+)\.(?P<extension>.+)$',
    'rv':r'cp_%s_s%s_ch%s_t%s_z%s.tiff',
  },
  'region':{
    'rx':r'^region_(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>.+)_t(?P<t>[0-9]+)_z(?P<z>[0-9]+)\.(?P<extension>.+)$',
    'rv':r'region_%s_s%s_ch%s_t%s_z%s.tiff',
  },
  'mask':{
    'rx':r'^(?P<id_token>[A-Z0-9]{8})\.(?P<extension>.+)$',
    'rv':r'%s.tiff',
  },
  'track':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_(?P<index>[0-9]+)\.xls$',
    'rv':r'%s_s%s_%s.xls',
  },
  'measure':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_(?P<index>[0-9]+)\.csv$',
    'rv':r'%s_s%s_%s.csv',
  }
}

### Default paths
default_paths = {
  'img':'img/storage/',
  'tracking':'img/tracking',
  'composite':'img/composite/',
  'cp':'img/cp/',
  'output':'img/output/',
  'mask':'img/mask/',
  'region':'img/region',
  'region_img':'img/region-img',
  'plot':'plot/',
  'track':'track/',
  'data':'data/',
  'pipeline':'pipelines/',
}
