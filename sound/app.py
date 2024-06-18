from flask import Flask, render_template, request, jsonify, send_file
from gtts import gTTS
import io
import sqlite3
from datetime import datetime
import subprocess
import os

app = Flask(__name__)
gesture_process = None
gesture_flag_file = 'gesture_running.flag'

def create_or_alter_table():
    conn = sqlite3.connect('speech.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS speeches (
            id INTEGER PRIMARY KEY,
            text TEXT,
            speech BLOB,
            timestamp DATETIME
        )
    ''')
    c.execute("PRAGMA table_info(speeches)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'timestamp' not in columns:
        c.execute('ALTER TABLE speeches ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP')
    
    conn.commit()
    conn.close()
 
create_or_alter_table()

@app.route('/')
def index():
    conn = sqlite3.connect('speech.db')
    c = conn.cursor()
    c.execute('''SELECT id, text, timestamp FROM speeches ORDER BY timestamp DESC''')
    saved_words = c.fetchall()
    conn.close()
    return render_template('index.html', saved_words=saved_words)

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data['text']

    tts = gTTS(text)
    speech_bytes = io.BytesIO()
    tts.write_to_fp(speech_bytes)
    speech_bytes.seek(0)

    conn = sqlite3.connect('speech.db')
    c = conn.cursor()
    c.execute('''INSERT INTO speeches (text, speech, timestamp) VALUES (?, ?, ?)''', 
              (text, speech_bytes.read(), datetime.now()))
    conn.commit()
    conn.close()

    speech_bytes.seek(0)

    return send_file(speech_bytes, mimetype='audio/mpeg')

@app.route('/page1')
def page1():
    return render_template('page1.html')

@app.route('/gesture')
def gesture():
    return render_template('gesture.html')

@app.route('/start_gesture_detection', methods=['POST'])
def start_gesture_detection_route():
    global gesture_process
    try:
        # Create the flag file
        with open(gesture_flag_file, 'w') as f:
            f.write('running')
        
        # Start the gesture detection script
        gesture_process = subprocess.Popen(['python', os.path.join(os.path.dirname(__file__), 'gesture.py')])
        return jsonify({'status': 'Live Image Detection'}), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

@app.route('/stop_gesture_detection', methods=['POST'])
def stop_gesture_detection_route():
    global gesture_process
    try:
        # Delete the flag file to signal the gesture script to stop
        if os.path.exists(gesture_flag_file):
            os.remove(gesture_flag_file)
        
        if gesture_process:
            gesture_process.terminate()
            gesture_process = None
        return jsonify({'status': 'Live Image Detection stopped'}), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
