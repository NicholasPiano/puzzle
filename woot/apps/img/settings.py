#woot.apps.img.settings

''' Settings specific to the img app '''

### Image file extensions
allowed_file_extensions = (
  '.tiff',
)

### default image filename template
img_template = r'(?P<experiment_name>.+)_ch(?P<image_type>[0-9]+)_t(?P<timepoint>[0-9]+)_z(?P<level>[0-9]+)\.(?P<extension>.+)$'

### Image types
img_types = {'0':'gfp','1':'bf','2':'mask'}
def img_type(query):
  return img_types[query]
