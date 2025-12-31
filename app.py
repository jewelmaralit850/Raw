from flask import Flask, request, jsonify, send_from_directory, abort
import os

app = Flask(__name__, static_folder='.', static_url_path='')

FILES_DIR = 'files'
KEYS_FILE = 'keys.txt'  # Stores path:api_key

os.makedirs(FILES_DIR, exist_ok=True)

# Load stored API keys
keys = {}
if os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if ':' in line:
                path, api_key = line.split(':', 1)
                keys[path] = api_key

def save_keys():
    with open(KEYS_FILE, 'w') as f:
        for path, api_key in keys.items():
            f.write(f'{path}:{api_key}\n')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/create')
def create_page():
    return app.send_static_file('index.html')

# Serve raw files as plain text
@app.route('/<filename>')
def serve_file(filename):
    filepath = os.path.join(FILES_DIR, filename)
    if os.path.exists(filepath):
        return send_from_directory(FILES_DIR, filename, mimetype='text/plain')
    return 'File not found', 404

# Unified endpoint: POST /api/filename.lua?apikey=secret
@app.route('/api/<filename>', methods=['POST'])
def api_update(filename):
    apikey = request.args.get('apikey')
    data = request.get_json()
    
    if not apikey:
        return jsonify({'error': 'API key is required'}), 400
    if not data or 'contents' not in data:
        return jsonify({'error': 'Missing contents'}), 400

    filepath = os.path.join(FILES_DIR, filename)
    stored_key = keys.get(filename)

    # If file exists, check API key
    if os.path.exists(filepath):
        if stored_key != apikey:
            return jsonify({'error': 'Invalid API key'}), 403
    else:
        # New file: store the API key
        keys[filename] = apikey
        save_keys()

    # Write the file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data['contents'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
