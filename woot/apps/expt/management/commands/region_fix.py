
# django
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# local
from apps.expt.models import Experiment, Series

# util
import os
import numpy as np
import tifffile as tiff
from scipy.misc import imread

### Command
class Command(BaseCommand):

  args = ''
  help = ''

  def handle(self, *args, **options):

    # 050714
    # images are in png NxMx2
    # need to go to tiff NxMx4 -> 3x first layer + 1x 255
    # series_050714 = Series.objects.get(experiment__name='050714')
    # region_path_050714 = series_050714.experiment.region_path
    # region2_path_050714 = series_050714.experiment.region_path + '2'
    # region_template = series_050714.experiment.templates.get(name='region')
    #
    # for file_name in [f for f in os.listdir(region_path_050714) if ('.DS' not in f and 'tiff' in f)]:
    #
    #   # load each image
    #   img = tiff.imread(os.path.join(region_path_050714, file_name))
    #
    #   # modify
    #   img_top = img[:,:,0]
    #   ones = np.ones(img_top.shape) * 255
    #   img = np.dstack([img_top,img_top,img_top])
    #
    #   # save to tiff in region 2
    #   tiff.imsave(os.path.join(region2_path_050714, file_name), img)

    # 260714
    # series_260714 = Series.objects.get(experiment__name='260714', name='15')
    # region_path_260714 = series_260714.experiment.region_path
    # region2_path_260714 = series_260714.experiment.region_path + '2'
    # region_template = series_260714.experiment.templates.get(name='region')
    #
    # for file_name in [f for f in os.listdir(region_path_260714) if ('.DS' not in f and 'tiff' in f)]:
    #
    #   # load each image
    #   img = tiff.imread(os.path.join(region_path_260714, file_name))
    #
    #   # modify
    #   img_top = img[:,:,0]
    #   ones = np.ones(img_top.shape) * 255
    #   img = np.dstack([img_top,img_top,img_top])
    #   print(img.shape)
    #
    #   # save to tiff in region 2
    #   tiff.imsave(os.path.join(region2_path_260714, file_name), img)

    # 280614
    # tiff NxMx2 -> tiff NxMx4
    series_280614 = Series.objects.get(experiment__name='280614', name='7')
    region_path_280614 = series_280614.experiment.region_path
    region2_path_280614 = series_280614.experiment.region_path + '2'
    region_template = series_280614.experiment.templates.get(name='region')

    for file_name in [f for f in os.listdir(region_path_280614) if ('.DS' not in f and 'tiff' in f)]:

      # load each image
      img = tiff.imread(os.path.join(region_path_280614, file_name))

      # modify
      img_top = img[:,:,0]
      ones = np.ones(img_top.shape) * 255
      img = np.dstack([img_top,img_top,img_top])
      print(img.shape)

      # save to tiff in region 2
      tiff.imsave(os.path.join(region2_path_280614, file_name), img)
