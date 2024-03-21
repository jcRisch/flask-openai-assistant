from flask import render_template, Blueprint, request, jsonify
from app.services.assistant import AssistantService

assistant_bp = Blueprint('assistant', __name__)

@assistant_bp.route('/assistant', methods=['GET', 'POST'])
def assistant():
    if request.method == 'POST':
        # Extract message from the POST request
        data = request.get_json()
        message = data.get('message', '')

        if not message:
            return jsonify({'error': 'No message provided'}), 400
      
        assistant_service = AssistantService()

        # Here you would typically process the message and generate a response
        # For demonstration, let's just echo the message back
        assistant_response = assistant_service.run_assistant(message)
        
        # Return response as JSON for the fetch call in home.html
        return jsonify({'assistant_response': assistant_response})
    else:
        # For GET requests, show the form without any initial response
        return render_template('home.html')