import json
import random
import os
import sqlite3
import streamlit as st
from master_ozz.utils import init_constants

# -----------------------------
# Config
# -----------------------------
constants = init_constants()
DB_PATH = os.path.join(constants['OZZ_DB'], "master_math.db")
CATEGORIES = ["addition", "subtraction", "multiplication", "division"]

# Number to word conversion
NUMBER_WORDS = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
    11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
    16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty",
    30: "thirty", 40: "forty", 50: "fifty", 60: "sixty", 70: "seventy", 
    80: "eighty", 90: "ninety", 100: "one hundred"
}

def number_to_words(n):
    if n in NUMBER_WORDS:
        return NUMBER_WORDS[n]
    if n < 100:
        tens = (n // 10) * 10
        ones = n % 10
        if tens in NUMBER_WORDS and ones in NUMBER_WORDS:
            return f"{NUMBER_WORDS[tens]}-{NUMBER_WORDS[ones]}"
    if n < 1000:
        hundreds = n // 100
        remainder = n % 100
        result = f"{NUMBER_WORDS[hundreds]} hundred"
        if remainder > 0:
            result += f" {number_to_words(remainder)}"
        return result
    return str(n)

# Story elements for reading problems
OBJECTS = {
    "addition": [
        "shiny red apples", "colorful balloons", "sparkling diamonds", "chocolate cookies",
        "golden coins", "rainbow stickers", "magical stars", "bright flowers"
    ],
    "subtraction": [
        "juicy oranges", "fluffy clouds", "candy bars", "toy cars",
        "birthday candles", "paper airplanes", "building blocks", "marbles"
    ],
    "multiplication": [
        "treasure chests", "gift boxes", "baskets", "bags", "containers", "jars", "bowls", "crates"
    ],
    "division": [
        "delicious cupcakes", "shiny marbles", "colorful crayons", "sweet strawberries",
        "puzzle pieces", "trading cards", "game tokens", "stickers"
    ]
}

CHARACTERS = [
    "Emma", "Liam", "Olivia", "Noah", "Sophia", "Mason", "Ava", "Lucas",
    "Isabella", "Ethan", "Mia", "Jackson", "Charlotte", "Aiden", "Harper"
]

ACTIONS = {
    "addition": ["found", "collected", "received", "picked up", "gathered", "discovered"],
    "subtraction": ["gave away", "lost", "ate", "used", "shared", "donated"],
    "multiplication": ["has", "found", "collected", "owns", "received", "bought"],
    "division": ["wants to share", "needs to divide", "is splitting", "is distributing"]
}

# -----------------------------
# Database helpers
# -----------------------------
def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database schema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Category scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS category_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            category TEXT,
            total_right INTEGER DEFAULT 0,
            total_wrong INTEGER DEFAULT 0,
            FOREIGN KEY (username) REFERENCES users(username),
            UNIQUE(username, category)
        )
    ''')
    
    # Equations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            category TEXT,
            equation TEXT,
            right INTEGER DEFAULT 0,
            wrong INTEGER DEFAULT 0,
            completed_correct INTEGER DEFAULT 0,
            FOREIGN KEY (username) REFERENCES users(username),
            UNIQUE(username, category, equation)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_users():
    """Get list of all users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users ORDER BY username')
    users = [row['username'] for row in cursor.fetchall()]
    conn.close()
    return users

def ensure_user(username):
    """Ensure user exists in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert user if not exists
    cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', (username,))
    
    # Ensure category scores exist
    for category in CATEGORIES:
        cursor.execute('''
            INSERT OR IGNORE INTO category_scores (username, category, total_right, total_wrong)
            VALUES (?, ?, 0, 0)
        ''', (username, category))
    
    conn.commit()
    conn.close()

def get_user_scores(username):
    """Get user's scores by category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, total_right, total_wrong
        FROM category_scores
        WHERE username = ?
    ''', (username,))
    
    scores = {}
    for row in cursor.fetchall():
        scores[row['category']] = {
            'total_right': row['total_right'],
            'total_wrong': row['total_wrong']
        }
    
    conn.close()
    return scores

