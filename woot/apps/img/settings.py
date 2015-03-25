# woot.apps.img.settings

''' Settings specific to the img app. '''

import random
import string

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
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>.+)_t(?P<t>[0-9]+)_z(?P<z>.+)\.(?P<extension>.+)$',
    'rv':r'%s_s%s_ch-%s_t%s_z%s.tiff',
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
