import os
import json

AI_MODELS_DIR = 'ai_models'


def select_best_ai(analyzed_input):
    best_ai = None
    best_score = -float('inf')

    for ai_file in os.listdir(AI_MODELS_DIR):
        ai_file_path = os.path.join(AI_MODELS_DIR, ai_file)

        # Skip directories
        if os.path.isdir(ai_file_path):
            continue

        try:
            with open(ai_file_path, 'r') as f:
                ai_info = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {ai_file_path} is empty or malformed and will be skipped.")
            continue  # Skip this file and continue with the next one
        except PermissionError:
            print(f"Warning: Permission denied for {ai_file_path}. Skipping this file.")
            continue

        score = calculate_score(analyzed_input, ai_info)
        if score > best_score:
            best_score = score
            best_ai = ai_info

    return best_ai
def calculate_score(analyzed_input, ai_info):
    score = 0

    # Keyword matching

    if 'keywords' in ai_info:
        for keyword in analyzed_input['keywords']:
            if keyword in ai_info['keywords']:
                score += 2

    # Complexity handling
    if analyzed_input['complexity'] > 0.7 and ai_info.get('handles_complex_queries', False):
        score += 5
    elif analyzed_input['complexity'] <= 0.7 and not ai_info.get('handles_complex_queries', True):
        score += 3

    # Input length handling
    if analyzed_input['length'] > 50 and ai_info.get('handles_long_input', False):
        score += 3
    elif analyzed_input['length'] <= 50 and not ai_info.get('handles_long_input', True):
        score += 2

    # Sentiment handling
    if analyzed_input['sentiment'] > 0 and ai_info.get('handles_positive_sentiment', True):
        score += 2
    elif analyzed_input['sentiment'] < 0 and ai_info.get('handles_negative_sentiment', True):
        score += 2

    # Question handling
    if analyzed_input['question'] and ai_info.get('handles_questions', True):
        score += 3

    return score
