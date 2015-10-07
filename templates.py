__author__ = 'felipe'


database_template = '#PVCD::FilesDB=1.0\n \
#type	id	path	filesize	width	height	timeStart	timeEnd	fps	num_transforms	transforms(name,preprocess)...\n \
V	$filename	si	1	1	1	0	2	2\n '


descriptor_template = '#PVCD::DescriptorData=1.2\n\
descriptor=$descriptor_kind\n\
segmentation=$segmentation\n\
descriptor_type=ARRAY_UCHAR\n\
array_length=$array_length\n\
num_subarrays=4\n\
subarray_length=64\n\
single_file=FALSE'