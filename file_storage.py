import importlib
import pkgutil
import sys
import os

def member_names(members):
	for name, obj in members:
		print(name)

class NVPStrategy():

	def __init__(self, silent=True):
		self.silent = silent

	def read(self, components, filename):
		values = []
		for idx, component in enumerate(components):

			try:
				value = component.read(filename)
				values.append(value)
			except Exception as e:
				if not self.silent:
					print("Component %i failed reading\n%s" % (idx+1, e))
		
		# Get the most frequent value
		values_freq = dict()
		for value in values:
			values_freq[value] = values_freq.get(value, 0) + 1
		if len(values_freq.keys()) == 0:
			# No components were able to perform service
			return None
		else:
			return max(values_freq, key=values_freq.get)

	# Spaghetti zone
	def write(self, components, filename, value):
		lengths = []
		for idx, component in enumerate(components):
			
			# # [Measure memory]
			# before = tracemalloc.take_snapshot()

			try:
				length = component.write(filename, value)
				lengths.append((component, length))
			except Exception as e:
				if not self.silent:
					print("Component %i failed writing\n%s" % (idx+1, e))
			
			# # [Measure memory]
			# after = tracemalloc.take_snapshot()
			# diff = after.compare_to(before, 'filename')
		
		# Find correct output
		lengths_freq = dict()
		for _, length in lengths:
			lengths_freq[length] = lengths_freq.get(length, 0) + 1
		if len(lengths_freq.keys()) == 0:
			# No components were able to perform service
			return None
		plurality_length = max(lengths_freq, key=lengths_freq.get)
		final_component = next(component for component, length in lengths if length==plurality_length)
		final_component.write(filename, value)
		return plurality_length

class RBStrategy():

	def __init__(self, silent=True):
		self.silent = silent

	def read(self, components, filename):
		pass

	def write(self, components, filename, value):
		pass


class Baseline():

	def __init__(self, component, data_dir):
		self.component = component
		self.data_dir = data_dir

	def read(self, filename):
		path = os.path.join(self.data_dir, filename)
		try:
			result = self.component.read(path)
			return result
		except:
			return None

	def write(self, filename, value):
		path = os.path.join(self.data_dir, filename)
		try:
			self.component.write(path, value)
		except:
			return None


class FileStorage():

	def __init__(self, ft_strategy, components, data_dir):
		self.components = components
		self.data_dir = data_dir
		self.ft_strategy = ft_strategy

	def read(self, filename):
		path = os.path.join(self.data_dir, filename)
		return self.ft_strategy.read(self.components, path)

	def write(self, filename, value):
		path = os.path.join(self.data_dir, filename)
		return self.ft_strategy.write(self.components, path, value)
