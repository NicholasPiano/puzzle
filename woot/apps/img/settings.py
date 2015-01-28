#woot.apps.img.settings

''' Settings specific to the img app '''

### Image file extensions
allowed_file_extensions = (
  '.tiff',
)

### default image filename template
img_template = r'(?P<experiment_name>.+)_ch(?P<channel>[0-9]+)_t(?P<timepoint>[0-9]+)_z(?P<level>[0-9]+)\.(?P<extension>.+)$'

### Image types
channels = {'0':'gfp','1':'bf','2':'mask'}
def channel(query):
  if query in channels.values():
    return query
  else:
    return channels[query]
