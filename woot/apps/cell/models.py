# woot.apps.cell.models

# django
from django.db import models

# local
from apps.img.models import Experiment, Series
from apps.pix.models import Composite, Channel, Gon

# util

### RECOGNITION STAGE
class CellTrack(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_tracks')
  series = models.ForeignKey(Series, related_name='cell_tracks')

  # properties
  track_id = models.IntegerField(default=0)
  index = models.IntegerField(default=0)

class CellMarker(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_markers')
  series = models.ForeignKey(Series, related_name='cell_markers')
  track = models.ForeignKey(CellTrack, related_name='markers')

  # properties
  r = models.IntegerField(default=0)
  c = models.IntegerField(default=0)
  t = models.IntegerField(default=0)

class Mask(models.Model): # cell mask is composite and channel dependent
  # connections
  composite = models.ForeignKey(Composite, related_name='masks')
  channel = models.ForeignKey(Channel, related_name='masks')
  gon = models.ForeignKey(Gon, related_name='masks')

  # properties
  mask_id = models.IntegerField(default=0)

  mask = None

class MaskPath(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='mask_paths')
  series = models.ForeignKey(Series, related_name='mask_paths')

  # properties
  url = models.CharField(max_length=255)
  file_name = models.CharField(max_length=255)
  t = models.IntegerField(default=0)
  z = models.IntegerField(default=0)

### DATA STAGE #####
class Region(models.Model):
  pass

class RegionInstance(models.Model):
  pass

class Cell(models.Model):
  pass

class CellInstance(models.Model):
  pass
