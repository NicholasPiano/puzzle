# woot.apps.cell.models

# django
from django.db import models

# local
from apps.img.models import Experiment, Series
from apps.pix.models import Composite, Channel, Path

# util

### RECOGNITION STAGE
class RegionMask(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='region_masks')
  series = models.ForeignKey(Series, related_name='region_masks')
  path = models.ForeignKey(Path, related_name='region_masks')

  # properties
  mask_id = models.IntegerField(default=0)

class CellTrack(models.Model):
  # connections
  pass

  # properties

class CellMarker(models.Model):
  # connections
  pass

  # properties

class CellMask(models.Model): # cell mask is composite and channel dependent
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_masks')
  series = models.ForeignKey(Series, related_name='cell_masks')
  path = models.ForeignKey(Path, related_name='cell_masks')

  # properties
  mask_id = models.IntegerField(default=0)

### DATA STAGE #####
class Region(models.Model):
  passw

class RegionInstance(models.Model):

class Cell(models.Model):
  pass

class CellInstance(models.Model):
  pass
