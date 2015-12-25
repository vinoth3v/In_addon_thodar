
class Thodar:
	''''''
	
	def get_thodar_info(self, current_entity_type, current_entity_id):
		'''returns thodar record info.'''
		
		try:

			cursor = IN.db.select({
				'table' : 'entity.thodar',
				'columns' : [
					'parent_entity_type',
					'parent_entity_id',
					'weight',
					'level',
				],
				'where' : [
					['entity_type', current_entity_type],
					['entity_id', current_entity_id],
				],
			}).execute()

			if cursor.rowcount > 0:

				row = cursor.fetchone()

				parent_entity_type = row['parent_entity_type']
				parent_entity_id = row['parent_entity_id']
				weight = row['weight']
				level = row['level']
				
				return {
					'parent_entity_type' : parent_entity_type,
					'parent_entity_id' : parent_entity_id,
					'weight' : weight,
					'level' : level,
				}

		except Exception as e:
			IN.logger.debug()
		
	def get_previous_entity(self, parent_entity_type, parent_entity_id, current_entity_type, current_entity_id):
		'''returns previous entity of thodar'''
		
		try:
			
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
						p.entity_id as prev_entity_id, 
						p.entity_type as prev_entity_type
					from rows
					left join (
						select * from rows
						where
							rownumber < (select rownumber from rows 
								where 
									entity_type = %(current_entity_type)s AND
									entity_id = %(current_entity_id)s)
						order by rownumber desc
						limit 1
					) p ON rows.rownumber = p.rownumber 
					where
						p.entity_id is not null
					limit 1
					'''
					
			cursor = IN.db.execute(sql, {
				'parent_entity_type' : parent_entity_type,
				'parent_entity_id' : parent_entity_id,
				'current_entity_type' : current_entity_type,
				'current_entity_id' : current_entity_id,
			})
			
			if cursor.rowcount == 1:
				row = cursor.fetchone()
				
				prev_entity_type = row['prev_entity_type']
				prev_entity_id = row['prev_entity_id']
				
				entity = IN.entitier.load_single(prev_entity_type, prev_entity_id)
				
				return entity
			
		except Exception as e:
			IN.logger.debug()


@IN.hook
def In_app_init(app):

	IN.thodar = Thodar()

