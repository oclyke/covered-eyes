class FftPlan:
  def __init__(self, buffers, sample_frequency):
    input_buffer, output_buffer = buffers
    self._input_buffer = input_buffer
    self._output_buffer = output_buffer
    self._sample_frequency = sample_frequency

class FloatBuffer():
  def __init__(self, n):
    self._n = n
  
  def __len__(self):
    return self._n
  
  def reference(self, window=None):
    if window is not None:
      min_bin, max_bin = window
    return self

def bin_stats():
  pass

def reshape(config, input, output=None):
  if output is None:
    return 1
  return None