def get_category_equations(username, category):
    """Get all equations for a specific category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT equation, right, wrong, completed_correct
        FROM equations
        WHERE username = ? AND category = ?
    ''', (username, category))
    
    equations = {}
    for row in cursor.fetchall():
        equations[row['equation']] = {
            'right': row['right'],
            'wrong': row['wrong'],
            'completed_correct': bool(row['completed_correct'])
        }
    
    conn.close()
    return equations

def record_attempt(username, category, equation, correct):
    """Record a problem attempt"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get or create equation record
    cursor.execute('''
        INSERT OR IGNORE INTO equations (username, category, equation, right, wrong, completed_correct)
        VALUES (?, ?, ?, 0, 0, 0)
    ''', (username, category, equation))
    
    # Update equation stats
    if correct:
        cursor.execute('''
            UPDATE equations
            SET right = right + 1,
                completed_correct = CASE WHEN right + 1 >= 3 THEN 1 ELSE completed_correct END
            WHERE username = ? AND category = ? AND equation = ?
        ''', (username, category, equation))
        
        # Update category totals
        cursor.execute('''
            UPDATE category_scores
            SET total_right = total_right + 1
            WHERE username = ? AND category = ?
        ''', (username, category))
    else:
        cursor.execute('''
            UPDATE equations
            SET wrong = wrong + 1
            WHERE username = ? AND category = ? AND equation = ?
        ''', (username, category, equation))
        
        # Update category totals
        cursor.execute('''
            UPDATE category_scores
            SET total_wrong = total_wrong + 1
            WHERE username = ? AND category = ?
        ''', (username, category))
    
    # Check if mastered
    cursor.execute('''
        SELECT right FROM equations
        WHERE username = ? AND category = ? AND equation = ?
    ''', (username, category, equation))
    
    row = cursor.fetchone()
    is_mastered = row['right'] >= 3 if row else False
    
    conn.commit()
    conn.close()
    
    return is_mastered

def is_problem_mastered(username, category, equation):
    """Check if user has mastered this problem (3+ correct)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT right FROM equations
        WHERE username = ? AND category = ? AND equation = ?
    ''', (username, category, equation))
    
    row = cursor.fetchone()
    conn.close()
    
    return row['right'] >= 3 if row else False

# -----------------------------
# Problem generation
# -----------------------------
def get_complexity_range(complexity):
    """Return min and max values based on complexity level"""
    ranges = {
        1: (1, 5),      # Very easy: 1-5
        2: (1, 10),     # Easy: 1-10
        3: (1, 12),     # Medium: 1-12
        4: (5, 20),     # Hard: 5-20
        5: (10, 50)     # Very hard: 10-50
    }
    return ranges.get(complexity, (1, 12))

def make_problem(category, complexity):
    range_min, range_max = get_complexity_range(complexity)
    a = random.randint(range_min, range_max)
    b = random.randint(range_min, range_max)

    if category == "addition":
        question = f"{a} + {b} ="
        answer = a + b
    elif category == "subtraction":
        # Ensure positive result for easier levels
        if complexity <= 2:
            a = max(a, b)
            b = min(a, b)
        question = f"{a} - {b} ="
        answer = a - b
    elif category == "multiplication":
        question = f"{a} × {b} ="
        answer = a * b
    elif category == "division":
        answer = random.randint(range_min, min(range_max, 20))
        b = random.randint(range_min, min(range_max // 2, 12))
        a = answer * b
        question = f"{a} ÷ {b} = ?"
    else:
        raise ValueError("Unknown category")
    return question, answer

def generate_new_problem(category, complexity, username, max_attempts=20):
    """Generate a problem that hasn't been mastered yet"""
    attempts = 0
    while attempts < max_attempts:
        q, a = make_problem(category, complexity)
        if not is_problem_mastered(username, category, q):
            return q, a
        attempts += 1
    # If all problems are mastered or max attempts reached, return any problem
    return make_problem(category, complexity)

