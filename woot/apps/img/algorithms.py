# woot.apps.img.algorithms

# django

# local

# util

def pmod_track(composite, id_token):
  ''' Highlights brightfield with gfp to allow easier centre recognition by eye. Not meant for automatic segmentation. '''
  print('running pmod_track for composite %s, mod %s...' % (composite.id_token, id_token))

  # loop through bulks
  for bulk in composite.bulks.order_by('t__index'):
    print('processing bulk at frame %d' % bulk.t.index)

    # get img sets
    great_gfp_gon = bulk.gons.get(great=True, channel__index=0)
    gfp = great_gfp_gon.load()

    great_bf_gon = bulk.gons.get(great=True, channel__index=1)
    bf = great_bf_gon.load()

    # create new channel
    name = 'pmod-track-' + id_token
    channel = composite.channels.create(experiment=composite.experiment, series=composite.series, name=name, index=composite.get_max_channel_index())

    # make new great gon
    new_great_gon = bulk.gons.create(experiment=composite.experiment, series=composite.series, composite=composite, channel=channel, great=True, id_token=composite.experiment.gon_id_token(), t=bulk.t, rows=bulk.rows, columns=bulk.columns, levels=bulk.levels)

    # perform calculations
    new = bf * gfp
    new_great_gon.array = new

    # create new gons and update bulk
    new_great_gon.split(id_token)
