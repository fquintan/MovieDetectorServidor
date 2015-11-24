from flask import jsonify
from flask import Flask
from flask import request
from subprocess import call
from flask import Response
from DescriptorParser import get_descriptor_parser

import PVCD_Wrapper

import os
#from flask import Flask, request
#, redirect, url_for

UPLOAD_FOLDER = '/home/felipe/Documents/memoria/Servidor/flask/query_videos'
ALLOWED_EXTENSIONS = set(['mp4'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def hello():
	return "Hello World!"


@app.route("/search/api/search_by_descriptor", methods=['POST'])
def search_by_descriptor():
	datos = request.get_json()
	detections = []
	if datos is not None:
		length = len(datos)
		app.logger.info('Length: %d', length)
		# app.logger.info(datos[0])
		db_name = 'query'
		descriptor_type = datos.get('type')
		descriptor_parser = get_descriptor_parser(descriptor_type, datos)
		app.logger.info('received %s descriptors of type %s' % (descriptor_parser.length, descriptor_parser.get_alias()))

		PVCD_Wrapper.create_database(db_name)
		PVCD_Wrapper.create_segmentation(db_name, descriptor_parser)
		PVCD_Wrapper.write_descriptors(db_name, descriptor_parser)
		PVCD_Wrapper.new_search_profile(db_name, descriptor_parser.get_alias())
		PVCD_Wrapper.search()
		detections = PVCD_Wrapper.detect()
		# detections = []
		# detections = [{'score': 2, 'reference': 'hello'}, {'score': 3, 'reference': 'world'}]
		app.logger.info(detections)

	return jsonify(detections=detections)

@app.route("/search/api/search_by_video_file", methods=['POST'])
def search_by_video_file():
	if request.method == 'POST':
		uploaded_file = request.files['uploaded_file']
		if uploaded_file and allowed_file(uploaded_file.filename):
			db_name = 'query'
			descriptor = request.form['descriptor']
			alias = request.form['alias']
			# filename = secure_filename(uploaded_file.filename)
			file_path = save_video_file(uploaded_file)
			PVCD_Wrapper.compute_descriptors(file_path, descriptor, alias)
			PVCD_Wrapper.new_search_profile(db_name, alias)
			PVCD_Wrapper.search()
			detections = PVCD_Wrapper.detect()

			return jsonify(detections=detections)


def save_video_file(file_to_save, directory=app.config['UPLOAD_FOLDER']):
	file_path = os.path.join(directory, file_to_save.filename)
	final_output = os.path.join(directory, 'query_video.mp4')
	file_to_save.save(file_path)
	call(['ffmpeg', '-y', '-i', file_path, '-ss', '00:00:00', '-t', '00:00:05',
		  '-async',  '1', '-strict', '-2', final_output])
	return final_output
# ffmpeg -i VID.mp4 -ss 00:00:00 -t 00:00:05 -async 1 -strict -2 cut.mp4

def allowed_file(filename):
	return True

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
