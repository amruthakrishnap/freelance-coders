from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Make sure this matches your file name

if __name__ == '__main__':
    app.run(debug=True)
