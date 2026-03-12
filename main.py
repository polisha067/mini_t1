from app import create_app

# Создаем экземпляр приложения через factory function
app = create_app()
app.json.ensure_ascii = False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)