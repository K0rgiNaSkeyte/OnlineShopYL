from flask_restful import Resource, reqparse
from flask_login import login_required, current_user
from app.models import User, UserProfile
from app.decorators import admin_required
from app import db

class UserResource(Resource):
    @login_required
    def get(self, user_id):
        """Получение информации о пользователе"""
        # Проверяем, что пользователь запрашивает информацию о себе или является администратором
        if current_user.id != user_id and not current_user.is_admin:
            return {'error': 'Доступ запрещен'}, 403
            
        user = User.query.get_or_404(user_id)
        
        # Базовая информация о пользователе
        user_data = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'phone': user.phone,
            'is_admin': user.is_admin,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None
        }
        
        # Добавляем информацию из профиля, если он существует
        if hasattr(user, 'profile') and user.profile:
            user_data['profile'] = {
                'avatar': user.profile.avatar,
                'address': user.profile.address,
                'birth_date': user.profile.birth_date.strftime('%Y-%m-%d') if user.profile.birth_date else None,
                'bio': user.profile.bio
            }
        
        return user_data
    
    @admin_required
    def put(self, user_id):
        """Обновление информации о пользователе (только для администраторов)"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('phone', type=str)
        parser.add_argument('is_admin', type=bool)
        args = parser.parse_args()
        
        user = User.query.get_or_404(user_id)
        
        if args.get('name'):
            user.name = args['name']
        if args.get('phone'):
            user.phone = args['phone']
        if args.get('is_admin') is not None:
            user.is_admin = args['is_admin']
            
        db.session.commit()
        
        return {'message': 'Пользователь успешно обновлен'}