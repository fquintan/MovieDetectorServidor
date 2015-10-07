from flask import Flask
from flask import jsonify
from flask import request
from flask import Response

import PVCD_Wrapper

app = Flask(__name__)


@app.route("/")
def hello():
	return "Hello World!"


@app.route("/search/api/search_by_descriptor", methods=['POST'])
def search_by_descriptor():
	datos = request.get_json()
	if datos is not None:
		length = len(datos)
		app.logger.info('Length: %d', length)
		# app.logger.info(datos[0])
		PVCD_Wrapper.create_database('query')
		PVCD_Wrapper.create_segmentation('query', datos)
		PVCD_Wrapper.write_descriptors('query', datos)
		# return jsonify(datos)
		return 'aaa'
	return 'No se recibieron datos'


if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
