from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from DescriptorParser import get_descriptor_parser
import json

import PVCD_Wrapper

app = Flask(__name__)


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

		PVCD_Wrapper.create_database(db_name)
		PVCD_Wrapper.create_segmentation(db_name, descriptor_parser)
		PVCD_Wrapper.write_descriptors(db_name, descriptor_parser)
		PVCD_Wrapper.new_search_profile(db_name)
		PVCD_Wrapper.search()
		detections = PVCD_Wrapper.detect()
		# detections = []
		# detections = [{'score': 2, 'reference': 'hello'}, {'score': 3, 'reference': 'world'}]
		app.logger.info(detections)

	return jsonify(detections=detections)


if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
