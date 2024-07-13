from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
@app.route('/login')
def index():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True, port=5041)
