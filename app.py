from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask import send_from_directory
import os
import time
import webbrowser
from threading import Timer

app = Flask(__name__, template_folder='templates')
# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for sessions



# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and bcrypt
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Ensure database tables are created
with app.app_context():
    db.create_all()
# Questions for autism level
LEVELS = {
    1: {
        'name': "Emotion Recognition",
        'questions': [
            {"question": "What emotion is this face showing?", "image": "happy.png", "options": ["Happy", "Sad", "Angry", "Surprised"], "answer": "Happy"},
            {"question": "What emotion is this face showing?", "image": "sad.png", "options": ["Happy", "Sad", "Angry", "Surprised"], "answer": "Sad"},
            {"question": "What emotion is this face showing?", "image": "angry.png", "options": ["Happy", "Sad", "Angry", "Surprised"], "answer": "Angry"},
        ]
    },
    2: {
        'name': "Pattern Recognition", 
        'questions': [
            {"question": "What comes next in the pattern: 🔵, 🔴, 🔵, 🔴, ?", "options": ["🔵", "🔴", "🟢", "🟡"], "answer": "🔵"},
            {"question": "Complete the pattern: 2, 4, 6, ?", "options": ["8", "7", "5", "10"], "answer": "8"},
            {"question": "Which shape doesn't belong?", "image": "shape.png", "options": ["Circle", "Square", "Triangle", "Hexagon"], "answer": "Hexagon"},
        ]
    },
    3: {
        'name': "Social Situations",
        'questions': [
            {"question": "What would you do if someone is crying?", "options": ["Comfort them", "Ignore them", "Laugh at them", "Tell them to stop"], "answer": "Comfort them"},
            {"question": "If someone says 'How are you?', what is the expected response?", "options": ["Tell them how you're feeling", "Say 'I'm fine, thanks'", "Ignore them", "Ask about the weather"], "answer": "Say 'I'm fine, thanks'"},
            {"question": "What does it mean when someone crosses their arms?", "options": ["They're cold", "They're angry", "They're defensive", "All of the above"], "answer": "All of the above"},
        ]
    }
}
# Dyslexia assessment questions
DYSLEXIA_QUESTION = {
    0: {  # Level 1: Letter & Word Recognition
        'name': 'Letter & Word Recognition',
        'questions': [
            {
                'question': 'Which word is spelled correctly?',
                'options': ['Banaana', 'Banana', 'Bannana', 'Banan'],
                'answer': 'Banana',
                'type': 'standard'
            },
            {
                'question': 'Identify the real word:',
                'options': ['Flower', 'Flobber', 'Flirber', 'Flommer'],
                'answer': 'Flower',
                'type': 'standard'
            },
            {
                'question': 'Which of these is NOT a real word?',
                'options': ['Table', 'Chair', 'Tible', 'Sofa'],
                'answer': 'Tible',
                'type': 'standard'
            },
            {
                'question': 'Select the correctly spelled color:',
                'options': ['Red', 'Rde', 'Erd', 'Der'],
                'answer': 'Red',
                'type': 'standard'
            },
            {
                'question': 'Remember this sequence of letters: A, C, E, G. Which letter comes next?',
                'options': ['H', 'I', 'J', 'K'],
                'answer': 'I',
                'type': 'sequence',
                'sequence': ['A', 'C', 'E', 'G'],
                'display_time': 5
            }
        ]
    },
    1: {  # Level 2: Sequencing & Memory
        'name': 'Sequencing & Memory',
        'questions': [
            {
                'question': 'What comes next in this sequence: B, D, F, H?',
                'options': ['I', 'J', 'K', 'L'],
                'answer': 'J',
                'type': 'standard'
            },
            {
                'question': 'Remember these words: Apple, Banana, Cherry. Which word was NOT in the list?',
                'options': ['Apple', 'Banana', 'Cherry', 'Orange'],
                'answer': 'Orange',
                'type': 'sequence',
                'sequence': ['Apple', 'Banana', 'Cherry'],
                'display_time': 5
            },
            {
                'question': 'Which of these is the correct spelling?',
                'options': ['Necessary', 'Neccessary', 'Nessessary', 'Necesary'],
                'answer': 'Necessary',
                'type': 'standard'
            },
            {
                'question': 'Which word is spelled correctly?',
                'options': ['Accomodate', 'Acommodate', 'Accommodate', 'Acomodate'],
                'answer': 'Accommodate',
                'type': 'standard'
            },
            {
                'question': 'Remember this number sequence: 3, 6, 9, 12. What comes next?',
                'options': ['13', '14', '15', '16'],
                'answer': '15',
                'type': 'sequence',
                'sequence': ['3', '6', '9', '12'],
                'display_time': 5
            }
        ]
    },
    2: {  # Level 3: Reading & Comprehension
        'name': 'Reading & Comprehension',
        'questions': [
            {
                'question': 'Read this sentence: "The quick brown fox jumps over the lazy dog." Which word describes the fox?',
                'options': ['Quick', 'Brown', 'Lazy', 'Dog'],
                'answer': 'Brown',
                'type': 'standard'
            },
            {
                'question': 'Which sentence is correct?',
                'options': [
                    'She dont like apples.',
                    'She doesn\'t likes apples.',
                    'She doesn\'t like apples.',
                    'She don\'t likes apples.'
                ],
                'answer': 'She doesn\'t like apples.',
                'type': 'standard'
            },
            {
                'question': 'Which word is the opposite of "begin"?',
                'options': ['Start', 'Continue', 'Finish', 'Pause'],
                'answer': 'Finish',
                'type': 'standard'
            },
            {
                'question': 'Which of these words is a noun?',
                'options': ['Run', 'Beautiful', 'Quickly', 'Happiness'],
                'answer': 'Happiness',
                'type': 'standard'
            },
            {
                'question': 'What is the plural of "child"?',
                'options': ['Childs', 'Children', 'Childes', 'Childern'],
                'answer': 'Children',
                'type': 'standard'
            }
        ]
    }
}
#adhd ques
QUESTIONS_BANKS= {
    1: {
        'name': "Attention Challenge",
        'questions': [
            {
                "question": "Watch the sequence carefully and select the correct order:",
                "sequence": ["🔵", "🔴", "🟢", "🟡"],
                "options": ["🔵, 🔴, 🟢, 🟡", "🔴, 🔵, 🟡, 🟢", "🟢, 🔵, 🔴, 🟡", "🟡, 🟢, 🔵, 🔴"],
                "answer": "🔵, 🔴, 🟢, 🟡",
                "display_time": 3
            },
            {
                "question": "Remember these numbers:",
                "sequence": ["5", "2", "8", "3"],
                "options": ["5, 2, 8, 3", "2, 5, 3, 8", "8, 3, 5, 2", "3, 8, 2, 5"],
                "answer": "5, 2, 8, 3",
                "display_time": 4
            }
        ]
    },
    2: {
        'name': "Patience Test",
        'questions': [
            {
                "question": "Wait until the button turns green to click it (5 seconds)",
                "type": "timed_wait",
                "wait_time": 5,
                "options": ["Too soon!", "Perfect timing!", "Way too early!", "I waited patiently"],
                "answer": "Perfect timing!"
            },
            {
                "question": "Don't press the button for 7 seconds",
                "type": "impulse_control",
                "wait_time": 7,
                "options": ["I waited", "I pressed too soon", "I couldn't wait", "What button?"],
                "answer": "I waited"
            }
        ]
    }
}





