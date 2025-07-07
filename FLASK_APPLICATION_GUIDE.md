# Flask Meal Planning Application - Complete Guide

## Table of Contents
1. [Project Structure Overview](#project-structure-overview)
2. [How Flask Works](#how-flask-works)
3. [Database Architecture](#database-architecture)
4. [API Endpoints](#api-endpoints)
5. [Frontend Integration](#frontend-integration)
6. [Application Flow](#application-flow)

---

## Project Structure Overview

### File Organization
```
New-Meal-Plan/
├── app.py                # Main Flask application (580 lines)
├── requirements.txt      # Versions
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
├── cursor_prompts_log.md # Development log
├── instance/
│   └── meals.db          # SQLite database file
├── static/               # Static assets (CSS, JS, images)
│   ├── css/
│   │   └── style.css     # Application styling
│   └── js/
│       └── app.js        # Frontend JavaScript
└── templates/            # HTML templates
    ├── base.html         # Base template with common layout
    ├── index.html        # Home page
    ├── plan.html         # Meal plan generation page
    ├── meals.html        # Dish management page
    ├── saved.html        # Saved plans page
    └── error.html        # Error page
```

### Code Structure Breakdown

#### 1. **Main Application (`app.py`)**
- **Lines 1-15**: Imports and Flask initialization
- **Lines 17-50**: Database models (Dish, MealPlan, SavedPlan)
- **Lines 52-95**: Sample dish data for demonstration
- **Lines 97-115**: Web page routes (HTML templates)
- **Lines 117-250**: API endpoints (JSON responses)
- **Lines 252-350**: Core meal generation algorithms
- **Lines 352-400**: Database operations and utilities
- **Lines 402-580**: Helper functions and application startup

#### 2. **Frontend Templates (`templates/`)**
- **`base.html`**: Master template with navigation and common elements
- **`index.html`**: Landing page with app introduction
- **`plan.html`**: Interactive meal plan generator
- **`meals.html`**: Dish management interface
- **`saved.html`**: Saved plans history viewer

#### 3. **Static Assets (`static/`)**
- **`style.css`**: Application styling and responsive design
- **`app.js`**: Frontend JavaScript for dynamic interactions

---

## How Flask Works

### What is Flask?
Flask is a lightweight web framework for Python that allows you to build web applications by combining Python code with HTML templates. It follows the **Model-View-Controller (MVC)** pattern.

### Core Flask Concepts

#### 1. **Application Instance**
```python
from flask import Flask
app = Flask(__name__)
```
- Creates a Flask application object
- `__name__` tells Flask where to look for templates and static files

#### 2. **Route Decorators**
```python
@app.route('/')
def index():
    return render_template('index.html')
```
- `@app.route('/')` defines URL patterns
- Functions return HTML responses using `render_template()`

#### 3. **Template Rendering**
```python
@app.route('/meals')
def meals():
    dishes = Dish.query.all()  # Get data from database
    return render_template('meals.html', dishes=dishes)  # Pass data to template
```
- Python data is passed to HTML templates
- Templates use Jinja2 syntax to display dynamic content

#### 4. **Request Handling**
```python
@app.route('/api/generate_plan', methods=['POST'])
def generate_plan():
    data = request.get_json()  # Get JSON data from frontend
    # Process data with Python logic
    return jsonify(result)  # Return JSON response
```

### How Flask Combines Python with Websites

#### **Backend (Python) → Frontend (HTML/JavaScript) Flow:**

1. **User visits a URL** (e.g., `/plan`)
2. **Flask route handler** processes the request
3. **Python logic** executes (database queries, calculations)
4. **Data is passed** to HTML template
5. **Template renders** with dynamic content
6. **HTML is sent** to user's browser
7. **JavaScript** handles interactive features

#### **Example Flow in Your App:**

```
User clicks "Generate Plan" 
    ↓
JavaScript sends POST request to /api/generate_plan
    ↓
Flask receives request with calorie target and preferences
    ↓
Python algorithm generates meal combinations
    ↓
Flask returns JSON response with meal plan
    ↓
JavaScript receives data and updates the page
```

---

## Database Architecture

### SQLAlchemy Integration
```python
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
```

### Database Models

#### 1. **Dish Model** (Core entity)
```python
class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    # Dietary flags
    vegetarian = db.Column(db.Boolean, default=False)
    vegan = db.Column(db.Boolean, default=False)
    gluten_free = db.Column(db.Boolean, default=False)
    low_carb = db.Column(db.Boolean, default=False)
```

#### 2. **MealPlan Model** (Future feature)
```python
class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_calories = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    # JSON strings storing dish IDs for each meal
    breakfast_dishes = db.Column(db.String(500))
    lunch_dishes = db.Column(db.String(500))
    dinner_dishes = db.Column(db.String(500))
    snack_dishes = db.Column(db.String(500))
```

#### 3. **SavedPlan Model** (User history)
```python
class SavedPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_calories = db.Column(db.Integer, nullable=False)
    total_protein = db.Column(db.Float, nullable=False)
    total_carbs = db.Column(db.Float, nullable=False)
    total_fat = db.Column(db.Float, nullable=False)
    plan_data = db.Column(db.Text, nullable=False)  # Complete plan as JSON
```

---

## API Endpoints

### Web Page Routes (Return HTML)
```python
@app.route('/')           # Home page
@app.route('/plan')       # Meal plan generator
@app.route('/meals')      # Dish management
@app.route('/saved')      # Saved plans history
```

### API Endpoints (Return JSON)
```python
@app.route('/api/generate_plan', methods=['POST'])  # Generate meal plan
@app.route('/api/dishes', methods=['GET'])          # Get all dishes
@app.route('/api/dishes', methods=['POST'])         # Add new dish
@app.route('/api/save_plan', methods=['POST'])      # Save meal plan
@app.route('/api/delete_plan/<int:plan_id>', methods=['POST'])  # Delete plan
```

### Request/Response Examples

#### Generate Meal Plan
**Request:**
```json
{
  "target_calories": 2000,
  "preferences": ["vegetarian", "gluten_free"],
  "selected_meals": ["breakfast", "lunch", "dinner", "snack"]
}
```

**Response:**
```json
{
  "total_calories": 1985,
  "target_calories": 2000,
  "breakfast": {
    "dishes": [...],
    "total_calories": 700,
    "total_protein": 25,
    "total_carbs": 120,
    "total_fat": 15
  },
  "lunch": {...},
  "dinner": {...},
  "snack": {...}
}
```

---

## Frontend Integration

### Template Inheritance
```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav>...</nav>
    <main>{% block content %}{% endblock %}</main>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
```

### Dynamic Content in Templates
```html
<!-- meals.html -->
{% for dish in dishes %}
<div class="dish-card">
    <h3>{{ dish.name }}</h3>
    <p>Calories: {{ dish.calories }}</p>
    <p>Protein: {{ dish.protein }}g</p>
    {% if dish.vegetarian %}
        <span class="badge">Vegetarian</span>
    {% endif %}
</div>
{% endfor %}
```

### JavaScript API Calls
```javascript
// app.js
async function generateMealPlan() {
    const response = await fetch('/api/generate_plan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            target_calories: 2000,
            preferences: ['vegetarian'],
            selected_meals: ['breakfast', 'lunch', 'dinner']
        })
    });
    
    const plan = await response.json();
    displayMealPlan(plan);
}
```

---

## Application Flow

### 1. **Application Startup**
```python
if __name__ == '__main__':
    init_db()        # Create database and add sample data
    app.run(debug=True)  # Start development server
```

### 2. **Database Initialization**
```python
def init_db():
    # Remove existing database
    if os.path.exists('meals.db'):
        os.remove('meals.db')
    
    # Create tables
    db.create_all()
    
    # Add sample dishes
    if Dish.query.count() == 0:
        for dish_data in SAMPLE_DISHES:
            dish = Dish(**dish_data)
            db.session.add(dish)
        db.session.commit()
```

### 3. **Meal Plan Generation Process**
1. **User Input**: Target calories, dietary preferences, selected meals
2. **Calorie Distribution**: Calculate calories per meal type
3. **Dish Filtering**: Filter dishes by preferences and meal type
4. **Combination Generation**: Create optimal dish combinations
5. **Calorie Adjustment**: Scale dishes if needed to match target
6. **Response**: Return complete meal plan with nutritional totals

### 4. **Data Flow Architecture**
```
User Interface (HTML/JS)
    ↓
Flask Routes (Python)
    ↓
Business Logic (Meal Generation)
    ↓
Database Operations (SQLAlchemy)
    ↓
SQLite Database
```

---

## Key Flask Features Used

### 1. **Template Engine (Jinja2)**
- Dynamic HTML generation
- Template inheritance
- Conditional rendering
- Loop structures

### 2. **Request Handling**
- GET/POST request processing
- JSON data parsing
- Query parameter extraction
- File uploads (if needed)

### 3. **Database Integration**
- SQLAlchemy ORM
- Model definitions
- Query building
- Session management

### 4. **Static File Serving**
- CSS and JavaScript files
- Image assets
- File organization

### 5. **Error Handling**
- Custom error pages
- HTTP status codes
- Exception handling

---

## Development and Deployment

### Development Server
```bash
python app.py
# Server runs on http://localhost:5000
```

### Production Considerations
- Use production WSGI server (Gunicorn, uWSGI)
- Configure environment variables
- Set up proper database (PostgreSQL, MySQL)
- Implement security measures
- Add logging and monitoring

### Dependencies (requirements.txt)
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
SQLAlchemy==2.0.21
Werkzeug==2.3.7
```

---

This Flask application demonstrates a complete web application with:
- **Backend logic** in Python
- **Database persistence** with SQLAlchemy
- **Dynamic frontend** with HTML templates and JavaScript
- **RESTful API** for data exchange
- **User interface** for meal planning

The combination of Flask's simplicity and Python's power makes it ideal for building web applications that require complex business logic, like this meal planning system. 