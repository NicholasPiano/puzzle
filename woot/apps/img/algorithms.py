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
def scan_point(img, rs, cs, r, c, size=0):
  r0 = r - size if r - size >= 0 else 0
  r1 = r + size + 1 if r + size + 1 <= rs else rs
  c0 = c - size if c - size >= 0 else 0
  c1 = c + size + 1 if c + size + 1 <= cs else cs

  column = img[r0:r1,c0:c1,:]
  column_1D = np.sum(np.sum(column, axis=0), axis=0)

  return column_1D

# algorithms
def mod_zmod(composite, mod_id, algorithm):
  # template
  template = composite.templates.get(name='source') # SOURCE TEMPLATE

  # channels
  zmod_channel, zmod_channel_created = composite.channels.get_or_create(name='-zmod')
  zmean_channel, zmean_channel_created = composite.channels.get_or_create(name='-zmean')
  zbf_channel, zbf_channel_created = composite.channels.get_or_create(name='-zbf')
  zcomp_channel, zbf_channel_created = composite.channels.get_or_create(name='-zcomp')

  # constants
  delta_z = -8
  size = 5
  sigma = 5
  template = composite.templates.get(name='source')

  # iterate over frames
  for t in range(composite.series.ts):

    # load gfp
    gfp_gon = composite.gons.get(t=t, channel__name='0')
    gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)
    gfp = gf(gfp, sigma=sigma) # <<< SMOOTHING

    # load bf
    bf_gon = composite.gons.get(t=t, channel__name='1')
    bf = exposure.rescale_intensity(bf_gon.load() * 1.0)

    # initialise images
    Z = np.zeros(composite.series.shape(d=2), dtype=int)
    Zmean = np.zeros(composite.series.shape(d=2))
    Zbf = np.zeros(composite.series.shape(d=2))
    Zcomp = np.zeros(composite.series.shape(d=2))

    # loop over image
    for r in range(composite.series.rs):
      for c in range(composite.series.cs):

        # scan
        data = scan_point(gfp, composite.series.rs, composite.series.cs, r, c, size=size)
        normalised_data = np.array(data) / np.max(data)

        # data
        z = int(np.argmax(normalised_data))
        cz = z + delta_z #corrected z
        mean = 1.0 - np.mean(normalised_data) # 1 - mean
        bfz = bf[r,c,cz]

        Z[r,c] = cz
        Zmean[r,c] = mean
        Zbf[r,c] = bfz
        Zcomp[r,c] = bfz * mean

      print(t,r)

    # images to channel gons
    zmod_gon, zmod_gon_created = composite.gons.get_or_create(experiment=composite.experiment, series=composite.series, channel=zmod_channel, t=t)
    if True:
      zmod_gon.set_origin(0,0,0,t)
      zmod_gon.set_extent(composite.series.rs, composite.series.cs, 1)

      zmod_gon.array = Z
      zmod_gon.save_array(composite.series.experiment.composite_path, template)
      zmod_gon.save()

    zmean_gon, zmean_gon_created = composite.gons.get_or_create(experiment=composite.experiment, series=composite.series, channel=zmean_channel, t=t)
    if True:
      zmean_gon.set_origin(0,0,0,t)
      zmean_gon.set_extent(composite.series.rs, composite.series.cs, 1)

      zmean_gon.array = exposure.rescale_intensity(Zmean * 1.0)
      zmean_gon.save_array(composite.series.experiment.composite_path, template)
      zmean_gon.save()

    zbf_gon, zbf_gon_created = composite.gons.get_or_create(experiment=composite.experiment, series=composite.series, channel=zbf_channel, t=t)
    if True:
      zbf_gon.set_origin(0,0,0,t)
      zbf_gon.set_extent(composite.series.rs, composite.series.cs, 1)

      zbf_gon.array = Zbf
      zbf_gon.save_array(composite.series.experiment.composite_path, template)
      zbf_gon.save()

    zcomp_gon, zcomp_gon_created = composite.gons.get_or_create(experiment=composite.experiment, series=composite.series, channel=zcomp_channel, t=t)
    if True:
      zcomp_gon.set_origin(0,0,0,t)
      zcomp_gon.set_extent(composite.series.rs, composite.series.cs, 1)

      zcomp_gon.array = Zcomp
      zcomp_gon.save_array(composite.series.experiment.composite_path, template)
      zcomp_gon.save()

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