@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("User already exists. Try logging in.", "danger")
            return redirect(url_for('signup'))

        # Create new user and store in DB
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch user from database
        user = User.query.filter_by(username=username).first()

        # Check if user exists
        if not user:
            flash("Account does not exist. Please sign up.", "danger")
            return redirect(url_for('signup'))

        # Verify password
        if bcrypt.check_password_hash(user.password, password):
            session['user'] = username  # Store username in session
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Try again.", "danger")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'])
    
    flash("Please log in first.", "warning")
    return redirect(url_for('login'))

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/Game.html')
def game():
    return render_template('Game.html')

@app.route('/module<int:module_id>.html')
def serve_module(module_id):
    if 1 <= module_id <= 12:
        return render_template(f'module{module_id}.html')
    return "Module not found", 404


# Routes for individual game pages
@app.route('/emoji_quest.html')
def emoji_quest():
    return render_template('emoji_quest.html')

@app.route('/sound.html')
def sound_explorer():
    return render_template('sound.html')

@app.route('/reactiontime.html')
def reaction_time():
    return render_template('reactiontime.html')

@app.route('/treasure.html')
def treasure_hunt():
    return render_template('treasure.html')

@app.route('/color-splash.html')
def color_splash():
    return render_template('color-splash.html')

@app.route('/bubble.html')
def bubble_pop():
    return render_template('bubble.html')

