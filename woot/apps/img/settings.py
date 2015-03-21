# woot.apps.img.settings

''' Settings specific to the img app. '''

import random
import string

### Image file extensions
allowed_file_extensions = (
  '.tiff',
)

### image filename templates
templates = {
  'source':{
    'rx':r'^(?P<experiment>.+)_s(?P<series>.+)_ch(?P<channel>.+)_t(?P<frame>[0-9]+)_z(?P<z>.+)\.(?P<extension>.+)$',
    'rv':r'%s_s%s_ch-%s_t%s_z%s.tiff',
  },
  'composite':{
    'rx':r'^(?P<id_token>.+)\.(?P<extension>.+)$',
    'rv':r'%s.tiff',
  },
  'output':{
    'rx':r'^out_(?P<experiment>.+)_s(?P<series>.+)_ch-(?P<channel>.+)_t(?P<frame>[0-9]+)_z(?P<z>.+)_id-(?P<id_token>.+)\.(?P<extension>.+)$',
    'rv':r'out_%s_s%s_ch-%s_t%s_z%s_id-%s.tiff',
  },
}

### Default paths
default_paths = {
  'img':'img/storage/',
  'composite':'img/composite/',
  'plot':'plot/',
  'track':'track/',
  'out':'out/',
}

### Image types
channels = {
  '0':'gfp',
  '1':'bf',
}

def channel(query):
  return channels[query]

### Generate id token
chars = string.ascii_uppercase + string.digits
def generate_id_token(Obj): #expects Obj.objects
  def get_id_token():
    return ''.join([random.choice(chars) for _ in range(8)]) #8 character string

  id_token = get_id_token()
  while Obj.objects.filter(id_token=id_token).count()>0:
    id_token = get_id_token()

  return id_token
