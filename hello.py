from flask import jsonify
from DescriptorParser import get_descriptor_parser

import PVCD_Wrapper

import os
from flask import Flask, request, redirect, url_for

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
		file = request.files['uploaded_file']
		if file and allowed_file(file.filename):
			db_name = 'query_db'
			alias = 'kf'
			# filename = secure_filename(file.filename)
			filename = file.filename
			file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(file_path)
			PVCD_Wrapper.compute_descriptors(file_path)
			PVCD_Wrapper.new_search_profile(db_name, alias)
			PVCD_Wrapper.search()
			detections = PVCD_Wrapper.detect()

			return jsonify(detections=detections)



def allowed_file(filename):
	return True

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
