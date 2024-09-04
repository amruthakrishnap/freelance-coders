from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/embed', methods=['GET'])
def embed_code():
    extension_url = request.args.get('extension_url')
    if not extension_url:
        return jsonify({'error': 'Missing extension URL'}), 400
    
    embed_code = f'<iframe src="https://freelance-coders.vercel.app/?extension_url={extension_url}" width="800" height="600" frameborder="0" allowfullscreen></iframe>'
    
    return jsonify({'embed_code': embed_code})


