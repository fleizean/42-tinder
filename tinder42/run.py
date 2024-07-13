from app import create_app
# from app.models import User, Post  # Örnek model sınıfları

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {"app": app}  # Buraya model sınıflarını ekleyebilirsiniz

if __name__ == '__main__':
    app.run(debug=True, port=5041)
