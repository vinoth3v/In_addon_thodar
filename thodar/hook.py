import json
import datetime
from collections import OrderedDict


def thodar_form_alter(form, post, entity = None):
	
	entitier = IN.entitier
	texter = IN.texter

	thodar_name = IN.APP.config.thodar['name']
	s_thodar_name = s(thodar_name)
	
	if entity:
		current_entity_id = entity.id
		current_entity_type = entity.__type__
	else:
		current_entity_id = 0
		current_entity_type = 'Content'
	
	set = form.add('FieldSet', {
		'id' : 'thodarset',
		'title' : s(thodar_name),
		'css' : ['i-form-row'],
		'weight' : 40,
	})

	db_thodar = False
	parent_entity_type = ''
	parent_entity_id = 0
	weight = 0
	level = 0
	
	if entity:
		try:

			thodar_info = IN.thodar.get_thodar_info(current_entity_type, current_entity_id)
			
			if thodar_info:
				
				parent_entity_type = thodar_info['parent_entity_type']
				parent_entity_id = thodar_info['parent_entity_id']
				weight = thodar_info['weight']
				level = thodar_info['level']
				
				db_thodar = True

		except Exception as e:
			IN.logger.debug()
	
	if post:
		thodar = post.get('thodar', 0) == '1'
	else:
		thodar = db_thodar
	
	option_entity = None
	
	if thodar:
		
		thodar_type = post.get('thodar_type', None)
		thodarcontent = post.get('thodarcontent', None)
		thodar_weight = post.get('thodar_weight', None)
		
		if thodar_type is None:
			if not entity:
				thodar_type = 'new'
			else:
				
				if not parent_entity_type or not parent_entity_id:
					thodar_type = 'new'
				else:
					try:
						
						option_entity = IN.thodar.get_previous_entity(parent_entity_type, parent_entity_id, current_entity_type, current_entity_id)
						
						if not option_entity:
							# use parent
							
							option_entity = entitier.load_single(parent_entity_type, parent_entity_id)
							
							if option_entity:
								thodar_type = 'sub'
							
						else:
							
							thodar_type = 'thodar'
							
					except Exception as e:
						IN.logger.debug()
		
		elif thodar_type == 'sub' or thodar_type == 'thodar':
			
			# use the form posted value if available
			if thodarcontent and thodarcontent.isnumeric():
				t_entity = entitier.load_single(current_entity_type, thodarcontent)
				if t_entity:
					option_entity = t_entity
			
			# or use db value
			if not option_entity and parent_entity_type and parent_entity_id:
				if thodar_type == 'sub':
					option_entity = entitier.load_single(parent_entity_type, parent_entity_id)
				elif thodar_type == 'thodar':
					option_entity = IN.thodar.get_previous_entity(parent_entity_type, parent_entity_id, current_entity_type, current_entity_id)
		
		if thodar_type is None:
			# something went wrong
			thodar = False
	
	
	set.add('CheckBox', {
		'label' : s('{thodar} content?', {'thodar' : s_thodar_name}),
		'id' : 'thodar',
		'value' : 1,	# returned value if checked
		'checked' : thodar,
		'info' : s('Check this if this content is a {thodar}.', {'thodar' : s_thodar_name}),
		'weight' : 0,
		'css' : ['ajax'],
		'attributes' : {'data-ajax_partial' : 1},
	})

	form.ajax_elements.append('thodarset')
	
	if thodar:
		
		set = set.add('FieldSet', {
			'id' : 'thodartypeset',
			'css' : ['i-form-row i-margin-left'],
			'weight' : 1,
		})

		options = OrderedDict()
		options['new'] = {
			'label' : s('This is a new {thodar}', {'thodar' : s_thodar_name}),
		}
		options['thodar'] = {
			'label' : s('Add this as a continuity to another content'),
			'info' : s('Part 3 may be a continuity to Part 2')
		}
		options['sub'] = {
			'label' : s('Add this as a sub of another content'),
			'info' : s('Part 3.1 may be a sub of Part 3')
		}

		set.add('RadioBoxes', {
			'id' : 'thodar_type',
			'name' : 'thodar_type',
			'options' : options,
			'value' : thodar_type,
			'css' : ['i-width-1-1 i-form-large'],
			'weight' : 1,
			'child_additional_data' : {
				'css' : ['ajax'],
				'attributes' : {'data-ajax_partial' : 1},
			}
		})

		
		if thodar_type != 'new':
			
			set = set.add('FieldSet', {
				'id' : 'thodarcontentset',
				'css' : ['i-form-row i-margin-left'],
				'weight' : 3,
			})
			
			if thodar_type == 'sub':
				thodarcontent_info = s('The content will be added under the selected content.')
				thodarcontent_title = s('Under which content?')
			else:
				thodarcontent_info = s('The content will be the continuity of the selected content.')
				thodarcontent_title = s('Continuity of which content?')
			
			thodarcontent_options = {}
			thodarcontent_value = None
			
			#if thodarcontent and thodarcontent.isnumeric():
				
				#t_entity = entitier.load_single(current_entity_type, thodarcontent)
				
				#if t_entity:
					#option_entity = t_entity
			
			if option_entity:
				thodarcontent_value = option_entity.id
				
				thodarcontent_options = {
					option_entity.id : texter.format(entitier.entity_title(option_entity), 'nochange')
				}
			
			if entity:
				extra = {
					'content_type' : current_entity_type,
					'nabar_id' : entity.nabar_id,
					'exclude' : {
						'content_type' : current_entity_type,
						'entity_id' : current_entity_id,
					}
				}
			else:
				extra = {
					'content_type' : current_entity_type,
				}
			
			set.add('HTMLSelect', {
				'id' : 'thodarcontent',
				'name' : 'thodarcontent',
				'title' : thodarcontent_title,
				'value' : thodarcontent_value,
				'options' : thodarcontent_options,
				'css' : ['autocomplete i-width-1-1'], # ajax
				'multiple' : False,
				'required' : True,
				'validation_rule' : ['NotEmpty', 'Content is required.'],
				'attributes' : {
					#'data-ajax_partial' : 1,
					'data-autocomplete_max_items' : 1,
					'data-autocomplete_create' : '0',
					'data-autocomplete_url' : ''.join(('/thodar/autocomplete')),
					'data-autocomplete_url_data' : json.dumps(extra, skipkeys = True, ensure_ascii = False),
				},
				'info' : thodarcontent_info,
				'weight' :  1,
			})
			
			if thodar_type == 'sub':
				
				if weight == 0 and thodar_weight is None and parent_entity_type and parent_entity_id:
					#'weight' # max weight + 1
					cursor = IN.db.select({
						'table' : 'entity.thodar',
						'columns' : ['max(weight) as weight'],
						'where' : [
							['parent_entity_type', parent_entity_type],
							['parent_entity_id', parent_entity_id],
						],
					}).execute()

					if cursor.rowcount == 1:
						thodar_weight = cursor.fetchone()['weight'] or -1
						thodar_weight += 1
				
				set.add('TextBoxNumber', {
					'id' : 'thodar_weight',
					'title' : s('Weight'),
					'value' : thodar_weight or weight,
					'css' : ['i-form-large'],
					'weight' : 2,
					'info' : s('In which position this content should be added?'),
				})
				


