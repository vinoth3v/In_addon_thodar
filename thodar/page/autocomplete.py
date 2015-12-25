
def action_thodar_autocomplete(context, action, query, **args):
	
	returns = []
	
	query = query.replace('%', '').replace("'", '')
	
	nabar_id = context.nabar.id
	
	
	
	try:
		
		query_get = context.request.args['query']
		
		content_type = query_get.get('content_type', 'Content')
		nabar_id = query_get.get('nabar_id', nabar_id)
		exclude_id = query_get.get('exclude', {}).get('entity_id', None)
		
		db = IN.db
		texter = IN.texter
		
		connection = db.connection

		limit = 10
		
		# TODO: make it dynamic
		if exclude_id is None:
			sql = '''SELECT 
						f.value, 
						f.entity_id
					FROM
						entity.thodar t
					INNER JOIN 
						entity.content c ON t.entity_id = c.id 
					INNER JOIN 
						field.field_title f ON c.id = f.entity_id
					WHERE
						t.entity_type = %(content_type)s AND
						c.nabar_id = %(nabar_id)s  AND
						c.status > 0 AND	
						f.value LIKE %(query)s
					ORDER BY
						f.value
					LIMIT %(limit)s
				'''
		else:
			sql = '''SELECT 
						f.value, 
						f.entity_id
					FROM
						entity.thodar t
					INNER JOIN 
						entity.content c ON t.entity_id = c.id 
					INNER JOIN 
						field.field_title f ON c.id = f.entity_id
					WHERE
						t.entity_type = %(content_type)s AND
						c.nabar_id = %(nabar_id)s  AND
						c.status > 0 AND	
						f.value LIKE %(query)s AND
						t.entity_id != %(exclude_id)s
					ORDER BY
						f.value
					LIMIT %(limit)s
				'''
		cursor = db.execute(sql, {
			'content_type' : content_type,
			'nabar_id' : nabar_id,
			'limit' : limit,
			'query' : query.join(('%', '%')),
			'exclude_id' : exclude_id
		})
		
		if cursor.rowcount >= 0:
			for row in cursor:
				returns.append({
					'id' : row['entity_id'],
					'text' : texter.format(row['value'], 'nochange')
				})
				
	except:
		IN.logger.debug()
	
	context.response = In.core.response.JSONResponse(output = returns)
	