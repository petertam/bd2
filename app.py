import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from agents.coordinator_agent import CoordinatorAgent

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the coordinator agent
coordinator = CoordinatorAgent()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message_from_server', {
        'message': 'Welcome! I am your AI investment advisor. How can I help you today?',
        'personality': 'Warren Buffett'
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message_from_user')
def handle_message(data):
    message = data.get('message', '')
    print(f'Received message: {message}')
    
    try:
        # Process the message through the coordinator agent
        response = coordinator.process_message(message)
        
        # Emit response back to client
        emit('message_from_server', {
            'message': response['message'],
            'personality': response.get('personality', 'Warren Buffett'),
            'data': response.get('data', None)
        })
    except Exception as e:
        print(f'Error processing message: {e}')
        emit('message_from_server', {
            'message': 'Sorry, I encountered an error processing your request. Please try again.',
            'personality': 'Warren Buffett'
        })

@socketio.on('personality_change')
def handle_personality_change(data):
    personality = data.get('personality', 'Warren Buffett')
    print(f'Personality changed to: {personality}')
    
    # Update the coordinator's personality
    coordinator.set_personality(personality)
    
    emit('personality_updated', {
        'personality': personality,
        'message': f'Personality changed to {personality}. How can I help you with your investments?'
    })

if __name__ == '__main__':
    port = int(os.getenv('FLASK_APP_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    socketio.run(app, debug=debug, port=port, host='0.0.0.0') 