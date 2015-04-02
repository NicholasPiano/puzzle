# apps.img.algorithms

# local


# util
import os
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
import numpy as np
from scipy.misc import imsave

# methods
def mod_pmod(composite, mod_id, algorithm):
  bf_set = composite.gons.filter(channel__name='1')
  gfp_set = composite.gons.filter(channel__name='0')

  # paths
  template = composite.templates.get(name='source')
  url = os.path.join(composite.experiment.composite_path, template.rv)

  # channel
  channel = composite.channels.create(name='1-%s-%s-%s' % (composite.id_token, 'pmod', mod_id))

  for t in range(composite.series.ts):
    print(t)
    # 1. get
    bf = bf_set.get(t=t)
    bf_array = exposure.rescale_intensity(bf.load() * 1.0)

    gfp = gfp_set.get(t=t)
    gfp_array = exposure.rescale_intensity(gfp.load() * 1.0)

    # 2. calculations
    gfp_smooth = gf(gfp_array, sigma=5)
    gfp_reduced_glow = gfp_smooth * gfp_smooth

    product = gfp_reduced_glow * bf_array

    # 3. output
    gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=channel)
    gon.set_origin(bf.r, bf.c, bf.z, bf.t)
    gon.set_extent(bf.rs, bf.cs, bf.zs)

    gon.array = product

    gon.save_paths(url, template)
    gon.split()

    gon.save()

mod_pmod.description = 'Scale portions of the brightfield using the gfp density.'

def mod_primary(composite, mod_id, algorithm):
  # paths
  template = composite.templates.get(name='source')
  url = os.path.join(composite.experiment.composite_path, template.rv)

  # channel
  channel = composite.channels.create(name='1-%s-%s-%s' % (composite.id_token, 'primary', mod_id))

  # get all cell markers
  for t in range(composite.series.ts):
    print(t)

    markers = composite.series.markers.filter(t=t)

    # black field in which to place markers
    b = np.zeros((composite.series.rs, composite.series.cs), dtype='uint8')

    for marker in markers:
      b[marker.r-1:marker.r+1, marker.c-1:marker.c+1] = 255

    # duplicate over z
    out = np.dstack([b]*composite.series.zs)

    # 3. output
    gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=channel)
    gon.set_origin(0, 0, 0, t)
    gon.set_extent(composite.series.rs, composite.series.cs, composite.series.zs)

    gon.array = out

    gon.save_paths(url, template)
    gon.split()

    gon.save()

mod_primary.description = 'Create channel containing track points to set as primary in Cell Profiler.'

def mod_reduced(composite, mod_id, algorithm):
  # paths
  template = composite.templates.get(name='source')
  url = os.path.join(composite.experiment.cp_path, template.rv)

  # channels
  pmod_reduced_channel = composite.channels.create(name='1-%s-%s-%s' % (composite.id_token, 'pmodreduced', mod_id))
  primary_reduced_channel = composite.channels.create(name='1-%s-%s-%s' % (composite.id_token, 'primaryreduced', mod_id))

  # image sets
  pmod_set = composite.gons.filter(channel__name__contains='pmod-')

  # loop through timesteps
  for t in range(composite.series.ts):
    print(t)

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

mod_reduced.description = ''
