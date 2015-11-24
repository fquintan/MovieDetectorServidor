__author__ = 'felipe'
from subprocess import call
from string import Template
import templates
import os
import shutil
from array import array
import json

path_to_pvcd = '/home/felipe/Documents/memoria/Servidor/multimedia_tools/instalacion/bin/'
path_to_databases = '/home/felipe/Documents/memoria/Servidor/flask/databases/'
pvcd_db = path_to_pvcd + 'pvcd_db'
pvcd_search = path_to_pvcd + 'pvcd_search'
pvcd_detect = path_to_pvcd + 'pvcd_detect'
pvcd_new_db = pvcd_db + ' -new -db '


def create_database(name):
	""" Creates a dummy database with one file for querys """
	template = Template(templates.database_template)
	content = template.substitute(filename=name)
	filename = 'databases/' + name + '_db/files.txt'
	if not os.path.exists(os.path.dirname(filename)):
		os.makedirs(os.path.dirname(filename))
	with open(filename, 'w+') as db_file:
		db_file.write(content)
	return


def create_segmentation(db_name, descriptor_parser):
	filename = 'databases/' + db_name + '_db/segmentations/SEGCTE_0.25/segmentation.des'
	content = '#PVCD::SegmentationData=1.0\nsegmentation=SEGCTE_0.25\n'
	# First create the segmentation.des file which is the same for every query
	if not os.path.exists(os.path.dirname(filename)):
		os.makedirs(os.path.dirname(filename))
	with open(filename, 'w+') as db_file:
		db_file.write(content)

	# Then create the .seg file with the information from the descriptors
	filename = 'databases/' + db_name + '_db/segmentations/SEGCTE_0.25/' + db_name + '.seg'
	if not os.path.exists(os.path.dirname(filename)):
		os.makedirs(os.path.dirname(filename))
	with open(filename, 'w+') as seg_file:
		for line in descriptor_parser.get_segmentation():
			seg_file.write(line)

	return


def write_descriptors(db_name, descriptor_parser):
	filename = 'databases/' + db_name + '_db/descriptors/' + descriptor_parser.get_alias() + '/descriptor.des'
	if not os.path.exists(os.path.dirname(filename)):
		os.makedirs(os.path.dirname(filename))
	with open(filename, 'w+') as db_file:
		db_file.write(descriptor_parser.get_descriptor_options())

	filename = 'databases/' + db_name + '_db/descriptors/' + descriptor_parser.get_alias() + '/' + db_name + '.bin'
	descriptor_parser.write_descriptors(filename)
	return


def new_search_profile(db_name, descriptor_alias):
	db_directory = path_to_databases + 'buscar'
	if os.path.exists(db_directory):
		shutil.rmtree(db_directory)
	db_path = db_name + '_db'

	call([pvcd_search, '-new', '-profile', 'buscar', '-query', db_path, '-reference',\
		  'videos_db2', '-desc', descriptor_alias, '-distance', 'L1'], cwd='/home/felipe/Documents/memoria/Servidor/flask/databases')
	return


def search():
	call([pvcd_search, '-ss', '-profile', 'buscar', '-knn', '3'], cwd='/home/felipe/Documents/memoria/Servidor/flask/databases')
	return


def detect():
	status = call([pvcd_detect, '-detect', '-ss', 'buscar\ss,segments-knn_3.txt', '-minLength', '1s', '-out', 'detections.txt'], cwd='/home/felipe/Documents/memoria/Servidor/flask/databases')
	detections=[]
	with open('databases/detections.txt') as f:
		detection = {}
		for line in f:
			items = line.split('\t')
			if is_number(items[0]):
				detection['score'] = items[0]
				detection['reference'] = items[4]
				detections.append(detection)
	return detections


def compute_descriptors(video_filepath, descriptor, alias):
	"""
	@type video_filepath: str
	@type descriptor: str
	@type alias: str
	"""
	db_directory = path_to_databases + 'query_db'
	if os.path.exists(db_directory):
		shutil.rmtree(db_directory)

	call([pvcd_db, '-new', '-db', 'query_db', video_filepath], cwd='/home/felipe/Documents/memoria/Servidor/flask/databases')
	call([pvcd_db, '-segment', '-db', 'query_db', '-seg', 'SEGCTE_0.25'], cwd='/home/felipe/Documents/memoria/Servidor/flask/databases')
	call([pvcd_db, '-extract', '-db', 'query_db', '-seg', 'SEGCTE_0.25', '-desc', descriptor, '-alias', alias],
		 cwd='/home/felipe/Documents/memoria/Servidor/flask/databases')


def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False
