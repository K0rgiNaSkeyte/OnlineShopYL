from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

account_bp = Blueprint('account', __name__, url_prefix='/account')


@account_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        try:
            # Обновление основных данных
            current_user.name = form.name.data
            current_user.phone = form.phone.data

            # Обработка аватара
            if form.avatar.data:
                filename = secure_filename(form.avatar.data.filename)
                avatar_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'avatars',
                    f'user_{current_user.id}_{filename}'
                )
                form.avatar.data.save(avatar_path)
                if not current_user.profile:
                    current_user.profile = UserProfile(user_id=current_user.id)
                current_user.profile.avatar = avatar_path

            # Обновление адреса
            if form.address.data:
                if not current_user.profile:
                    current_user.profile = UserProfile(user_id=current_user.id)
                current_user.profile.address = form.address.data

            db.session.commit()
            flash('Профиль успешно обновлен', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating profile: {str(e)}')
            flash('Ошибка при обновлении профиля', 'danger')

    return render_template('account/profile.html', form=form)


@account_bp.route('/orders')
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id) \
        .order_by(Order.created_at.desc()) \
        .paginate(page=page, per_page=10)
    return render_template('account/orders.html', orders=orders)


@account_bp.route('/orders/<int:order_id>')
@login_required
def order_details(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('account/order_details.html', order=order)


@account_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Пароль успешно изменен', 'success')
            return redirect(url_for('account.profile'))
        else:
            flash('Неверный текущий пароль', 'danger')

    return render_template('account/change_password.html', form=form)