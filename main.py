from flask import Flask, render_template, request, jsonify
import json
import sqlite3
from command import commands         # Import the commands dictionary
from qanstest import get_qan_answer  # Import QA function
from datetime import datetime, timedelta
from outlook_scheduler import schedule_teams_meeting
import os

# Path to JSON file - use relative path for deployment
file_paths = os.path.join(os.path.dirname(__file__), "responses.json")

def load_responses(file_paths):
    """Load responses from a JSON file."""
    try:
        with open(file_paths, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{file_paths}' was not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: The file '{file_paths}' contains invalid JSON.")
        return {}

app = Flask(__name__)

@app.route('/')  # URL path http://localhost:5000/
def home():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify deployment status."""
    import os
    health_status = {
        'status': 'ok',
        'checks': {}
    }
    
    # Check responses.json
    responses_file = os.path.join(os.path.dirname(__file__), "responses.json")
    health_status['checks']['responses.json'] = os.path.exists(responses_file)
    
    # Check softdel_index directory
    index_dir = os.path.join(os.path.dirname(__file__), "softdel_index")
    health_status['checks']['softdel_index'] = os.path.exists(index_dir)
    
    # Check OPENAI_API_KEY (don't expose the key, just if it exists)
    api_key = os.getenv("OPENAI_API_KEY")
    health_status['checks']['OPENAI_API_KEY'] = bool(api_key and api_key.startswith("sk-"))
    
    # Check if all checks passed
    if not all(health_status['checks'].values()):
        health_status['status'] = 'degraded'
    
    return jsonify(health_status)

@app.route('/chat', methods=['POST'])  # URL path http://localhost:5000/chat
def chat():
    try:
        user_input = request.json.get('user_input', '').lower()
        print(f"📥 User input: {user_input}")  # Log user input

        responses = load_responses(file_paths)
        if not responses:
            print("❌ Responses file not loaded")
            return jsonify({'response': "I cannot start without responses. Please check the JSON file."})

        # Check for exact matches in JSON responses
        response = responses.get(user_input)

        # Check for commands if no exact match
        if response is None:
            for keyword, command in commands.items():
                if keyword in user_input:
                    response = command() if callable(command) else command
                    break
        # Check scheduling keywords BEFORE AI
        # List of phrases (full strings or parts of sentences) to detect scheduling intent
        schedule_strings = [
            "schedule a call",
            "book a meeting",
            "connect with executive",
            "talk to representative",
            "schedule a meeting",
            "i want to schedule a call",
            "can we have a demo"
        ]

        user_input_lower = user_input.lower()

        # Check if user input contains any of the full phrases
        if any(phrase in user_input_lower for phrase in schedule_strings):
            response = '📅 Do you want me to schedule a call with our executive? Please provide name, email, phone, and preferred time.'

        # Fallback to QA function if still no match
        if response is None:
            print("🤖 Calling QA function...")
            try:
                response = get_qan_answer(user_input)
                print(f"✅ QA response received: {response[:100]}...")
            except Exception as e:
                print(f"❌ Error in QA function: {type(e).__name__}: {e}")
                import traceback
                print(f"❌ Traceback:\n{traceback.format_exc()}")
                response = f"❌ Error processing your request: {type(e).__name__}. Please try again or contact support."

        # Use default response if QA returns nothing
        if not response:
            response = responses.get("default", "I'm sorry, I don't understand that.")

        print(f"📤 Bot response: {response[:100]}...")  # Log bot response
        return jsonify({'response': response})
    except Exception as e:
        print(f"❌ Unexpected error in chat endpoint: {type(e).__name__}: {e}")
        import traceback
        print(f"❌ Traceback:\n{traceback.format_exc()}")
        return jsonify({'response': f"❌ An unexpected error occurred: {type(e).__name__}. Please try again."}), 500

# Initialize DB
def init_db():
    conn = sqlite3.connect("scheduler.db")
    c = conn.cursor()
    c.execute(''' CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT NOT NULL,
            meeting_date TEXT NOT NULL,
            meeting_time TEXT NOT NULL,
            meeting_duration TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/submit_schedule", methods=["POST"])
def submit_schedule():
    try:
        # Extract fields
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "❌ No data received"})
        
        name = data.get('name', '')
        mobile = data.get('mobile', '')
        email = data.get('email', '')
        date = data.get('date', '')
        time = data.get('time', '')
        duration = data.get('duration', '')
        
        print(" user data", name)

        # Combine date and time into datetime object
      #  time_from = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

        # Calculate end time
       # time_to = time_from + timedelta(minutes=duration)

        # Store in ISO format (e.g., "2025-10-10T14:30:00")
        #time_from_str = time_from.isoformat()
        #time_to_str = time_to.isoformat()

        # Validate required fields
        if not all([name, mobile, email, date, time, duration]):
            return jsonify({"success": False, "message": "❌ All fields are required"})
        
        # Convert duration to integer
        try:
            duration_int = int(duration)
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": "❌ Invalid duration value"})
        
        # Save to DB
        # Call Outlook scheduler
        result = schedule_teams_meeting(
            subject=f"Call with {name}",
            date_input=date,
            start_time_input=time,
            duration=duration_int,
            attendees_input=email
        )
        print(" scheduler result", result)

        # Optionally save to DB only if meeting scheduled successfully
        if result.get("success"):
            conn = sqlite3.connect("scheduler.db")
            c = conn.cursor()
            c.execute("""
                INSERT INTO meetings (name, mobile, email, meeting_date, meeting_time, meeting_duration)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, mobile, email, date, time, duration_int))
            conn.commit()
            conn.close()

        return jsonify(result)

    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"❌ Error processing request: {str(e)}"})

# def get_data_from_db():
#     conn = sqlite3.connect('scheduler.db')  # your .db file
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM schedule_calls ORDER BY id DESC LIMIT 1" )  # example table
#     rows = cursor.fetchall()
#     conn.close()
#     return [{"name": r[0], "mobile": r[1], "email": r[2], "meeting_date": r[3], "meeting_time": r[4], "meeting_duration": r[5]} for r in rows]

# @app.route('/api/users', methods=['POST'])
# def get_users():
#     data = get_data_from_db()
#     return jsonify(data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Use debug=True for local testing, debug=False for production
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    app.run(host="127.0.0.1", port=port, debug=debug_mode)