@app.route('/memory_quest.html')
def memory_quest():
    return render_template('memory_quest.html')

@app.route('/static/<path:filename>')  # Ensure Flask serves static files
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))



@app.route('/adhd')
def adhd_page():
    return render_template('adhd/homem.html')  # Corrected path
@app.route('/start_adhd', methods=['POST'])
def start_adhd():
    session['assessment_type'] = 'adhd'
    session['mlevel'] = 1
    session['mquestion_num'] = 0
    session['mtotal_score'] = 0
    session['manswers'] = []
    session.modified = True  

    return redirect(url_for('adhd_question'))  # ✅ Start assessment
@app.route('/adhd_question')
def adhd_question():
    level = session.get('mlevel', 1)
    question_num = session.get('mquestion_num', 0)

    if level not in QUESTIONS_BANKS:
        flash("Invalid level!", "error")
        return redirect(url_for('adhd_page'))

    adhd_questions = QUESTIONS_BANKS[level]
    questions = adhd_questions.get('questions', [])

    if question_num >= len(questions):
        return redirect(url_for('adhd_level_complete'))  # Move to the next level

    question_data = questions[question_num]  # ✅ Fetch the correct question

    # ✅ Debugging logs to verify the data is correct
    print(f"Level: {level}, Question Num: {question_num}")
    print(f"Question Data: {question_data}")

    return render_template('adhd/questionm.html',
                           level=level,
                           level_name=adhd_questions['name'],
                           question_num=question_num + 1,
                           total_questions=len(questions),
                           question=question_data)  # ✅ Ensure 'question' is passed
@app.route('/submit_adhd_answer', methods=['POST'])
def submit_adhd_answer():
    level = session.get('mlevel', 1)
    question_num = session.get('mquestion_num', 0)
    user_answer = request.form.get('answer')

    adhd_questions = QUESTIONS_BANKS.get(level, {})
    if not adhd_questions:
        flash("Invalid level!", "error")
        return redirect(url_for('adhd_page'))

    questions = adhd_questions.get('questions', [])
    if question_num >= len(questions):
        return redirect(url_for('adhd_level_complete'))  # ✅ Redirect when all questions are answered

    question_data = questions[question_num]
    is_correct = (user_answer == question_data['answer'])

    # ✅ Update session score
    if is_correct:
        session['mtotal_score'] = session.get('mtotal_score', 0) + 1

    session['manswers'].append({
        'question': question_data['question'],
        'user_answer': user_answer,
        'correct_answer': question_data['answer'],
        'is_correct': is_correct
    })

    session['mquestion_num'] += 1  # ✅ Move to the next question
    session.modified = True

    # ✅ If all questions are answered, show "Level Complete"
    if session['mquestion_num'] >= len(questions):
        return redirect(url_for('adhd_level_complete'))

    return redirect(url_for('adhd_question'))  # ✅ Show next question
@app.route('/adhd_level_complete')
def adhd_level_complete():
    level = session.get('mlevel', 1)
    session.modified = True  # ✅ Ensure session updates persist

    score = session.get('mtotal_score', 0)
    answers = session.get('manswers', [])

    adhd_questions = QUESTIONS_BANKS.get(level, {})
    if not adhd_questions:
        flash("Invalid level!", "error")
        return redirect(url_for('adhd_page'))

    total_questions = len(adhd_questions['questions'])

    return render_template('adhd/level_completem.html',
                           level=level,
                           level_name=adhd_questions['name'],
                           score=score,
                           total_questions=total_questions,
                           answers=answers)
@app.route('/next_adhd_level', methods=['POST'])
def next_adhd_level():
    if session.get('assessment_type') != 'adhd':
        flash("Please start ADHD assessment first!", "error")
        return redirect(url_for('adhd_page'))

    adhd_questions = QUESTIONS_BANKS
    current_level = session.get('mlevel', 1)

    max_level = max(adhd_questions.keys())  # ✅ Get the highest level number
    if current_level < max_level:
        session['mlevel'] = current_level + 1  # ✅ Move to the next level
        session['mquestion_num'] = 0  # ✅ Reset question counter
        session['manswers'] = []  # ✅ Clear only level-specific answers
        return redirect(url_for('adhd_question'))  # ✅ Go to next level questions
    else:
        return redirect(url_for('adhd_final_score'))  # ✅ Redirect to final score after last level
