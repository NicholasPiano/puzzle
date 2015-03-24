# woot.apps.img.settings

''' Settings specific to the img app. '''

import random
import string

### Image file extensions
allowed_file_extensions = (
  '.tiff',
)

allowed_track_extensions = (
  '.csv',
)

### image filename templates
templates = {
  'source':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>.+)_t(?P<t>[0-9]+)_z(?P<z>.+)\.(?P<extension>.+)$',
    'rv':r'%s_s%s_ch-%s_t%s_z%s.tiff',
  },
  'output':{
    'rx':r'^out_(?P<name>.+)_t(?P<t>[0-9]+)_z(?P<z>.+)\.(?P<extension>.+)$',
    'rv':r'out_%s_t%s_z%s.tiff',
  },
  'track':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_(?P<index>[0-9]+)\.(?P<extension>.+)$',
    'rv':r'%s_s%s_%s.csv',
  },
  'mask':{
    'rx':r'^mask_(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>.+)_t(?P<t>[0-9]+)_z(?P<z>.+)\.(?P<extension>.+)$',
    'rv':r'mask_%s_s%s_ch%s_t%s_z%s.tif',
  }
}

### Default paths
default_paths = {
  'img':'img/storage/',
  'composite':'img/composite/',
  'mask':'img/mask/out/',
  'plot':'plot/',
  'track':'track/',
  'out':'out/',
}
