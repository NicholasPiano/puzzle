# woot.apps.cell.models

# django
from django.db import models

# local
from apps.img.models import Experiment, Series, Path
from apps.pix.models import Composite, Channel

# util

### RECOGNITION STAGE
class RegionMask(models.Model):
  # connections
  experiment = models.ForeignKey(Experiment, related_name='region_masks')
  series = models.ForeignKey(Series, related_name='region_masks')
  path = models.ForeignKey(Path, related_name='region_masks')

  # properties
  mask_id = models.IntegerField(default=0)
  index = models.IntegerField(default=0)

  mask = None

  def load(self):
    # load image from path
    masks = self.path.load()

    # keep only the parts of the image that have the same id as mask
    masks[masks!=self.mask_id] = 0
    self.mask = masks==0
    return self.mask

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

class CellMask(models.Model): # cell mask is composite and channel dependent
  # connections
  experiment = models.ForeignKey(Experiment, related_name='cell_masks')
  series = models.ForeignKey(Series, related_name='cell_masks')
  path = models.ForeignKey(Path, related_name='cell_masks')

  # properties
  mask_id = models.IntegerField(default=0)
  index = models.IntegerField(default=0)

  mask = None

  def load(self):
    # load image from path
    masks = self.path.load()

    # keep only the parts of the image that have the same id as mask
    masks[masks!=self.mask_id] = 0
    self.mask = masks==0
    return self.mask

### DATA STAGE #####
class Region(models.Model):
  pass

class RegionInstance(models.Model):
  pass

class Cell(models.Model):
  pass

class CellInstance(models.Model):
  pass
