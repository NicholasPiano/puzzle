#woot.apps.img.settings

''' Settings specific to the img app '''

import random

### Image file extensions
allowed_file_extensions = (
  '.tiff',
)

### image filename templates
img_template = r'(?P<experiment_name>.+)_ch(?P<channel>[0-9]+)_t(?P<timepoint>[0-9]+)_z(?P<level>[0-9]+)\.(?P<extension>.+)$'
composite_img_template = {
  'template':r'',
  'regex':r'',
}

### Image types
channels = {
  '0':'gfp','1':'bf','2':'mask',
}
def channel(query):
  return channels[query]

### Generate id token
def generate_id_token(Obj): #expects Obj.objects
  def get_id_token():
    return ''.join([random.choice(chars) for _ in range(8)]) #8 character string

  id_token = get_id_token()
  while Obj.objects.filter(id_token=id_token).count()>0:
    id_token = get_id_token()

  return id_token