@app.route('/adhd_final_score')
def adhd_final_score():
    total_score = session.get('mtotal_score', 0)

    # ✅ Count ADHD-specific questions for accurate scoring
    adhd_questions = QUESTIONS_BANKS
    max_possible = sum(len(level['questions']) for level in adhd_questions.values()) if adhd_questions else 1

    percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0

    # ✅ Provide feedback
    if percentage >= 80:
        feedback = "Excellent focus and patience!"
    elif percentage >= 50:
        feedback = "Good effort! With practice, you can improve."
    else:
        feedback = "You might benefit from focus-building exercises."

    return render_template('adhd/final_scorem.html',
                           total_score=total_score,
                           max_possible=max_possible,
                           percentage=percentage,
                           feedback=feedback)


 
@app.route('/autism')
def autism_page():
    return render_template('autism/home.html')  # Corrected path
@app.route('/start', methods=['POST'])
def start():
    session['level'] = 1
    session['question_num'] = 0
    session['total_score'] = 0
    session['answers'] = []
    return redirect(url_for('show_question'))  # Redirects to the first question
@app.route('/question')
def show_question():
    level = session.get('level', 1)
    question_num = session.get('question_num', 0)

    level_data = LEVELS.get(level, LEVELS[1])
    if question_num >= len(level_data['questions']):
        return redirect(url_for('level_complete'))  

    question = level_data['questions'][question_num]

    return render_template('autism/question.html',  # Correct path
                           level=level,
                           level_name=level_data['name'],
                           question_num=question_num + 1,
                           total_questions=len(level_data['questions']), 
                           question=question) 
@app.route('/answer', methods=['POST'])
def answer():
    level = session.get('level', 1)
    question_num = session.get('question_num', 0)
    user_answer = request.form.get('answer')

    level_data = LEVELS.get(level, LEVELS[1])
    
    if question_num >= len(level_data['questions']): 
        return redirect(url_for('level_complete'))  # Ensure valid question number

    question = level_data['questions'][question_num]
    is_correct = user_answer == question['answer']

    if is_correct:
        session['total_score'] = session.get('total_score', 0) + 1
    
    session['answers'].append({
        'question': question['question'],
        'user_answer': user_answer,
        'correct_answer': question['answer'],
        'is_correct': is_correct,
    })

    # Move to next question
    session['question_num'] += 1
    session.modified = True  # Ensure session changes are saved

    return redirect(url_for('show_question'))  # Redirect to next question
@app.route('/level_complete')
def level_complete():
    level = session.get('level', 1)
    score = session.get('total_score', 0)
    answers = session.get('answers', [])
    total_questions = len(LEVELS[level]['questions'])

    return render_template('autism/level_complete.html',
                           level=level,
                           level_name=LEVELS[level]['name'],
                           score=score,
                           total_questions=total_questions, 
                           answers=answers)
@app.route('/next_level', methods=['POST'])
def next_level():
    current_level = session.get('level', 1)

    if current_level < len(LEVELS):  # Check if next level exists
        session['level'] = current_level + 1
        session['question_num'] = 0  # Reset question number for the new level
        session['answers'] = []  # Clear answers for the next level
        session.modified = True  # Ensure session updates persist

        return redirect(url_for('show_question'))
    else:
        return redirect(url_for('final_score'))  # Go to final score if all levels are done
@app.route('/final_score')
def final_score():
    total_score = session.get('total_score', 0)  
    max_possible = sum(len(level['questions']) for level in LEVELS.values())
    percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0

    # Round percentage properly for the template
    percentage = round(percentage, 2)

    if percentage >= 80:
        feedback = "Excellent focus and patience!"
    elif percentage >= 50:
        feedback = "Good effort! With practice, you can improve."
    else:
        feedback = "You might benefit from focus-building exercises."

    return render_template('autism/final_score.html',
                           total_score=total_score,
                           max_possible=max_possible,
                           percentage=percentage,
                           feedback=feedback)





@app.route('/dyslexia')
def dyslexia_page():
    return render_template('dyslexia/homes.html')
@app.route('/begin_dyslexia', methods=['POST'])
def begin_dyslexia():
    # Initialize dyslexia-specific session variables
    session['dlevel'] = 0  # Start at level 0
    session['dquestion_num'] = 0  # Start at question 0
    session['dscore'] = 0  # Initialize score
    session['danswers'] = []  # Store answers
    session['dstart_time'] = time.time()  # Track start time
    
    return redirect(url_for('dyslexia_question'))  # Redirect to first question
