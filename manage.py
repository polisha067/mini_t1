import os
from app import create_app

if __name__ == '__main__':
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    app = create_app(config_name)
    app.run(debug=True, host='0.0.0.0', port=5000)