from flask import jsonify


def success_response(data=None, message='', status_code=200):
    """Успешный JSON-ответ"""
    response = {
        'success': True,
        'message': message,
        'data': data
    }
    return jsonify(response), status_code


def error_response(message='', status_code=400, errors=None):
    """Ошибка в JSON-формате"""
    response = {
        'success': False,
        'message': message,
        'errors': errors or {}
    }
    return jsonify(response), status_code


def paginated_response(query, schema, page=1, per_page=20):
    """Форматирование ответа с пагинацией"""
    paginated = query.paginate(page=page, per_page=per_page)
    return {
        'items': schema.dump(paginated.items),
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page
    }