def problem_to_reading(category, question, answer, complexity):
    """Convert a math problem to a colorful reading format based on complexity"""
    parts = question.replace("=", "").replace("?", "").strip().split()
    a_num = int(parts[0])
    b_num = int(parts[2])
    
    char = random.choice(CHARACTERS)
    obj = random.choice(OBJECTS[category])
    action = random.choice(ACTIONS[category])
    
    if complexity == 1:
        # Simple, direct question
        if category == "addition":
            return f"{char} has {number_to_words(a_num)} {obj} and gets {number_to_words(b_num)} more. How many total?"
        elif category == "subtraction":
            return f"{char} has {number_to_words(a_num)} {obj} and {action} {number_to_words(b_num)}. How many left?"
        elif category == "multiplication":
            return f"{char} has {number_to_words(a_num)} {obj}, each with {number_to_words(b_num)} items. How many total?"
        elif category == "division":
            return f"{char} has {number_to_words(a_num)} {obj} to share among {number_to_words(b_num)} friends. How many each?"
    
    elif complexity == 2:
        # Add location
        locations = ["at the park", "in the garden", "at school", "at home", "in the store"]
        location = random.choice(locations)
        
        if category == "addition":
            return f"{char} {action} {number_to_words(a_num)} {obj} {location}, then {action} {number_to_words(b_num)} more. How many {obj} does {char} have now?"
        elif category == "subtraction":
            return f"{char} had {number_to_words(a_num)} {obj} {location} but {action} {number_to_words(b_num)} of them. How many {obj} are left?"
        elif category == "multiplication":
            return f"{char} {action} {number_to_words(a_num)} {obj} {location}. Each one contains {number_to_words(b_num)} items. How many items in total?"
        elif category == "division":
            return f"{char} has {number_to_words(a_num)} {obj} {location} and {action} them equally among {number_to_words(b_num)} people. How many does each person get?"
    
    elif complexity == 3:
        # Add time and more context
        times = ["yesterday", "this morning", "today", "last week", "on Monday"]
        locations = ["at the colorful park", "in the sunny garden", "at the busy school", "at the cozy home"]
        time = random.choice(times)
        location = random.choice(locations)
        
        if category == "addition":
            return f"{time}, {char} {action} {number_to_words(a_num)} beautiful {obj} {location}. Later, {char} {action} {number_to_words(b_num)} more {obj}. How many {obj} does {char} have altogether?"
        elif category == "subtraction":
            return f"{char} had {number_to_words(a_num)} {obj} {location} {time}. Then {char} {action} {number_to_words(b_num)} of them. How many {obj} does {char} have remaining?"
        elif category == "multiplication":
            return f"{time}, {char} {action} {number_to_words(a_num)} {obj} {location}. Inside each one were {number_to_words(b_num)} special items. What is the total number of items?"
        elif category == "division":
            return f"{char} baked {number_to_words(a_num)} {obj} {time} {location}. {char} {action} them fairly between {number_to_words(b_num)} friends. How many {obj} will each friend receive?"
    
    elif complexity == 4:
        # Add multiple characters and actions
        char2 = random.choice([c for c in CHARACTERS if c != char])
        times = ["early in the morning", "during lunch break", "after school", "on a rainy day"]
        locations = ["at the vibrant park", "in the lush green garden", "at the exciting school fair", "in the cozy kitchen"]
        time = random.choice(times)
        location = random.choice(locations)
        
        if category == "addition":
            return f"{time}, {char} {action} {number_to_words(a_num)} sparkling {obj} {location}. Then {char2} gave {char} {number_to_words(b_num)} more {obj} as a gift. How many {obj} does {char} have in total now?"
        elif category == "subtraction":
            return f"{char} had collected {number_to_words(a_num)} {obj} {location} {time}. When {char2} asked for help, {char} kindly {action} {number_to_words(b_num)} of the {obj}. How many {obj} does {char} still have?"
        elif category == "multiplication":
            return f"{char} and {char2} were organizing {obj} {location} {time}. They arranged {number_to_words(a_num)} groups, with {number_to_words(b_num)} items in each group. What is the total count of items they organized?"
        elif category == "division":
            return f"{time}, {char} prepared {number_to_words(a_num)} delicious {obj} {location}. {char} decided to share them equally with {char2} and {number_to_words(b_num - 1)} other friends (making {number_to_words(b_num)} people total). How many {obj} will each person enjoy?"
    
    else:  # complexity == 5
        # Very elaborate story with multiple steps
        char2 = random.choice([c for c in CHARACTERS if c != char])
        char3 = random.choice([c for c in CHARACTERS if c not in [char, char2]])
        times = ["on a beautiful sunny afternoon", "during an exciting adventure", "at a wonderful celebration"]
        locations = ["at the magnificent park with tall trees", "in the enchanting garden full of flowers", "at the grand festival downtown"]
        time = random.choice(times)
        location = random.choice(locations)
        
        if category == "addition":
            return f"{time}, {char} went {location} and {action} exactly {number_to_words(a_num)} amazing {obj}. Shortly after, {char2} and {char3} came by and together they {action} {number_to_words(b_num)} additional {obj}. If {char} keeps all the {obj}, how many wonderful {obj} will {char} have collected in total?"
        elif category == "subtraction":
            return f"{char} was thrilled to have {number_to_words(a_num)} precious {obj} that were collected {location} {time}. When {char2} and {char3} organized a charity event, {char} generously decided to {action.replace('gave away', 'donate')} {number_to_words(b_num)} of these {obj} to help others. How many valuable {obj} will {char} have left after this kind donation?"
        elif category == "multiplication":
            return f"{time}, {char}, {char2}, and {char3} discovered {location} some mysterious {obj}. They found {number_to_words(a_num)} large containers, and after careful counting, realized each container held exactly {number_to_words(b_num)} precious items. What is the grand total of all the items they discovered together?"
        elif category == "division":
            return f"{char} spent all {time} {location} preparing an impressive collection of {number_to_words(a_num)} homemade {obj}. Planning a fair distribution, {char} wants to share these equally among a group that includes {char2}, {char3}, and {number_to_words(b_num - 2)} other wonderful friends (totaling {number_to_words(b_num)} people). How many {obj} will each lucky person receive?"
    
    return question

