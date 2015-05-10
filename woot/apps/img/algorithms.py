# apps.img.algorithms

# local
from apps.img.util import cut_to_black
from apps.expt.util import generate_id_token

# util
import os
from scipy.ndimage.filters import gaussian_filter as gf
from skimage import exposure
import numpy as np
from scipy.ndimage.measurements import label

# methods
### STEP 2: Generate images for tracking
def mod_step02_tracking(composite, mod_id, algorithm):
  bf_set = composite.gons.filter(channel__name='1')
  gfp_set = composite.gons.filter(channel__name='0')

  # template
  template = composite.templates.get(name='source') # SOURCE TEMPLATE

  # channel
  tracking_channel, tracking_channel_created = composite.channels.get_or_create(name='-trackingimg')

  # iterate over frames
  for t in range(composite.series.ts):
    print('step02 | processing mod_step02_tracking t{}...'.format(t), end='\r')

    # 1. get
    bf_gon = bf_set.get(t=t)
    bf_gon = bf_gon.gons.get(z=int(bf_gon.zs/2.0))
    bf = exposure.rescale_intensity(bf_gon.load() * 1.0)

    gfp_gon = gfp_set.get(t=t)
    gfp = exposure.rescale_intensity(gfp_gon.load() * 1.0)

    # 2. calculations
    gfp_smooth = gf(gfp, sigma=2)
    gfp_smooth = np.sum(gfp_smooth, axis=2) / 14.0 # completely arbitrary factor

    product = bf + gfp_smooth # superimposes the (slightly) smoothed gfp onto the bright field.

    # pmod
    tracking_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=tracking_channel, template=template)
    tracking_gon.set_origin(0, 0, 0, t)
    tracking_gon.set_extent(composite.series.rs, composite.series.cs, 1)

    tracking_gon.array = product

    tracking_gon.save_array(composite.experiment.tracking_path, template)
    tracking_gon.save()

mod_step02_tracking.description = ''

### STEP 3: combine channels for recognition
def mod_step03_pmod(composite, mod_id, algorithm):
  bf_set = composite.gons.filter(channel__name='1')
  gfp_set = composite.gons.filter(channel__name='0')

  # template
  template = composite.templates.get(name='source') # SOURCE TEMPLATE

  # channel
  channel, channel_created = composite.channels.get_or_create(name='-pmod')

  # iterate over frames
  for t in range(composite.series.ts):
    print('step03 | processing mod_step03_pmod t{}...'.format(t), end='\r')
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
    gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=channel, template=template)
    gon.set_origin(bf_gon.r, bf_gon.c, bf_gon.z, bf_gon.t)
    gon.set_extent(bf_gon.rs, bf_gon.cs, bf_gon.zs)

    gon.array = product

    gon.save_array(composite.experiment.composite_path, template)

    gon.save()

mod_step03_pmod.description = 'Scale portions of the brightfield using the gfp density.'

def mod_step04_region_img(composite, mod_id, algorithm):
  bf_set = composite.gons.filter(channel__name='1')

  # template
  template = composite.templates.get(name='source') # SOURCE TEMPLATE

  # channel
  channel, channel_created = composite.channels.get_or_create(name='-regionimg')

  # iterate over frames
  for t in range(composite.series.ts):
    print('step03 | processing mod_step04_region_img t{}...'.format(t), end='\r')
    # 1. get
    bf_great_gon = bf_set.get(t=t)
    bf_gon = bf_great_gon.gons.get(z=int(bf_great_gon.zs / 2.0))
    bf = exposure.rescale_intensity(bf_gon.load() * 1.0)

    # 3. output
    gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=channel, template=template)
    gon.set_origin(bf_gon.r, bf_gon.c, 0, bf_gon.t)
    gon.set_extent(bf_gon.rs, bf_gon.cs, bf_gon.zs)

    gon.array = bf

    gon.save_array(composite.experiment.region_img_path, template)
    gon.save()

mod_step04_region_img.description = 'Raw brightfield image at the centre of the environment'

