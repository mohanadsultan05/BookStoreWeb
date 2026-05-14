from flask import jsonify


def success_response(data=None, message='Success', status_code=200):
    response = {'success': True, 'message': message}
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


def error_response(message='An error occurred', status_code=400, details=None):
    response = {'success': False, 'error': message}
    if details:
        response['details'] = details
    return jsonify(response), status_code


def paginate_query(query, page, per_page=12):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }
