__author__ = 'felipe'
from abc import ABCMeta, abstractmethod
from string import Template
from array import array
import templates
import json


class DescriptorParser:
	__metaclass__ = ABCMeta

	def __init__(self, descriptor_data):
		self.length = descriptor_data.get('length')
		self.options = json.loads(descriptor_data.get('options'))
		self.descriptors = json.loads(descriptor_data.get('descriptors'))
		self.type = descriptor_data.get('type')

	def get_segmentation(self):
		yield '#PVCD::FileSegmentation=1.1\n'
		yield str(self.length) + '\t24.0\n'
		frames_start = [descriptor.get('frameNumber') for descriptor in self.descriptors]
		frames_last = [x-1 for x in frames_start[1:] + [frames_start[-1]+2]]
		timestamps = [descriptor.get('timestamp')/1000.0 for descriptor in self.descriptors]
		time_steps = [y-x for x, y in zip(timestamps[:-1], timestamps[1:])] + [0.1]
		for start, end, timestamp, time_step in zip(frames_start, frames_last, timestamps, time_steps):
			middle = (start + end) / 2
			line = []
			line.append(str(start))
			line.append(str(middle))
			line.append(str(end))
			line.append(str(timestamp))
			line.append(str(timestamp + (time_step / 2)))
			line.append(str(timestamp + time_step) + '\n')
			separator = '\t'
			yield separator.join(line)

	def fill_descriptor_template(self, descriptor_kind, segmentation, array_length, num_subarrays, subarray_length, array_kind):
		template = Template(templates.descriptor_template)
		content = template.substitute(descriptor_kind=descriptor_kind,
								  segmentation=segmentation,
								  array_length=array_length,
								  num_subarrays=num_subarrays,
								  subarray_length=subarray_length,
								  array_kind=array_kind)
		return content

	def write_descriptors(self, filename):
		output_file = open(filename, 'wb')
		for descriptor in self.descriptors:
			descriptor_array = descriptor.get('descriptor')
			data_type = self.get_data_type()
			data_array = array(data_type, descriptor_array)
			data_array.tofile(output_file)
		output_file.close()
		return


	@abstractmethod
	def get_descriptor_options(self):
		pass

	@abstractmethod
	def get_data_type(self):
		pass

	@abstractmethod
	def get_alias(self):
		pass


class GrayHistogramParser(DescriptorParser):
	def get_alias(self):
		return 'ghd'

	def get_data_type(self):
		if self.quant == '1U':
			return 'B'
		else:
			return 'f'

	def __init__(self, descriptor_data):
		super(GrayHistogramParser, self).__init__(descriptor_data)
		self.zones_x = self.options.get('zones_x')
		self.zones_y = self.options.get('zones_y')
		self.bins = self.options.get('bins')
		self.quant = str(self.options.get('quant'))

	def get_descriptor_options(self):
		if self.quant == '1U':
			array_kind = 'ARRAY_UCHAR'
		else:
			array_kind = 'ARRAY_FLOAT'
		descriptor_kind = 'HISTGRAY_' + str(self.zones_x) + '_' + str(self.zones_y) + '_' + self.quant + '_' + str(self.bins)
		segmentation = 'SEGCTE_0.25'
		array_length = str(self.zones_y * self.zones_x * self.bins)
		num_subarrays = str(self.zones_y * self.zones_x)
		subarray_length = str(self.bins)
		return self.fill_descriptor_template(descriptor_kind, segmentation, array_length,
											 num_subarrays, subarray_length, array_kind)


class KeyframeParser(DescriptorParser):
	def get_alias(self):
		return 'kf'

	def __init__(self, descriptor_data):
		super(KeyframeParser, self).__init__(descriptor_data)
		self.height = self.options.get('height')
		self.width = self.options.get('width')
		self.colorspace = self.options.get('colorspace')
		self.quant = self.options.get('quant')

	def get_data_type(self):
		if self.quant == '1U':
			return 'B'
		else:
			return 'f'

	def get_descriptor_options(self):
		if self.quant == '1U':
			array_kind = 'ARRAY_UCHAR'
		else:
			array_kind = 'ARRAY_FLOAT'
		descriptor_kind = 'KF_' + str(self.width) + 'x' + str(self.height) + '_' + self.colorspace + '_' + str(self.quant)
		segmentation = 'SEGCTE_0.25'
		array_length = str(self.height * self.width * 3)
		num_subarrays = str(self.height * self.width)
		subarray_length = str(3)
		return self.fill_descriptor_template(descriptor_kind, segmentation, array_length,
											 num_subarrays, subarray_length, array_kind)


def get_descriptor_parser(descriptor_type, descriptor_data):
	if descriptor_type == 'GrayHistogram':
		return GrayHistogramParser(descriptor_data)
	elif descriptor_type == 'Keyframe':
		return KeyframeParser(descriptor_data)