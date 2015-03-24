# woot.apps.pix.algorithms

# django

# local

# util
import os
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
import numpy as np
from scipy.misc import imsave

# methods
# every algorithm follows this pattern:
# 1. start from composite
# 2. get images in some order
# 3. perform some calculations on gons -> 2D or 3D
# 4. after each 2D or 3D calculation, save images and create new gons
# 5. done.

def channel_test_3D(composite, mod_id, algorithm):
  # simply multiply each 3D gon in the brightfield by its corresponding gon in the GFP.
  bf_set = composite.gons.filter(channel__name='1')
  gfp_set = composite.gons.filter(channel__name='0')

  # paths
  composite_template = composite.templates.get(name='composite')
  composite_url = os.path.join(composite.experiment.composite_path, composite_template.rv)

  # channel
  channel = composite.channels.create(name='%s-%s' % (mod_id, algorithm))

  for t in range(composite.series.ts):
    print(t)
    # 1. get
    bf = bf_set.get(t=t)
    bf_array = bf.load()

    gfp = gfp_set.get(t=t)
    gfp_array = gfp.load()

    # 2. calculations
    product = gfp_array * bf_array

    # 3. output
    gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=channel)
    gon.set_origin(bf.r, bf.c, bf.z, bf.t)
    gon.set_extent(bf.rs, bf.cs, bf.zs)

    gon.array = product

    gon.save_paths(composite_url, composite_template)
    gon.split()

    gon.save()

def pmod(composite, mod_id, algorithm):
  # simply multiply each 3D gon in the brightfield by its corresponding gon in the GFP.
  bf_set = composite.gons.filter(channel__name='1')
  gfp_set = composite.gons.filter(channel__name='0')

  # paths
  template = composite.templates.get(name='source')
  url = os.path.join(composite.experiment.composite_path, template.rv)

  # channel
  channel = composite.channels.create(name='%s-%s' % (mod_id, '-pmod-mask'))

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

def primary(composite, mod_id, algorithm):
  # get all cell markers
  for t in range(composite.series.ts):
    print(t)

    markers = composite.series.cell_markers.filter(t=t)

    b = np.zeros((composite.series.rs, composite.series.cs), dtype='uint8')

    for marker in markers:
      b[marker.r-1:marker.r+1, marker.c-1:marker.c+1] = 255

    print(b.sum())

    for z in range(composite.series.zs):
      imsave(os.path.join(composite.experiment.composite_path, 'primary_t%s_z%s.tiff' % (str('0'*(len(str(composite.series.ts)) - len(str(t))) + str(t)),str('0'*(len(str(composite.series.zs)) - len(str(z))) + str(z)))), b)