def mod_step08_reduced(composite, mod_id, algorithm):
  # paths
  template = composite.templates.get(name='source') # SOURCE TEMPLATE

  # channels
  pmod_reduced_channel, pmod_reduced_channel_created = composite.channels.get_or_create(name='-pmodreduced')
  bf_reduced_channel, bf_reduced_channel_created = composite.channels.get_or_create(name='-bfreduced')

  # image sets
  pmod_set = composite.gons.filter(channel__name='-pmod')
  bf_set = composite.gons.filter(channel__name='1')

  # create batches
  batch = 0
  max_batch_size = 100

  # iterate over frames
  for t in range(composite.series.ts):
    print('step08 | processing mod_step08_reduced t{}...'.format(t), end='\n' if t==composite.series.ts-1 else '\r')

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
        if not os.path.exists(os.path.join(composite.experiment.cp_path, composite.series.name, str(batch))):
          os.makedirs(os.path.join(composite.experiment.cp_path, composite.series.name, str(batch)))

        if len(os.listdir(os.path.join(composite.experiment.cp_path, composite.series.name, str(batch))))==max_batch_size:
          batch += 1
          if not os.path.exists(os.path.join(composite.experiment.cp_path, composite.series.name, str(batch))):
            os.makedirs(os.path.join(composite.experiment.cp_path, composite.series.name, str(batch)))

        root = os.path.join(composite.experiment.cp_path, composite.series.name, str(batch)) # CP PATH

        # pmod
        if pmod_reduced_channel.paths.filter(t=t, z=sz).count()==0:
          rpmod_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=pmod_reduced_channel, template=template)
          rpmod_gon.set_origin(0, 0, sz, t)
          rpmod_gon.set_extent(composite.series.rs, composite.series.cs, 1)

          rpmod_gon.array = pmod_gon.gons.get(z=sz).load()

          rpmod_gon.save_array(root, template)
          rpmod_gon.save()

        # bf
        if bf_reduced_channel.paths.filter(t=t, z=sz).count()==0:
          rbf_gon = composite.gons.create(experiment=composite.experiment, series=composite.series, channel=bf_reduced_channel, template=template)
          rbf_gon.set_origin(0, 0, sz, t)
          rbf_gon.set_extent(composite.series.rs, composite.series.cs, 1)

          rbf_gon.array = bf_gon.gons.get(z=sz).load()

          rbf_gon.save_array(root, template)
          rbf_gon.save()

mod_step08_reduced.description = 'Include bf channel to aid recognition'

def mod_step09_regions(composite, mod_id, algorithm):
  # paths
  template = composite.templates.get(name='region') # REGION TEMPLATE
  mask_template = composite.templates.get(name='mask')

  # get region img set that has the region template
  region_img_set = composite.gons.filter(channel__name='-regionimg', template__name='region')

  # channel
  region_channel, region_channel_created = composite.channels.get_or_create(name='-regions')

  # iterate
  for t in range(composite.series.ts):
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
    region_gon.save_array(composite.experiment.mask_path, template)

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

mod_step09_regions.description = 'Convert gimp images into binary masks'

def mod_step11_masks(composite, mod_id, algorithm):
  # templates
  cp_template = composite.templates.get(name='cp')
  mask_template = composite.templates.get(name='mask')

  # mask img set
  mask_gon_set = composite.gons.filter(channel__name__in=['pmodreduced','bfreduced'], template__name='cp')

  for mask_gon in mask_gon_set:
    # load and get unique values
    mask_array = mask_gon.load()

    # unique
    for unique_value in [u for u in np.unique(mask_array) if u>0]:
      print('step11 | processing mod_step11_masks... {}: {} masks'.format(mask_gon.paths.get().file_name, unique_value), end='\r')

      # 1. cut image to single value
      unique_image = np.zeros(mask_array.shape)
      unique_image[mask_array==unique_value] = 1
      cut, (r,c,rs,cs) = cut_to_black(unique_image)

      # 3. make mask with cut image and associate to gon2
      mask = mask_gon.masks.create(composite=composite, channel=mask_gon.channel, mask_id=unique_value)
      mask.set_origin(r,c,mask_gon.z)
      mask.set_extent(rs,cs)

def mod_step13_cell_masks(composite, mod_id, algorithm):
  pass
