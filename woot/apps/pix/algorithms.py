# woot.apps.pix.algorithms

# django

# local

# util
import os

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
