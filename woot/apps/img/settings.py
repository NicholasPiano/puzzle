#woot.apps.img.settings

''' Settings specific to the img app '''

### Image file extensions
allowed_file_extensions = (
  '.tiff',
)

### default image filename template
img_template = r'(?P<experiment_name>.+)_ch(?P<channel>[0-9]+)_t(?P<timepoint>[0-9]+)_z(?P<level>[0-9]+)\.(?P<extension>.+)$'

### Image types
channels = {
  '0':'gfp','1':'bf','2':'mask',
  'gfp':'0','bf':'1','mask':'2',
}
def channel(query):
  return channels[query]
