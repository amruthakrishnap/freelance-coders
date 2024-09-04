from flask import Flask, request, render_template, jsonify
from apify_client import ApifyClient

app = Flask(__name__)

# Initialize the ApifyClient with your API token
client = ApifyClient("<YOUR_API_TOKEN>")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('extension_url')
        
        # Prepare the Actor input
        run_input = { "url": url }
        
        # Run the Actor and wait for it to finish
        run = client.actor("7SshY9hNcK1GA49RO").call(run_input=run_input)
        
        # Fetch and display Actor results from the run's dataset
        results = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)
        
        return render_template('index.html', results=results)
    
    return render_template('index.html', results=[])

if __name__ == '__main__':
    app.run(debug=True)

