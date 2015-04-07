# apps.img.util

# django

# local

# util
import numpy as np


def cut_to_black(array):
  # coordinates of non-black
  r0 = np.argmax(np.any(array, axis=1))
  r1 = array.shape[0] - np.argmax(np.any(array, axis=1)[::-1])
  c0 = np.argmax(np.any(array, axis=0))
  c1 = array.shape[1] - np.argmax(np.any(array, axis=0)[::-1])

  # return cut
  return array[r0:r1,c0:c1]
