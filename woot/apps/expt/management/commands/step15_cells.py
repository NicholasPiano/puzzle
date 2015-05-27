# expt.command: step15_cells

# django
from django.core.management.base import BaseCommand, CommandError

# local
from apps.expt.models import Series
from apps.img.models import Gon
from apps.expt.util import *
from apps.expt.data import allowed_img_extensions

# util
import os
import subprocess
from optparse import make_option

### Command
class Command(BaseCommand):
  option_list = BaseCommand.option_list + (

    make_option('--expt', # option that will appear in cmd
      action='store', # no idea
      dest='expt', # refer to this in options variable
      default='050714-test', # some default
      help='Name of the experiment to import' # who cares
    ),

    make_option('--series', # option that will appear in cmd
      action='store', # no idea
      dest='series', # refer to this in options variable
      default='13', # some default
      help='Name of the series' # who cares
    ),

  )

  args = ''
  help = ''

  def handle(self, *args, **options):
    '''
    1. What does this script do?
    > Remotely run CellProfiler using a command line. I want to pretend that I am simply modding the images and creating a new channel.

    2. What data structures are input?
    > CP Pipeline file, Channel

    3. What data structures are output?
    > Nothing

    4. Is this stage repeated/one-time?
    > One-time per pipeline

    Steps:

    1. Search in pathfor batches
    2. For each batch, run command

    '''

    # 1. get path and batches
    series = Series.objects.get(experiment__name=options['expt'], name=options['series'])

    # 2. open spreadsheet
    for batch_number in os.listdir(os.path.join(series.experiment.output_path, series.name)):
      with open(os.path.join(series.experiment.output_path, series.name, batch_number, 'Nuclei.csv')) as spreadsheet:
        # get data
        lines = spreadsheet.readlines()
        titles = lines[0].split(',')
        data = [line.split(',') for line in lines[1:]]

        # for each line, create a cell and fill in the details
        for i,d in enumerate(data):
          print('step15 | processing line {}/{}...'.format(i,len(data)))
          # some data: d[titles.index('title')]

          # get gon for marker -> marker_id, track_id
          gon = Gon.objects.get(id_token=d[titles.index('Metadata_id_token')])
          marker = gon.marker
          track_id = gon.marker.track.track_id

          # create cell
          cell, cell_created = series.experiment.cells.get_or_create(series=series, cell_id=track_id, cell_index=series.experiment.cells.filter(cell_id=track_id).count())

          # create cell instance
          cell_instance, cell_instance_created = cell.cell_instances.get_or_create(experiment=cell.experiment, series=cell.series, region=marker.region, gon=gon)

          # populate fields
          cell_instance.z, cell_instance.t = marker.z, marker.t

          cell_instance.AreaShape_Area = float(d[titles.index('AreaShape_Area')])
          cell_instance.r = float(d[titles.index('AreaShape_Center_X')])
          cell_instance.c = float(d[titles.index('AreaShape_Center_Y')])
          cell_instance.AreaShape_Compactness = float(d[titles.index('AreaShape_Compactness')])
          cell_instance.AreaShape_Eccentricity = float(d[titles.index('AreaShape_Eccentricity')])
          cell_instance.AreaShape_EulerNumber = float(d[titles.index('AreaShape_EulerNumber')])
          cell_instance.AreaShape_Extent = float(d[titles.index('AreaShape_Extent')])
          cell_instance.AreaShape_FormFactor = float(d[titles.index('AreaShape_FormFactor')])
          cell_instance.AreaShape_MajorAxisLength = float(d[titles.index('AreaShape_MajorAxisLength')])
          cell_instance.AreaShape_MaximumRadius = float(d[titles.index('AreaShape_MaximumRadius')])
          cell_instance.AreaShape_MeanRadius = float(d[titles.index('AreaShape_MeanRadius')])
          cell_instance.AreaShape_MedianRadius = float(d[titles.index('AreaShape_MedianRadius')])
          cell_instance.AreaShape_MinorAxisLength = float(d[titles.index('AreaShape_MinorAxisLength')])
          cell_instance.AreaShape_Orientation = float(d[titles.index('AreaShape_Orientation')])
          cell_instance.AreaShape_Perimeter = float(d[titles.index('AreaShape_Perimeter')])
          cell_instance.AreaShape_Solidity = float(d[titles.index('AreaShape_Solidity')])
          cell_instance.Location_Center_X = float(d[titles.index('Location_Center_X')])
          cell_instance.Location_Center_Y = float(d[titles.index('Location_Center_Y')])

          # save
          cell_instance.save()
          cell.save()

      # 3. calculate cell velocities
      for cell in series.cells.all():
        previous_cell_instance = None
        for cell_instance in cell.cell_instances.order_by('t'):
          if previous_cell_instance is not None:
            cell_instance.vr = cell_instance.r - previous_cell_instance.r
            cell_instance.vc = cell_instance.c - previous_cell_instance.c
            cell_instance.vz = cell_instance.z - previous_cell_instance.z
          else:
            cell_instance.vr = 0
            cell_instance.vc = 0
            cell_instance.vz = 0

          previous_cell_instance = cell_instance

          cell_instance.save()
