# apps.img.algorithms

# local


# util
import os
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
import numpy as np
from scipy.misc import imsave
from PIL import Image
import matplotlib.cm as cm

# methods
### STEP 2: Generate images for
def mod_step2_tracking(composite, mod_id, algorithm):
  bf_set = composite.gons.filter(channel__name='1')
  gfp_set = composite.gons.filter(channel__name='0')

  # paths
  template = composite.templates.get(name='composite') # COMPOSITE TEMPLATE
  url = os.path.join(composite.experiment.tracking_path, template.rv) # TRACKING DIRECTORY

  # channel
  tracking_channel = composite.channels.create(name='%s-%s-%s' % (composite.id_token, 'tracking', mod_id))

  # iterate over frames
  for t in range(composite.series.ts):
    print('processing mod_step2_tracking t%d...' % t)

    # 1. get
    bf_gon = bf_set.get(t=t)
    bf_gon = bf_gon.gons.get(z=int(bf_gon.zs/2.0))
    bf = exposure.rescale_intensity(bf_gon.load() * 1.0)

    gfp_gon = gfp_set.get(t=t)
    gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)

    # 2. calculations
    gfp_smooth = gf(gfp, sigma=2)
    gfp_smooth = np.sum(gfp_smooth, axis=2) / 14.0 # completely arbitrary factor
    # gfp_reduced_glow = gfp_smooth * gfp_smooth
    # gfp_reduced_glow = np.sum(gfp_reduced_glow, axis=2)

    product = bf + gfp_smooth # superimposes the (slightly) smoothed gfp onto the bright field.

    # pmod
    tracking_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=tracking_channel)
    tracking_gon.set_origin(0, 0, 0, t)
    tracking_gon.set_extent(composite.series.rs, composite.series.cs, 1)

    tracking_gon.array = product

    tracking_gon.save_single(url, template, 0)
    tracking_gon.save()

mod_step2_tracking.description = ''

### STEP 5: combine channels - FAILED: too many images
def mod_step5_pmod(composite, mod_id, algorithm):
  bf_set = composite.gons.filter(channel__name='1')
  gfp_set = composite.gons.filter(channel__name='0')

  # paths
  template = composite.templates.get(name='composite') # COMPOSITE TEMPLATE
  url = os.path.join(composite.experiment.composite_path, template.rv) # COMPOSITE DIRECTORY

  # channel
  channel = composite.channels.create(name='%s-%s-%s' % (composite.id_token, 'pmod', mod_id))

  # iterate over frames
  for t in range(composite.series.ts):
    print('processing mod_step5_pmod t%d...' % t)
    # 1. get
    bf_gon = bf_set.get(t=t)
    bf = exposure.rescale_intensity(bf_gon.load() * 1.0)

    gfp_gon = gfp_set.get(t=t)
    gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)

    # 2. calculations
    gfp_smooth = exposure.rescale_intensity(gf(gfp, sigma=5)) / 2.0
    # gfp_reduced_glow = gfp_smooth * gfp_smooth

    # product = gfp_reduced_glow * bf
    product = bf * gfp_smooth

    # 3. output
    gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=channel)
    gon.set_origin(bf_gon.r, bf_gon.c, bf_gon.z, bf_gon.t)
    gon.set_extent(bf_gon.rs, bf_gon.cs, bf_gon.zs)

    gon.array = product

    gon.save_paths(url, template)
    gon.split()

    gon.save()

mod_step5_pmod.description = 'Scale portions of the brightfield using the gfp density.'

