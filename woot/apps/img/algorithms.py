# apps.img.algorithms

# local


# util
import os
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
import numpy as np
from scipy.misc import imsave

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

### STEP 5: Combine channels
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
    gfp_smooth = gf(gfp, sigma=5)
    gfp_reduced_glow = gfp_smooth * gfp_smooth

    product = gfp_reduced_glow * bf

    # 3. output
    gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=channel)
    gon.set_origin(bf_gon.r, bf_gon.c, bf_gon.z, bf_gon.t)
    gon.set_extent(bf_gon.rs, bf_gon.cs, bf_gon.zs)

    gon.array = product

    gon.save_paths(url, template)
    gon.split()

    gon.save()

mod_step5_pmod.description = 'Scale portions of the brightfield using the gfp density.'

### STEP 5: generate images for cell profiler
# Output images in composite format
# Cell profiler will prepend 'cp_' to the filename
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
      # pmod
      rpmod_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=pmod_reduced_channel)
      rpmod_gon.set_origin(0, 0, 0, t)
      rpmod_gon.set_extent(composite.series.rs, composite.series.cs, 1)

      rpmod_gon.array = pmod_gon.gons.get(z=z).load()

      rpmod_gon.save_single(url, template, z)
      rpmod_gon.save()

      # markers
      rprimary_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=primary_reduced_channel)
      rprimary_gon.set_origin(0, 0, 0, t)
      rprimary_gon.set_extent(composite.series.rs, composite.series.cs, 1)

      # make black field
      markers_z = markers.filter(z=z)
      b = np.zeros((composite.series.rs, composite.series.cs), dtype='uint8')

      for marker in markers_z:
        b[marker.r-1:marker.r+1, marker.c-1:marker.c+1] = 255

      rprimary_gon.array = b

      rprimary_gon.save_single(url, template, z)
      rprimary_gon.save()

mod_step5_reduced.description = ''