def make_choices(correct):
    choices = {correct}
    while len(choices) < 4:
        delta = random.randint(-6, 6)
        if delta == 0:
            delta = random.choice([-1, 1])
        choices.add(correct + delta)
    choices = list(choices)
    random.shuffle(choices)
    return choices

# -----------------------------
# UI
# -----------------------------
# Initialize database
init_database()

st.set_page_config(page_title="OZZ Math Game", page_icon="🧮", initial_sidebar_state='collapsed')
cols = st.columns([3, 2])
with cols[0]:
    st.title("🧮 OZZ Math Game")

# Create / Select user
with st.sidebar:
    st.subheader("Player")
    new_name = st.text_input("Add new player name")
    if st.button("Add Player"):
        if new_name.strip():
            ensure_user(new_name.strip())
            st.success(f"Added {new_name.strip()}")
            st.rerun()

users = get_all_users()
with cols[1]:
    selected_user = st.selectbox("Select player", options=users) if users else None

st.divider()
cols = st.columns((3, 2))

# Game settings
with cols[0]:
    st.subheader("Game Settings")
    mode = st.radio("Answer Mode", options=["Multiple Choice", "Text Input", "Reading Problem"], horizontal=True)

with cols[1]:
    category = st.selectbox("Category", options=CATEGORIES + ["random"])

# Complexity slider
complexity = st.slider(
    "🎯 Complexity Level",
    min_value=1,
    max_value=5,
    value=2,
    help="1: Very Easy (1-5) | 2: Easy (1-10) | 3: Medium (1-12) | 4: Hard (5-20) | 5: Very Hard (10-50)"
)

