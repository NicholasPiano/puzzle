# woot.apps.img.algorithms

# django

# local

# util

def pmod_track(self, composite, id_token):
  ''' Highlights brightfield with gfp to allow easier centre recognition by eye. Not meant for automatic segmentation. '''
  print('running pmod_track for composite %s, mod %s...' % (composite.id_token, id_token))

  # loop through bulks
  for bulk in composite.bulks.order_by('frame__index'):

    # get img sets
    great_gfp_gon = bulk.gons.get(great=True, channel__index=0)
    gfp = great_gfp_gon.load()

    great_bf_gon = bulk.gons.get(great=True, channel__index=1)
    bf = great_bf_gon.load()

    # perform calculations
    new_great_gon

    # create new channel
    name = 'pmod_track' + id_token
    channel = composite.channels.create(experiment=composite.experiment, series=composite.series, name=name, index=composite.get_max_channel_index())

    # create new gons and update bulk
    new_great_gon.split(id_token)
