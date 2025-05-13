from flask_restful import fields

user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'name': fields.String,
    'phone': fields.String,
    'avatar': fields.Url('static', absolute=True)
}

order_fields = {
    'id': fields.Integer,
    'total_price': fields.Float,
    'status': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601'),
    'items': fields.List(fields.Nested({
        'product_name': fields.String,
        'quantity': fields.Integer,
        'price': fields.Float
    }))
}