### STEP 5: only relevant z levels - FAILED: inconsistent recognition
def mod_step5_reduced(composite, mod_id, algorithm):
  # paths
  template = composite.templates.get(name='composite') # COMPOSITE TEMPLATE
  url = os.path.join(composite.experiment.cp_path, template.rv) # CP PATH

  # channels
  pmod_reduced_channel = composite.channels.create(name='%s-%s-%s' % (composite.id_token, 'pmodreduced', mod_id))
  primary_reduced_channel = composite.channels.create(name='%s-%s-%s' % (composite.id_token, 'primaryreduced', mod_id))

  # image sets
  pmod_set = composite.gons.filter(channel__name__contains='pmod-')

  # iterate over frames
  for t in range(composite.series.ts):
    print('processing mod_step5_reduced t%d...' % t)

    # 1. get
    pmod_gon = pmod_set.get(t=t)

    markers = composite.series.markers.filter(t=t)

    # 2. for each unique z value of the markers, make a gon and add it to the pmod_reduced channel
    marker_z_values = list(np.unique([marker.z for marker in markers]))

    for z in marker_z_values:
      # save z range
      lower_z = z - 1 if z - 1 >= 0 else 0
      upper_z = z + 2 if z + 2 < composite.series.zs else composite.series.zs

      for sz in range(lower_z,upper_z):

        # pmod
        rpmod_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=pmod_reduced_channel)
        rpmod_gon.set_origin(0, 0, 0, t)
        rpmod_gon.set_extent(composite.series.rs, composite.series.cs, 1)

        rpmod_gon.array = pmod_gon.gons.get(z=sz).load()

        rpmod_gon.save_single(url, template, sz)
        rpmod_gon.save()

        # markers
        rprimary_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=primary_reduced_channel)
        rprimary_gon.set_origin(0, 0, 0, t)
        rprimary_gon.set_extent(composite.series.rs, composite.series.cs, 1)

        # make black field
        markers_z = markers.filter(z__gte=lower_z, z__lt=upper_z)
        b = np.zeros((composite.series.rs, composite.series.cs), dtype='uint8')

        for marker in markers_z:
          b[marker.r-1:marker.r+1, marker.c-1:marker.c+1] = 255

        rprimary_gon.array = b

        rprimary_gon.save_single(url, template, sz)
        rprimary_gon.save()

mod_step5_reduced.description = ''

### STEP 5: flatten gfp for masks - FAILED: bad recognition
def mod_step5_gfp_flat(composite, mod_id, algorithm):

  gfp_set = composite.gons.filter(channel__name='0')

  # paths
  template = composite.templates.get(name='composite') # COMPOSITE TEMPLATE
  url = os.path.join(composite.experiment.cp_path, template.rv) # CP DIRECTORY

  # channel
  channel = composite.channels.create(name='%s-%s-%s' % (composite.id_token, 'pmodgfpflat', mod_id))

  # iterate over frames
  for t in range(composite.series.ts):
    print('processing mod_step5_gfp_flat t%d...' % t)
    # 1. get

    gfp_gon = gfp_set.get(t=t)
    gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)

    # 2. calculations
    gfp_smooth = exposure.rescale_intensity(gf(gfp, sigma=2))
    # gfp_reduced_glow = gfp_smooth * gfp_smooth

    # 3. output
    gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=channel)
    gon.set_origin(gfp_gon.r, gfp_gon.c, gfp_gon.z, gfp_gon.t)
    gon.set_extent(gfp_gon.rs, gfp_gon.cs, 1)

    gon.array = np.sum(gfp_smooth, axis=2)
    gon.save_single(url, template, 0)

    gon.save()

mod_step5_gfp_flat.description = 'Flatten gfp and blur slightly.'

def mod_step5_bf_gfp_reduced(composite, mod_id, algorithm):
  # paths
  template = composite.templates.get(name='composite') # COMPOSITE TEMPLATE

  # channels
  pmod_reduced_channel = composite.channels.create(name='%s-%s-%s' % (composite.id_token, 'pmodreduced', mod_id))
  bf_reduced_channel = composite.channels.create(name='%s-%s-%s' % (composite.id_token, 'bfreduced', mod_id))

  # image sets
  pmod_set = composite.gons.filter(channel__name__contains='pmod-')
  bf_set = composite.gons.filter(channel__name='1')

  # create batches
  batch = 0
  max_batch_size = 100

  # iterate over frames
  for t in range(composite.series.ts):
    print('processing mod_step5_bf_gfp_reduced t%d...' % t)

    # 1. get
    pmod_gon = pmod_set.get(t=t)
    bf_gon = bf_set.get(t=t)

    # 2. for each unique z value of the markers, make a gon and add it to the pmod_reduced channel
    marker_z_values = list(np.unique([marker.z for marker in composite.series.markers.filter(t=t)]))

    for z in marker_z_values:
      # save z range
      lower_z = z - 1 if z - 1 >= 0 else 0
      upper_z = z + 2 if z + 2 < composite.series.zs else composite.series.zs

      for sz in range(lower_z,upper_z):

        # check batch and make folders, set url
        if not os.path.exists(os.path.join(composite.experiment.cp_path, str(batch))):
          os.mkdir(os.path.join(composite.experiment.cp_path, str(batch)))

        if len(os.listdir(os.path.join(composite.experiment.cp_path, str(batch))))==max_batch_size:
          batch += 1
          if not os.path.exists(os.path.join(composite.experiment.cp_path, str(batch))):
            os.mkdir(os.path.join(composite.experiment.cp_path, str(batch)))

        url = os.path.join(composite.experiment.cp_path, str(batch), template.rv) # CP PATH

        # pmod
        rpmod_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=pmod_reduced_channel)
        rpmod_gon.set_origin(0, 0, sz, t)
        rpmod_gon.set_extent(composite.series.rs, composite.series.cs, 1)

        rpmod_gon.array = pmod_gon.gons.get(z=sz).load()

        rpmod_gon.save_single(url, template, sz)
        rpmod_gon.save()

        # markers
        rbf_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=bf_reduced_channel)
        rbf_gon.set_origin(0, 0, sz, t)
        rbf_gon.set_extent(composite.series.rs, composite.series.cs, 1)

        rbf_gon.array = bf_gon.gons.get(z=sz).load()

        rbf_gon.save_single(url, template, sz)
        rbf_gon.save()

