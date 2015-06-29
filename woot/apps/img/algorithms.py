# apps.img.algorithms

# local
from apps.img.util import cut_to_black, create_bulk_from_image_set, nonzero_mean, edge_image
from apps.expt.util import generate_id_token

# util
import os
from scipy.misc import imsave
from scipy.ndimage.filters import gaussian_filter as gf
from scipy.ndimage.measurements import center_of_mass as com
from skimage import exposure
import numpy as np
from scipy.ndimage.measurements import label
import matplotlib.pyplot as plt

# methods


# algorithms
def mod_zmod(composite, mod_id, algorithm):
  bf_set = composite.gons.filter(channel__name='1')
  gfp_set = composite.gons.filter(channel__name='0')

  # template
  template = composite.templates.get(name='source') # SOURCE TEMPLATE

  # channels
  zmod_channel, zmod_channel_created = composite.channels.get_or_create(name='-zmod')
  zmean_channel, zmean_channel_created = composite.channels.get_or_create(name='-zmean')
  zcomp_channel, zcomp_channel_created = composite.channels.get_or_create(name='-zcomp')

  # iterate over frames
  for t in range(composite.series.ts):

    # load gfp

    # load bf



def mod_regions(composite, mod_id, algorithm):
  # paths
  template = composite.templates.get(name='region') # REGION TEMPLATE
  mask_template = composite.templates.get(name='mask')

  # get region img set that has the region template
  region_img_set = composite.gons.filter(channel__name='-regionimg', template__name='region')

  # channel
  region_channel, region_channel_created = composite.channels.get_or_create(name='-regions')

  # iterate
  for t in range(composite.series.ts):
    region_img = region_img_set.filter(t=t)
    if region_img.count()==0:
      region_img = region_img_set.get(t=t-1)
    else:
      region_img = region_img_set.get(t=t)

    # for each image, determine unique values of labelled array
    # make gon with label array and save

    region_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=region_channel, template=template)
    region_gon.set_origin(0, 0, 0, t)
    region_gon.set_extent(composite.series.rs, composite.series.cs, 1)

    # modify image
    region_array = region_img.load()
    region_array = region_array[:,:,0]
    region_array[region_array>0] = 1
    region_array, n = label(region_array)

    region_gon.array = region_array.copy()
    region_gon.save_array(os.path.join(composite.experiment.mask_path, composite.series.name), template)

    for unique_value in [u for u in np.unique(region_array) if u>0]:
      # 1. cut image to single value
      unique_image = np.zeros(region_array.shape)
      unique_image[region_array==unique_value] = 1
      cut, (r,c,rs,cs) = cut_to_black(unique_image)

      # 2. make gon with cut image and associate to gon
      gon = region_gon.gons.create(experiment=composite.experiment, series=composite.series, channel=region_channel, template=mask_template)
      gon.id_token = generate_id_token('img','Gon')
      gon.set_origin(r,c,0,t)
      gon.set_extent(rs,cs,1)

      gon.array = cut.copy()

      gon.save_mask(composite.experiment.sub_mask_path)
      gon.save()

      # 3. make mask with cut image and associate to gon2
      mask = region_gon.masks.create(composite=composite, channel=region_channel, mask_id=unique_value)
      mask.set_origin(r,c,0)
      mask.set_extent(rs,cs)
