from flask import Blueprint, jsonify

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/hello', methods=['GET'])
def hello():
    """Проверка работоспособности API"""
    return jsonify({
        "status": "success",
        "message": "API работает! Каркас готов",
        "project": "mini_t1"
    }), 200

@bp.route('/status', methods=['GET'])
def status():
    """Статус сервера"""
    return jsonify({
        "server": "running",
        "version": "0.1.0"
    }), 200