mod_step5_bf_gfp_reduced.description = 'Include bf channel to aid recognition'

def mod_system_check(composite, mod_id, algorithm):
  # paths
  template = composite.templates.get(name='composite') # COMPOSITE TEMPLATE
  url = os.path.join(composite.experiment.composite_path, template.rv) # CP PATH

  # channels
  system_check_channel = composite.channels.create(name='%s-%s-%s' % (composite.id_token, 'systemcheck', mod_id))

  # image sets
  bf_set = composite.gons.filter(channel__name='1')

  # iterate over frames
  for t in range(composite.series.ts):
    print('processing mod_system_check t%d...' % t)

    # 1. get
    bf_gon = bf_set.get(t=t)

    # 2. for each unique z value of the markers, make a gon and add it to the pmod_reduced channel
    marker_z_values = list(np.unique([marker.z for marker in composite.series.markers.filter(t=t)]))

    for z in marker_z_values:
      # make new gon
      system_check_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=system_check_channel)
      system_check_gon.set_origin(0, 0, z, t)
      system_check_gon.set_extent(composite.series.rs, composite.series.cs, 1)

      # make array
      # - 1. bf image at z
      bf_z = exposure.rescale_intensity(bf_gon.gons.get(z=z).load() * 1.0)

      # - 2. the sum of all the combined masks at this z
      combined_mask_sum = np.zeros((composite.series.rs, composite.series.cs), dtype=float)
      for marker in composite.series.markers.filter(t=t, z=z):
        combined_mask_sum += exposure.rescale_intensity(marker.combined_mask()*1.0)

      combined_mask_sum = exposure.rescale_intensity(combined_mask_sum)

      # - 3. alpha-ness is proportional to the value of the image.
      alpha_stack = exposure.rescale_intensity(bf_z + combined_mask_sum*combined_mask_sum)

      # assign array
      system_check_gon.array = alpha_stack.copy()

      # save gon and image
      system_check_gon.save_single(url, template, z)
      system_check_gon.save()

def mod_region_img(composite, mod_id, algorithm):
  # paths
  template = composite.templates.get(name='composite') # COMPOSITE TEMPLATE
  url = os.path.join(composite.experiment.region_img_path, template.rv) # REGION IMG PATH

  # channels
  region_img_channel = composite.channels.create(name='%s-%s-%s' % (composite.id_token, 'regionimg', mod_id))

  # image sets
  bf_set = composite.gons.filter(channel__name='1')

  # iterate over frames
  for t in range(composite.series.ts):

    # get middle z level
    middle_z = int(composite.series.zs / 2.0)
    print(middle_z)

    # get single bf plane at z
    bf = bf_set.get(t=t, z=middle_z).load()

    # make gon
    region_img_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=region_img_channel)
    region_img_gon.set_origin(0, 0, z, t)
    region_img_gon.set_extent(composite.series.rs, composite.series.cs, 1)

    region_img_gon.array = exposure.rescale_intensity(bf * 1.0)
    region_img_gon.save_single(url, template, z)
    region_img_gon.save()