if selected_user:
    ensure_user(selected_user)

    # Initialize session state
    if "current_problem" not in st.session_state:
        st.session_state.current_problem = None
        st.session_state.choices = None
        st.session_state.last_category = None
        st.session_state.last_complexity = None
    
    # Check if category or complexity changed
    if st.session_state.last_category != category or st.session_state.last_complexity != complexity:
        st.session_state.last_category = category
        st.session_state.last_complexity = complexity
        chosen_category = random.choice(CATEGORIES) if category == "random" else category
        q, a = generate_new_problem(chosen_category, complexity, selected_user)
        st.session_state.current_problem = {
            "category": chosen_category,
            "question": q,
            "answer": a,
            "complexity": complexity
        }
        st.session_state.choices = make_choices(a)
    
    # Generate initial problem if none exists
    if st.session_state.current_problem is None:
        chosen_category = random.choice(CATEGORIES) if category == "random" else category
        q, a = generate_new_problem(chosen_category, complexity, selected_user)
        st.session_state.current_problem = {
            "category": chosen_category,
            "question": q,
            "answer": a,
            "complexity": complexity
        }
        st.session_state.choices = make_choices(a)

    prob = st.session_state.current_problem
    st.write(f"**Category:** {prob['category'].title()} | **Level:** {prob.get('complexity', 2)}")
    
    # Display the problem based on mode
    if mode == "Reading Problem":
        reading_question = problem_to_reading(prob['category'], prob['question'], prob['answer'], prob.get('complexity', 2))
        st.markdown(f"### {reading_question}")
    else:
        st.markdown(f"# {prob['question']}")

    if mode == "Text Input":
        user_answer = st.text_input("Your answer", key="text_answer")
        if st.button("Submit Answer"):
            try:
                ans_int = int(user_answer)
                correct = ans_int == prob["answer"]
            except (TypeError, ValueError):
                correct = False

            if correct:
                is_mastered = record_attempt(selected_user, prob["category"], prob["question"], True)
                st.balloons()
                if is_mastered:
                    st.success("Correct! 🎉 You've mastered this problem! ⭐")
                else:
                    st.success("Correct! 🎉")
            else:
                record_attempt(selected_user, prob["category"], prob["question"], False)
                st.error(f"Wrong. Correct answer: {prob['answer']}")
    
    elif mode == "Reading Problem":
        col1, col2 = st.columns(2)
        choices = st.session_state.choices
        
        with col1:
            if st.button(str(choices[0]), use_container_width=True, key="btn0"):
                correct = choices[0] == prob["answer"]
                if correct:
                    is_mastered = record_attempt(selected_user, prob["category"], prob["question"], True)
                    st.balloons()
                    if is_mastered:
                        st.success("Correct! 🎉 You've mastered this problem! ⭐")
                    else:
                        st.success("Correct! 🎉")
                else:
                    record_attempt(selected_user, prob["category"], prob["question"], False)
                    st.error(f"Wrong. Correct answer: {prob['answer']}")
            
            if st.button(str(choices[2]), use_container_width=True, key="btn2"):
                correct = choices[2] == prob["answer"]
                if correct:
                    is_mastered = record_attempt(selected_user, prob["category"], prob["question"], True)
                    st.balloons()
                    if is_mastered:
                        st.success("Correct! 🎉 You've mastered this problem! ⭐")
                    else:
                        st.success("Correct! 🎉")
                else:
                    record_attempt(selected_user, prob["category"], prob["question"], False)
                    st.error(f"Wrong. Correct answer: {prob['answer']}")
        
        with col2:
            if st.button(str(choices[1]), use_container_width=True, key="btn1"):
                correct = choices[1] == prob["answer"]
                if correct:
                    is_mastered = record_attempt(selected_user, prob["category"], prob["question"], True)
                    st.balloons()
                    if is_mastered:
                        st.success("Correct! 🎉 You've mastered this problem! ⭐")
                    else:
                        st.success("Correct! 🎉")
                else:
                    record_attempt(selected_user, prob["category"], prob["question"], False)
                    st.error(f"Wrong. Correct answer: {prob['answer']}")
            
            if st.button(str(choices[3]), use_container_width=True, key="btn3"):
                correct = choices[3] == prob["answer"]
                if correct:
                    is_mastered = record_attempt(selected_user, prob["category"], prob["question"], True)
                    st.balloons()
                    if is_mastered:
                        st.success("Correct! 🎉 You've mastered this problem! ⭐")
                    else:
                        st.success("Correct! 🎉")
                else:
                    record_attempt(selected_user, prob["category"], prob["question"], False)
                    st.error(f"Wrong. Correct answer: {prob['answer']}")
    
    else:  # Multiple Choice
        col1, col2 = st.columns(2)
        choices = st.session_state.choices
        
        with col1:
            if st.button(str(choices[0]), use_container_width=True, key="btn0"):
                correct = choices[0] == prob["answer"]
                if correct:
                    is_mastered = record_attempt(selected_user, prob["category"], prob["question"], True)
                    st.balloons()
                    if is_mastered:
                        st.success("Correct! 🎉 You've mastered this problem! ⭐")
                    else:
                        st.success("Correct! 🎉")
                else:
                    record_attempt(selected_user, prob["category"], prob["question"], False)
                    st.error(f"Wrong. Correct answer: {prob['answer']}")
            
            if st.button(str(choices[2]), use_container_width=True, key="btn2"):
                correct = choices[2] == prob["answer"]
                if correct:
                    is_mastered = record_attempt(selected_user, prob["category"], prob["question"], True)
                    st.balloons()
                    if is_mastered:
                        st.success("Correct! 🎉 You've mastered this problem! ⭐")
                    else:
                        st.success("Correct! 🎉")
                else:
                    record_attempt(selected_user, prob["category"], prob["question"], False)
                    st.error(f"Wrong. Correct answer: {prob['answer']}")
        
        with col2:
            if st.button(str(choices[1]), use_container_width=True, key="btn1"):
                correct = choices[1] == prob["answer"]
                if correct:
                    is_mastered = record_attempt(selected_user, prob["category"], prob["question"], True)
                    st.balloons()
                    if is_mastered:
                        st.success("Correct! 🎉 You've mastered this problem! ⭐")
                    else:
                        st.success("Correct! 🎉")
                else:
                    record_attempt(selected_user, prob["category"], prob["question"], False)
                    st.error(f"Wrong. Correct answer: {prob['answer']}")
            
            if st.button(str(choices[3]), use_container_width=True, key="btn3"):
                correct = choices[3] == prob["answer"]
                if correct:
                    is_mastered = record_attempt(selected_user, prob["category"], prob["question"], True)
                    st.balloons()
                    if is_mastered:
                        st.success("Correct! 🎉 You've mastered this problem! ⭐")
                    else:
                        st.success("Correct! 🎉")
                else:
                    record_attempt(selected_user, prob["category"], prob["question"], False)
                    st.error(f"Wrong. Correct answer: {prob['answer']}")

    # New Problem button
    if st.button("New Problem", use_container_width=True):
        chosen_category = random.choice(CATEGORIES) if category == "random" else category
        q, a = generate_new_problem(chosen_category, complexity, selected_user)
        st.session_state.current_problem = {
            "category": chosen_category,
            "question": q,
            "answer": a,
            "complexity": complexity
        }
        st.session_state.choices = make_choices(a)
        st.rerun()

    # Scores
    st.divider()
    if st.button("View Scores", use_container_width=True):
        st.subheader("Scores")
        user_scores = get_user_scores(selected_user)
        for cat in CATEGORIES:
            scores = user_scores.get(cat, {'total_right': 0, 'total_wrong': 0})
            st.write(f"**{cat.title()}** — Right: {scores['total_right']} | Wrong: {scores['total_wrong']}")
            with st.expander(f"Equations for {cat.title()}"):
                eqs = get_category_equations(selected_user, cat)
                if not eqs:
                    st.write("No attempts yet.")
                else:
                    for eq, stats in eqs.items():
                        mastered = " ⭐ MASTERED" if stats['right'] >= 3 else ""
                        st.write(f"{eq} — Right: {stats['right']} | Wrong: {stats['wrong']}{mastered}")

else:
    st.info("Add a player to start.")