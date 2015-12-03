import PVCD_Wrapper
import os

def perform_query(db_name, descriptor_alias, results):
		"""
			@type results: dict
			@type descriptor_alias: str
			@type db_name: str
		"""
		PVCD_Wrapper.new_search_profile(db_name, descriptor_alias)
		PVCD_Wrapper.search()
		detections = PVCD_Wrapper.detect()
		results[db_name] = detections


def get_immediate_subdirectories(a_dir, prefix):
	return [name[:-3] for name in os.listdir(a_dir)
			if os.path.isdir(os.path.join(a_dir, name))
			and name.startswith(prefix)]

current_dir = '/home/felipe/Documents/memoria/Servidor/flask/databases'
descriptors_alias = ['ghd', 'ehd', 'kf']
items = '119'
for descriptor_alias in descriptors_alias:
	results = {}
	output_filename = 'results_' + descriptor_alias + '_' + items + '.txt'
	for database in get_immediate_subdirectories(current_dir, descriptor_alias):
		perform_query(database, descriptor_alias, results)

	out = open(output_filename, 'w')
	for name, res in results.iteritems():
		out.write(name + '-->' + str(res)+'\n')
	out.close()