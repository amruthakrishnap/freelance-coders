from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder=os.path.join('src', 'templates'))

@app.route('/')
def index():
    return render_template('index2.html')

if __name__ == '__main__':
    app.run(debug=True)
