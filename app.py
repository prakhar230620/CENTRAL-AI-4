from flask import Flask, render_template, request, jsonify, session
from ai_selector.analyzer import analyze_input
from ai_selector.selector import select_best_ai
from ai_connector.connector import connect_ai,load_ai_module
from utils.google_api import search_google
from utils.voice_recognition import recognize_speech, text_to_speech
import uuid
from werkzeug.utils import secure_filename
import os
import json



app = Flask(__name__)
app.secret_key = '2d6901abea00aa7639baf9a8'  # Session management ke liye
UPLOAD_FOLDER = 'ai_models'
ALLOWED_EXTENSIONS = {'py', 'json'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('index.html')


@app.route('/process_input', methods=['POST'])
def process_input():
    user_input = request.json['input']
    input_type = request.json['type']  # 'text' or 'voice'
    user_id = session['user_id']

    if input_type == 'voice':
        user_input = recognize_speech(user_input)

    analyzed_input = analyze_input(user_input)
    selected_ai = select_best_ai(analyzed_input)

    if selected_ai:
        response = connect_ai(selected_ai, user_input, user_id)
    else:
        response = search_google(user_input)

    if input_type == 'voice':
        audio_file = text_to_speech(response)
        return jsonify({'response': response, 'audio_file': audio_file})

    return jsonify({'response': response})


@app.route('/integrate_ai', methods=['GET', 'POST'])
def integrate_ai():
    if request.method == 'POST':
        ai_name = request.form['ai_name']
        ai_type = request.form['ai_type']
        ai_description = request.form['ai_description']
        ai_file = request.files['ai_file']

        if ai_file and allowed_file(ai_file.filename):
            filename = secure_filename(ai_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            ai_file.save(file_path)

            ai_info = {
                'name': ai_name,
                'type': ai_type,
                'description': ai_description,
                'file_path': file_path,
            }

            # If it's a custom AI, try to get additional info
            if ai_type == 'custom':
                try:
                    ai_module = load_ai_module(file_path)
                    if hasattr(ai_module, 'get_info'):
                        additional_info = ai_module.get_info()
                        ai_info.update(additional_info)
                except Exception as e:
                    return jsonify({'success': False, 'message': f'Error loading custom AI: {str(e)}'})

            # Save AI info
            with open(f'ai_models/{ai_name}.json', 'w') as f:
                json.dump(ai_info, f)

            return jsonify({'success': True, 'message': f'AI {ai_name} successfully integrated'})

        return jsonify({'success': False, 'message': 'Invalid file'})

    return render_template('ai_integration.html')

def assign_unique_port():
    # Existing ports ko check karke naya unique port assign karna
    existing_ports = set()
    for ai_file in os.listdir('ai_models'):
        with open(f'ai_models/{ai_file}', 'r') as f:
            ai_info = json.load(f)
            existing_ports.add(ai_info['port'])

    new_port = max(existing_ports) + 1 if existing_ports else 8000
    return new_port


if __name__ == '__main__':
    app.run(debug=True)