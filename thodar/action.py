from .page import *

@IN.hook
def actions():
	actns = {}

	actns['thodar/autocomplete/{query}'] = {
		'title' : 'thodar autocomplete',
		'handler' : action_thodar_autocomplete,
	}
	
	return actns