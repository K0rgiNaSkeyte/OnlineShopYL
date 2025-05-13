import os
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}


def allowed_file(filename):
    """Проверка расширения файла"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, subfolder=''):
    """Сохранение загруженного файла"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)

        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        # Оптимизация изображения
        if filename.lower().endswith(('jpg', 'jpeg', 'png')):
            optimize_image(filepath)

        return filename
    return None


def optimize_image(filepath, max_size=(1200, 1200), quality=85):
    """Оптимизация изображения"""
    try:
        img = Image.open(filepath)
        img.thumbnail(max_size)
        img.save(filepath, quality=quality, optimize=True)
    except Exception as e:
        current_app.logger.error(f'Error optimizing image: {str(e)}')
