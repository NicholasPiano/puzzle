#woot.apps.img.models

#django
from django.db import models

#local
from apps.cell.models import Experiment

#util
import os
from scipy.misc import imread, imsave

### Models
class Composite(models.Model):
  ''' A 3D collection of chunks. '''
  #connections
  experiment = models.ForeignKey(Experiment, related_name='composites')

  #properties
  rows = models.IntegerField(default=0)
  columns = models.IntegerField(default=0)
  levels = models.IntegerField(default=0)
  timepoints = models.IntegerField(default=0)

  #methods
  def pixelate(self):
    #1. load all associated images and create pixel objects
    for image in self.images.all():
      print('processing %s' % image.path)
      parameter, parameter_created = self.parameters.get_or_create(name=image.channel.name)
      image.load()

      #loop over array
      rows, columns = image.array.shape
      for row in range(rows):
        for column in range(columns):
          #pixels are identified uniquely by spatial coordinates -> r,c,l,t
          pixel, created = self.pixels.get_or_create(source_image=image, row=row, column=column, level=image.level, timepoint=image.timepoint)

          #parameters
          pixel_parameter, pixel_parameter_created = pixel.parameters.get_or_create(parameter=parameter)
          pixel_parameter.value = int(image.array[row,column])
          pixel_parameter.save()
          pixel.save()

  def chunkify(self, chunk_size=(5,5,5)):
    #create chunk objects using dimensions of images
    pass

class Channel(models.Model):
  #connections
  experiment = models.ManyToManyField(Experiment, related_name='channels')

  #properties
  name = models.CharField(max_length=255)

class SourceImage(models.Model):
  '''
  Stores original details about the source images from which pixel objects and chunk objects are derived.

  An image can be uniquely identified by its full path. This must be checked before creating another image object.

  '''
  #connections
  experiment = models.ForeignKey(Experiment, related_name='images')
  composite = models.ForeignKey(Composite, related_name='images', null=True)
  channel = models.ForeignKey(Channel, related_name='images', null=True)

  #properties
  path = models.CharField(max_length=255)
  array = None

  timepoint = models.IntegerField(default=0)
  level = models.IntegerField(default=0)

  #methods
  def load(self):
    self.array = imread(self.path)

### Units
class Chunk(models.Model):
  ''' Subdivisions of an image of constant size, say 16x16x16. '''
  #connections
  composite = models.ForeignKey(Composite, related_name='chunks')

  #properties
  ''' n-dimension parameter space for chunks. '''
  #1. coordinates of chunk origin
  row = models.IntegerField(default=0)
  column = models.IntegerField(default=0)
  level = models.IntegerField(default=0)
  timepoint = models.IntegerField(default=0)

  #methods

class Pixel(models.Model):
  ''' Stores the n-dimensional parameters of a pixel at a set of spacial coordinates. '''
  #connections
  composite = models.ForeignKey(Composite, related_name='pixels')
  source_image = models.ForeignKey(SourceImage, related_name='pixels')
  chunk = models.ManyToManyField(Chunk, related_name='pixels')

  #properties
  row = models.IntegerField(default=0)
  column = models.IntegerField(default=0)
  level = models.IntegerField(default=0)
  timepoint = models.IntegerField(default=0)

  #methods

### Parameters
class Parameter(models.Model):
  ''' This mechanic is similar to the cell and cell_instance idea. '''
  #connections
  composite = models.ForeignKey(Composite, related_name='parameters')

  #properties
  name = models.CharField(max_length=255)

class ChunkParameter(models.Model):
  ''' Serves as one instance of a named parameter. '''
  #connections
  chunk = models.ForeignKey(Chunk, related_name='parameters')
  parameter = models.ForeignKey(Parameter, related_name='chunk_instances')

  #properties
  value = models.IntegerField(default=0)
  float_value = models.FloatField(default=0.0)
  boolean_value = models.BooleanField(default=False)

class PixelParameter(models.Model):
  #connections
  pixel = models.ForeignKey(Pixel, related_name='parameters')
  parameter = models.ForeignKey(Parameter, related_name='pixel_instances')

  #properties
  value = models.IntegerField(default=0)
  float_value = models.FloatField(default=0.0)
  boolean_value = models.BooleanField(default=False)