@app.route('/dyslexia_question')
def dyslexia_question():
    try:
        dlevel = session.get('dlevel', 0)
        dquestion_num = session.get('dquestion_num', 0)
        
        if dlevel >= len(DYSLEXIA_QUESTION):
            return redirect(url_for('dyslexia_final_score'))
            
        level_data = DYSLEXIA_QUESTION[dlevel]
        
        if dquestion_num >= len(level_data['questions']):
            return redirect(url_for('dyslexia_level_complete'))
            
        question = level_data['questions'][dquestion_num]
        
        return render_template(
            'dyslexia/questions.html',
            level=dlevel + 1,  # 1-based for display
            level_name=level_data['name'],
            question_num=dquestion_num + 1,  # 1-based for display
            total_questions=len(level_data['questions']),
            question=question
        )
    except Exception as e:
        flash("Error loading question", "error")
        return redirect(url_for('dyslexia_page'))
@app.route('/dyslexia_answer', methods=['POST'])
def dyslexia_answer():
    # Get current progress from session
    dlevel = session.get('dlevel', 0)
    dquestion_num = session.get('dquestion_num', 0)
    user_answer = request.form.get('answer')
    
    # Get question data
    question_data = DYSLEXIA_QUESTION[dlevel]['questions'][dquestion_num]
    correct_answer = question_data['answer']
    is_correct = user_answer == correct_answer
    
    # Update score if correct
    if is_correct:
        session['dscore'] = session.get('dscore', 0) + 1
    
    # Store answer details
    session['danswers'].append({
        'question': question_data['question'],
        'user_answer': user_answer,
        'correct_answer': correct_answer,
        'is_correct': is_correct,
        'elapsed_time': time.time() - session.get('dstart_time', time.time())
    })
    
    # Move to next question and update time
    session['dquestion_num'] = dquestion_num + 1
    session['dstart_time'] = time.time()
    
    return redirect(url_for('dyslexia_question'))
@app.route('/dyslexia_level_complete')
def dyslexia_level_complete():
    try:
        # Get current level and score from session
        dlevel = session.get('dlevel', 0)
        dscore = session.get('dscore', 0)
        
        # Get level data
        level_data = DYSLEXIA_QUESTION[dlevel]
        total_questions = len(level_data['questions'])
        
        return render_template(
            'dyslexia/level_completes.html',
            level=dlevel + 1,  # Convert to 1-based index for display
            level_name=level_data['name'],
            score=dscore,
            total_questions=total_questions,
            answers=session.get('danswers', [])
        )
    except Exception as e:
        flash("Error loading level completion", "error")
        return redirect(url_for('dyslexia_page'))
@app.route('/dyslexia_next_level', methods=['POST'])
def dyslexia_next_level():
    # Move to next level and reset question tracking
    session['dlevel'] = session.get('dlevel', 0) + 1
    session['dquestion_num'] = 0
    session['danswers'] = []
    session['dstart_time'] = time.time()  # Reset timer for new level
    return redirect(url_for('dyslexia_question'))
@app.route('/dyslexia_final_score')
def dyslexia_final_score():
    # Calculate final score
    total_score = session.get('dscore', 0)
    max_possible = sum(len(level['questions']) for level in DYSLEXIA_QUESTION.values())
    percentage = round((total_score / max_possible) * 100, 2) if max_possible > 0 else 0
    
    # Generate appropriate feedback
    if percentage >= 80:
        feedback = "Excellent! Your reading and language skills are strong."
    elif percentage >= 60:
        feedback = "Good job! You have average reading and language skills."
    elif percentage >= 40:
        feedback = "You might benefit from some reading support strategies."
    else:
        feedback = "Consider seeking a professional assessment for dyslexia."
    
    return render_template(
        'dyslexia/final_scores.html',  # Matches your template filename
        total_score=total_score,
        max_possible=max_possible,
        percentage=percentage,
        feedback=feedback
    )










@app.route('/dyspraxia')
def dyspraxia_page():
    return render_template('dyspraxia/homes.html')

@app.route('/dyscalculia')
def dyscalculia_page():
    return render_template('dyscalculia.html')

@app.route('/tourette')
def tourette_page():
    return render_template('tourette.html')


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000") 

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)