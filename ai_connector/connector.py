from datetime import datetime
import importlib.util
import sys
import requests
import subprocess
import json
import os


def load_ai_module(file_path):
    spec = importlib.util.spec_from_file_location("ai_module", file_path)
    ai_module = importlib.util.module_from_spec(spec)
    sys.modules["ai_module"] = ai_module
    spec.loader.exec_module(ai_module)
    return ai_module


def connect_ai(ai_info, user_input, user_id):
    ai_type = ai_info['type']

    if ai_type == 'custom':
        ai_module = load_ai_module(ai_info['file_path'])
        if hasattr(ai_module, 'create_assistant'):
            assistant = ai_module.create_assistant()
            return assistant.process_query(user_input)
        else:
            raise ValueError(f"Custom AI module does not have 'create_assistant' function")
    elif ai_type == 'api':
        return connect_api(ai_info, user_input, user_id)
    elif ai_type == 'local':
        return run_local_ai(ai_info, user_input, user_id)
    else:
        # Load dynamic connector if available
        connector_path = f'ai_connector/{ai_type}_connector.py'
        if os.path.exists(connector_path):
            connector_module = load_ai_module(connector_path)
            if hasattr(connector_module, 'process_query'):
                return connector_module.process_query(ai_info, user_input, user_id)

        raise ValueError(f"Unknown or unsupported AI type: {ai_type}")


def connect_api(ai_info, user_input, user_id):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {ai_info['api_key']}"
    }

    data = {
        'input': user_input,
        'user_id': user_id
    }

    try:
        response = requests.post(ai_info['api_url'], headers=headers, json=data)
        response.raise_for_status()
        return response.json()['output']
    except requests.RequestException as e:
        return f"Error connecting to {ai_info['name']}: {str(e)}"


def run_local_ai(ai_info, user_input, user_id):
    env = os.environ.copy()
    env['AI_INPUT'] = user_input
    env['USER_ID'] = user_id

    try:
        result = subprocess.run(
            ai_info['run_command'],
            shell=True,
            capture_output=True,
            text=True,
            env=env,
            timeout=30  # 30 second timeout
        )
        if result.returncode != 0:
            return f"Error running {ai_info['name']}: {result.stderr}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return f"Timeout while running {ai_info['name']}"
    except Exception as e:
        return f"Error running {ai_info['name']}: {str(e)}"


def save_conversation(user_id, ai_name, user_input, ai_output):
    conversation_file = f'conversations/{user_id}.json'

    if os.path.exists(conversation_file):
        with open(conversation_file, 'r') as f:
            conversation = json.load(f)
    else:
        conversation = []

    conversation.append({
        'ai': ai_name,
        'user_input': user_input,
        'ai_output': ai_output,
        'timestamp': datetime.now().isoformat()
    })

    with open(conversation_file, 'w') as f:
        json.dump(conversation, f)