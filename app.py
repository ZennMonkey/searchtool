# app.py
import os
import serpapi
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import pandas as pd
import time
import tempfile

app = Flask(__name__, template_folder='.')
CORS(app)

# Default API Key
SERP_API_KEY = "b791a8aebc9fe1387038a6362fe8b65bc775892c30fc31405cd279222f19ef86"

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering template: {str(e)}")
        return str(e), 500

@app.route('/search', methods=['POST'])
def search():
    try:
        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Read CSV
        df = pd.read_csv(file)
        if 'business_name' not in df.columns:
            return jsonify({'error': 'CSV must have a business_name column'}), 400

        # Get API key from request or use default
        api_key = request.headers.get('X-API-Key', SERP_API_KEY)
        client = serpapi.Client(api_key=api_key)
        
        all_results = []
        total_businesses = len(df)
        
        # Process each business
        for index, row in df.iterrows():
            business_name = str(row['business_name']).strip()
            if not business_name:
                continue

            try:
                print(f"Processing {index + 1}/{total_businesses}: {business_name}")
                
                # Perform the search
                result = client.search(
                    q=f"{business_name}",
                    engine="google",
                    location="Canada",
                    hl="en",
                    gl="ca",
                    google_domain="google.ca"
                )
                
                # Process organic results
                if 'organic_results' in result:
                    for res in result['organic_results']:
                        all_results.append({
                            'business_name': business_name,
                            'search_query': f"{business_name}",
                            'organic_position': res.get('position'),
                            'title': res.get('title', ''),
                            'snippet': res.get('snippet', ''),
                            'link': res.get('link', ''),
                            'domain': res.get('displayed_link', ''),
                            'source_type': 'organic',
                            'status': 'success'
                        })
                else:
                    all_results.append({
                        'business_name': business_name,
                        'search_query': f"{business_name}",
                        'error': 'No results found',
                        'status': 'no_results'
                    })
                
                # Add delay between searches
                time.sleep(2)

            except Exception as e:
                print(f"Error processing {business_name}: {str(e)}")
                all_results.append({
                    'business_name': business_name,
                    'search_query': f"{business_name}",
                    'error': str(e),
                    'organic_position': None,
                    'title': '',
                    'snippet': '',
                    'link': '',
                    'domain': '',
                    'source_type': 'error',
                    'status': 'error'
                })

        # Create output CSV in a temporary directory
        df_results = pd.DataFrame(all_results)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        temp_dir = tempfile.gettempdir()
        output_file = os.path.join(temp_dir, f'search_results_{timestamp}.csv')
        df_results.to_csv(output_file, index=False)
        
        return send_file(
            output_file,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'search_results_{timestamp}.csv'
        )

    except Exception as e:
        print(f"Error in search endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting server...")
    print("Current working directory:", os.getcwd())
    print("Files in directory:", os.listdir())
    app.run(port=5000, debug=True)