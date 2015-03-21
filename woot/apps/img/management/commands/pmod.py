#django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#local
from apps.img.models import Composite, Mod
from apps.img import settings as img_settings

#util
import os
import re
from optparse import make_option
import matplotlib.pyplot as plt
from skimage import feature as ft
from skimage import exposure as ex
from scipy.ndimage.filters import gaussian_filter as gaufil
from scipy.misc import imsave

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):
    # c = Composite.objects.get()
    # pmod = c.mods.create(experiment=c.experiment, series=c.series, id_token=img_settings.generate_id_token(Mod), algorithm='pmod_track')
    # pmod.run()
    c = Composite.objects.get(series__name='13')

    bulk = c.bulks.get(t__index=0)

    output_path = os.path.join(c.experiment.base_path, c.experiment.output_path)

    # process gfp as a great gon
    gfp_great_gon = bulk.gons.get(great=True, channel__index=0)
    gfp_gon = gfp_great_gon.load()

    gfp_gon = ex.rescale_intensity(gfp_gon*1.0)
    gfp_gon[gfp_gon<gfp_gon.mean()] = 0
    smooth_gon = gaufil(gfp_gon, sigma=10)

    for level in range(bulk.levels):
      print(level)

      smooth = smooth_gon[:,:,level]

      bf_gon = bulk.gons.get(great=False, l=level, channel__index=1)
      bf = bf_gon.load()

      # 1. edges in bf
      edges3 = ft.canny(bf, sigma=3)
      edges4 = ft.canny(bf, sigma=4)
      edges5 = ft.canny(bf, sigma=5)

      edges = edges3 + edges4 + edges5
      edges = ex.rescale_intensity(edges*1.0)
      edges = gaufil(edges, sigma=10)

      # 3. filter
      out = ex.rescale_intensity(smooth)

      bf = ex.rescale_intensity(bf)
      new_bf = bf*out

      imsave(os.path.join(output_path, 'pmod_z%s.tiff' % (str('0'*(len(str(bulk.levels))-len(str(level)))) + str(level))), new_bf)

    # display test
    # plt.imshow(new_bf, cmap='Greys_r')
    # plt.show()