def thodar_form_process_submit(form, post, entity):
	''''''
	
	try : 
		
		if form.has_errors:
			return
		
		thodar = form['thodarset']['thodar'].checked
		
		db = IN.db
		
		if not thodar:
			
			# remove thodar
			cursor = db.delete({
				'table' : 'entity.thodar',
				'where' : [
					['entity_type', entity.__type__],
					['entity_id', entity.id],
				]
			}).execute()
			db.connection.commit()
			
			return
			
		parent_entity_id = 0
		weight = 0
		level = 0
		
		thodar_type = form['thodarset']['thodartypeset']['thodar_type'].value
		
		if thodar_type != 'new':
			thodarcontent_id = form['thodarset']['thodartypeset']['thodarcontentset']['thodarcontent'].value
			if not thodarcontent_id:
				thodarcontent_id = 0
				
			
			if thodar_type == 'sub':
				weight = form['thodarset']['thodartypeset']['thodarcontentset']['thodar_weight'].value
				if weight is None:
					weight = 0
				elif type(weight) is str:
					if weight.isnumeric():
						weight = int(weight)
					else:
						weight = 0
				
				
		else:
			thodarcontent_id = 0
			
		
		
		# test if exists
		cursor = IN.db.select({
			'table' : 'entity.thodar',
			'columns' : [
				'parent_entity_type',
				'parent_entity_id',
				'weight',
				'level',
			],
			'where' : [
				['entity_type', entity.__type__],
				['entity_id', entity.id],
			],
		}).execute()
		
		if cursor.rowcount > 0:
			# update
			
			set = [
				['parent_entity_type', entity.__type__],
			]
			
			if thodar_type == 'new':
				set += [
					['parent_entity_id', parent_entity_id],
					['weight', weight],
					['level', level],
				]
			elif thodar_type == 'sub':
				
				parent_entity_id = thodarcontent_id
				
				parent_thodar_info = IN.thodar.get_thodar_info(entity.__type__, parent_entity_id)
				if parent_thodar_info:
					level = parent_thodar_info['level'] + 1
					
				set += [
					['parent_entity_id', parent_entity_id], # sub of selected's
					['weight', weight],
					['level', level],
				]
				
			else:
				
				thodar_thodar_info = IN.thodar.get_thodar_info(entity.__type__, thodarcontent_id)
				if thodar_thodar_info:
					parent_entity_id = thodar_thodar_info['parent_entity_id']
					weight = thodar_thodar_info['weight'] + 1
					level = thodar_thodar_info['level']
					
					# if no parent, add as sub
					if not parent_entity_id:
						parent_entity_id = thodarcontent_id
						level += 1
						
						#'weight' # total child + 1
						cursor = IN.db.select({
							'table' : 'entity.thodar',
							'columns' : ['max(weight) as weight'],
							'where' : [
								['parent_entity_type', entity.__type__],
								['parent_entity_id', parent_entity_id],
							],
						}).execute()

						if cursor.rowcount == 1:
							weight = cursor.fetchone()['weight'] or -1
							weight += 1
							
				set += [
					['parent_entity_id', parent_entity_id], # sub of selected's parent
					['weight', weight],
					['level', level],
				]
			
			cursor = IN.db.update({
				'table' : 'entity.thodar',
				'set' : set,
				'where' : [
					['entity_type', entity.__type__],
					['entity_id', entity.id],
				],
			}).execute()
			
			db.connection.commit()
			
		else:
			# insert
			
			now = datetime.datetime.now()
			
			
			values = [
				entity.__type__, 	#'type',
				now, 				#'created',
				1, 					#'status',
				entity.nabar_id,	#'nabar_id',
				entity.__type__, 	#'entity_type',
				entity.id, 			#'entity_id',
				entity.__type__,	#'parent_entity_type',						
			]
			
			if thodar_type == 'sub':
				
				#'parent_entity_id',
				parent_entity_id = thodarcontent_id
				
				parent_thodar_info = IN.thodar.get_thodar_info(entity.__type__, parent_entity_id)
				if parent_thodar_info:
					#'level',
					level = parent_thodar_info['level'] + 1
				
				##'weight' # max weight + 1
				#cursor = IN.db.select({
					#'table' : 'entity.thodar',
					#'columns' : ['max(weight) as weight'],
					#'where' : [
						#['parent_entity_type', entity.__type__],
						#['parent_entity_id', parent_entity_id],
					#],
				#}).execute()

				#if cursor.rowcount == 1:
					#weight = cursor.fetchone()['weight'] or -1
					#weight += 1
					
			elif thodar_type == 'thodar':
				
				thodar_thodar_info = IN.thodar.get_thodar_info(entity.__type__, thodarcontent_id)
				if thodar_thodar_info:
					#'parent_entity_id',
					parent_entity_id = thodar_thodar_info['parent_entity_id']
					
					#'weight'
					weight = thodar_thodar_info['weight'] + 1
					#'level',
					level = thodar_thodar_info['level']
					
					# if no parent, add as sub
					if not parent_entity_id:
						parent_entity_id = thodarcontent_id
						level += 1
						
						#'weight' # total child + 1
						cursor = IN.db.select({
							'table' : 'entity.thodar',
							'columns' : ['max(weight) as weight'],
							'where' : [
								['parent_entity_type', entity.__type__],
								['parent_entity_id', parent_entity_id],
							],
						}).execute()

						if cursor.rowcount == 1:
							weight = cursor.fetchone()['weight'] or -1
							weight += 1
					
			else:
				# new
				pass
			
			values += [parent_entity_id, weight, level]
			
			cursor = IN.db.insert({
				'table' : 'entity.thodar',
				'columns' : [
					'type',
					'created',
					'status',
					'nabar_id',
					'entity_type',
					'entity_id',
					'parent_entity_type',
					'parent_entity_id',
					'weight',
					'level',
				]
			}).execute([values])
			
			db.connection.commit()
			
	except Exception as e:
		IN.logger.debug()



@IN.hook
def form_load_ContentAddForm(form, post, args):
	
	thodar_form_alter(form, post)
	
	
@IN.hook
def form_load_ContentEditForm(form, post, args):
	
	thodar_form_alter(form, post, form.entity)
	


@IN.hook
def form_process_ContentAddForm_validate(form, post):
	''''''
	
	
@IN.hook
def form_process_ContentEditForm_validate(form, post):
	''''''
	


@IN.hook
def form_process_ContentAddForm_submit(form, post):
	''''''
	
	entity = form.processed_data['entity']
	thodar_form_process_submit(form, post, entity)
	

@IN.hook
def form_process_ContentEditForm_submit(form, post):
	''''''
	
	entity = form.processed_data['entity']
	thodar_form_process_submit(form, post, entity)
	