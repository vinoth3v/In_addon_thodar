
class ThodarBoxThodarList(In.boxer.BoxLazy):
	
	parent_entity_type = 'Content'
	view_mode = 'default'
	limit = 25
	
	parent_entity_id = 0
	
	def __init__(self, data = None, items = None, **args):
		
		super().__init__(data, items, **args)
		
		self.id = '_'.join((self.__type__, self.parent_entity_type, str(self.parent_entity_id)))
		
		if IN.context.request.ajax_lazy:
			
			try:
				
				if not self.parent_entity_id:
					return
				
				entitier = IN.entitier
				texter = IN.texter
				
				nav_added = False
				list_added = False
				
				cursor = IN.db.execute('''SELECT 
					parent_entity_type,
					parent_entity_id
					FROM
						entity.thodar 
					WHERE
						entity_type = %(entity_type)s AND
						entity_id = %(entity_id)s AND
						parent_entity_id > 0
						''', {
					'entity_type' : self.parent_entity_type,
					'entity_id' : self.parent_entity_id,
				})
				
				if cursor.rowcount == 1:
					
					nav_added = True
					
					grid = self.add('TextDiv', {
						'css' : ['i-grid i-grid-divider'],
						'weight' : 1,
					})
					
					self.add('Hr', {
						'css' : ['i-grid-divider'],
						'weight' : 2,
					})
					
					l = grid.add('TextDiv', {
						'css' : ['i-width-1-3 i-text-center'],
						'weight' : 1,
					})
					
					c = grid.add('TextDiv', {
						'css' : ['i-width-1-3 i-text-center'],
						'weight' : 5,
					})
					
					row = cursor.fetchone()
					
					entity_id = row['parent_entity_id']
					entity_type = row['parent_entity_type']
					
					entity = entitier.load_single(entity_type, entity_id)
					
					if entity:
						
						entity_title = texter.format(entitier.entity_title(entity), 'nochange')

						if entity_title:
							
							c.add('Link', {
								'value' : '<i class="i-icon-arrow-circle-up"></i><br>' + entity_title,
								'href' : '/' + entitier.path(entity),
							})
					
					r = grid.add('TextDiv', {
						'css' : ['i-width-1-3 i-text-center'],
						'weight' : 10,
					})
					
					sql = '''WITH rows AS (
							select 
								ROW_NUMBER() OVER (ORDER BY weight, entity_id) AS rownumber, entity_id, entity_type
							from 
								entity.thodar 
							where 
								parent_entity_type = %(parent_entity_type)s AND
								parent_entity_id = %(parent_entity_id)s
							order by 
								weight, entity_id
						)
						select 
							p.entity_id as prev_id, 
							p.entity_type as prev_type,  
							n.entity_id as next_id,
							n.entity_type as next_type
						from rows
						left join (
							select * from rows
							where
								rownumber < (select rownumber from rows where entity_id = %(current_entity_id)s)
							order by rownumber desc
							limit 1
						) p ON rows.rownumber = p.rownumber 
						left join (
							select * from rows
							where
								rownumber > (select rownumber from rows where entity_id = %(current_entity_id)s)
							order by rownumber
							limit 1
						) n ON rows.rownumber = n.rownumber 
						where
							p.entity_id is not null OR
							n.entity_id is not null
						'''


					'''select (
							select entity_id from rows
							where
								rownumber < (select rownumber from rows where entity_id = %(current_entity_id)s)
							order by rownumber desc
							limit 1
						) as prev_id, 
						(
							select entity_type from rows
							where
								rownumber < (select rownumber from rows where entity_id = %(current_entity_id)s)
							order by rownumber desc
							limit 1
						) as prev_type, 
						(
							select entity_id from rows
							where
								rownumber > (select rownumber from rows where entity_id = %(current_entity_id)s)
							order by rownumber
							limit 1
						) as next_id, 
						(
							select entity_type from rows
							where
								rownumber > (select rownumber from rows where entity_id = %(current_entity_id)s)
							order by rownumber
							limit 1
						) as next_type
					'''
					cursor = IN.db.execute(sql, {
						'parent_entity_type' : self.parent_entity_type,
						'parent_entity_id' : entity_id,
						'current_entity_id' : self.parent_entity_id,
					})
				
					if cursor.rowcount > 0:
						
						for row  in cursor:
							
							prev_id = row['prev_id']
							next_id = row['next_id']
							prev_type = row['prev_type']
							next_type = row['next_type']
							
							if prev_id and prev_type:
								
								entity = entitier.load_single(prev_type, prev_id)
							
								if entity:
									
									entity_title = texter.format(entitier.entity_title(entity), 'nochange')

									if entity_title:
										
										l.add('Link', {
											'value' : '<i class="i-icon-arrow-circle-left"></i><br>' + entity_title,
											'href' : '/' + entitier.path(entity),
										})
										
							if next_id and next_type:
								
								entity = entitier.load_single(next_type, next_id)
							
								if entity:
									
									entity_title = texter.format(entitier.entity_title(entity), 'nochange')

									if entity_title:
										
										r.add('Link', {
											'value' : '<i class="i-icon-arrow-circle-right"></i><br>' + entity_title,
											'href' : '/' + entitier.path(entity),
										})

				cursor = IN.db.select({
					'table' : 'entity.thodar',
					'columns' : ['entity_type', 'entity_id', 'weight'],
					'where' : [
						['parent_entity_type', self.parent_entity_type],
						['parent_entity_id', self.parent_entity_id],
						['status', '>', 0], 
					],
					#'limit' : self.limit,
					'order' : 'weight',
				}).execute()

				if cursor.rowcount > 0:
					
					list_added = True

					ul = self.add('Ul', {
						'css' : ['i-nav i-nav-side'],
						'weight' : 5,
					})
					
					added = 1
					
					for result in cursor:
						
						entity_id = result['entity_id']
						entity_type = result['entity_type']
						
						entity = entitier.load_single(entity_type, entity_id)
						
						if entity:
							
							entity_title = texter.format(entitier.entity_title(entity), 'nochange')

							if entity_title:
								
								ul.add('Li', {
									'weight' : added,
								}).add('Link', {
									'value' : entity_title,
									'href' : '/' + entitier.path(entity),
								})
								added += 1
				
				if not nav_added and not list_added:
					self.title = ''
				
			except Exception as e:
				IN.logger.debug()

@IN.register('ThodarBoxThodarList', type = 'Themer')
class ThodarBoxThodarListThemer(In.boxer.BoxLazyThemer):
	''''''

	def theme_items(self, obj, format, view_mode, args):
		
		obj.css.append('i-panel i-panel-box')
		
		super().theme_items(obj, format, view_mode, args)
