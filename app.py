from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import os
from sqlalchemy.types import JSON as SQLAlchemyJSON
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vegetarian = db.Column(db.Boolean, default=False)
    vegan = db.Column(db.Boolean, default=False)
    gluten_free = db.Column(db.Boolean, default=False)
    low_carb = db.Column(db.Boolean, default=False)

class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_calories = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    breakfast_dishes = db.Column(db.String(500))  # JSON string of dish IDs
    lunch_dishes = db.Column(db.String(500))
    dinner_dishes = db.Column(db.String(500))
    snack_dishes = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavedPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_calories = db.Column(db.Integer, nullable=False)
    total_protein = db.Column(db.Float, nullable=False)
    total_carbs = db.Column(db.Float, nullable=False)
    total_fat = db.Column(db.Float, nullable=False)
    plan_data = db.Column(db.Text, nullable=False)  # JSON-encoded meal plan

# Sample dish data
SAMPLE_DISHES = [
    # Breakfast dishes
    {"name": "Oatmeal", "calories": 150, "protein": 6, "carbs": 27, "fat": 3, "meal_type": "breakfast", "vegetarian": True, "vegan": True, "gluten_free": False, "low_carb": False},
    {"name": "Fresh Berries", "calories": 50, "protein": 1, "carbs": 12, "fat": 0, "meal_type": "breakfast", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Greek Yogurt", "calories": 120, "protein": 15, "carbs": 8, "fat": 2, "meal_type": "breakfast", "vegetarian": True, "vegan": False, "gluten_free": True, "low_carb": True},
    {"name": "Honey", "calories": 60, "protein": 0, "carbs": 17, "fat": 0, "meal_type": "breakfast", "vegetarian": True, "vegan": False, "gluten_free": True, "low_carb": False},
    {"name": "Scrambled Eggs", "calories": 200, "protein": 14, "carbs": 2, "fat": 15, "meal_type": "breakfast", "vegetarian": True, "vegan": False, "gluten_free": True, "low_carb": True},
    {"name": "Whole Grain Toast", "calories": 80, "protein": 4, "carbs": 15, "fat": 1, "meal_type": "breakfast", "vegetarian": True, "vegan": False, "gluten_free": False, "low_carb": False},
    {"name": "Banana", "calories": 100, "protein": 1, "carbs": 26, "fat": 0, "meal_type": "breakfast", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": False},
    {"name": "Almond Butter", "calories": 100, "protein": 4, "carbs": 3, "fat": 8, "meal_type": "breakfast", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    
    # Lunch dishes
    {"name": "Grilled Chicken Breast", "calories": 250, "protein": 35, "carbs": 0, "fat": 12, "meal_type": "lunch", "vegetarian": False, "vegan": False, "gluten_free": True, "low_carb": True},
    {"name": "Mixed Greens", "calories": 20, "protein": 2, "carbs": 4, "fat": 0, "meal_type": "lunch", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Cherry Tomatoes", "calories": 30, "protein": 1, "carbs": 6, "fat": 0, "meal_type": "lunch", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Olive Oil Dressing", "calories": 100, "protein": 0, "carbs": 0, "fat": 11, "meal_type": "lunch", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Quinoa", "calories": 200, "protein": 8, "carbs": 39, "fat": 4, "meal_type": "lunch", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": False},
    {"name": "Roasted Vegetables", "calories": 150, "protein": 4, "carbs": 25, "fat": 5, "meal_type": "lunch", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": False},
    {"name": "Turkey Breast", "calories": 180, "protein": 25, "carbs": 0, "fat": 8, "meal_type": "lunch", "vegetarian": False, "vegan": False, "gluten_free": True, "low_carb": True},
    {"name": "Whole Grain Bread", "calories": 120, "protein": 6, "carbs": 22, "fat": 2, "meal_type": "lunch", "vegetarian": True, "vegan": False, "gluten_free": False, "low_carb": False},
    {"name": "Lettuce", "calories": 10, "protein": 1, "carbs": 2, "fat": 0, "meal_type": "lunch", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Mustard", "calories": 10, "protein": 0, "carbs": 2, "fat": 0, "meal_type": "lunch", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    
    # Dinner dishes
    {"name": "Salmon Fillet", "calories": 300, "protein": 35, "carbs": 0, "fat": 18, "meal_type": "dinner", "vegetarian": False, "vegan": False, "gluten_free": True, "low_carb": True},
    {"name": "Steamed Broccoli", "calories": 50, "protein": 4, "carbs": 10, "fat": 0, "meal_type": "dinner", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Brown Rice", "calories": 150, "protein": 3, "carbs": 32, "fat": 1, "meal_type": "dinner", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": False},
    {"name": "Lean Beef Strips", "calories": 250, "protein": 25, "carbs": 0, "fat": 15, "meal_type": "dinner", "vegetarian": False, "vegan": False, "gluten_free": True, "low_carb": True},
    {"name": "Stir Fry Vegetables", "calories": 100, "protein": 4, "carbs": 15, "fat": 3, "meal_type": "dinner", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": False},
    {"name": "Soy Sauce", "calories": 20, "protein": 2, "carbs": 4, "fat": 0, "meal_type": "dinner", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Whole Wheat Pasta", "calories": 200, "protein": 8, "carbs": 40, "fat": 1, "meal_type": "dinner", "vegetarian": True, "vegan": False, "gluten_free": False, "low_carb": False},
    {"name": "Tomato Sauce", "calories": 80, "protein": 2, "carbs": 12, "fat": 3, "meal_type": "dinner", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": False},
    {"name": "Parmesan Cheese", "calories": 120, "protein": 8, "carbs": 2, "fat": 8, "meal_type": "dinner", "vegetarian": True, "vegan": False, "gluten_free": True, "low_carb": True},
    {"name": "Chickpeas", "calories": 150, "protein": 8, "carbs": 25, "fat": 3, "meal_type": "dinner", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": False},
    {"name": "Coconut Milk", "calories": 100, "protein": 1, "carbs": 2, "fat": 10, "meal_type": "dinner", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Curry Spices", "calories": 20, "protein": 1, "carbs": 4, "fat": 0, "meal_type": "dinner", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    
    # Snack dishes
    {"name": "Apple", "calories": 80, "protein": 0, "carbs": 21, "fat": 0, "meal_type": "snack", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": False},
    {"name": "Peanut Butter", "calories": 120, "protein": 6, "carbs": 4, "fat": 10, "meal_type": "snack", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Mixed Nuts", "calories": 180, "protein": 6, "carbs": 8, "fat": 16, "meal_type": "snack", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Carrot Sticks", "calories": 50, "protein": 1, "carbs": 12, "fat": 0, "meal_type": "snack", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Hummus", "calories": 100, "protein": 4, "carbs": 8, "fat": 6, "meal_type": "snack", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Greek Yogurt", "calories": 120, "protein": 15, "carbs": 8, "fat": 2, "meal_type": "snack", "vegetarian": True, "vegan": False, "gluten_free": True, "low_carb": True},
    # Afternoon Tea dishes
    {"name": "Green Tea", "calories": 2, "protein": 0, "carbs": 0, "fat": 0, "meal_type": "afternoon_tea", "vegetarian": True, "vegan": True, "gluten_free": True, "low_carb": True},
    {"name": "Scone", "calories": 180, "protein": 4, "carbs": 30, "fat": 6, "meal_type": "afternoon_tea", "vegetarian": True, "vegan": False, "gluten_free": False, "low_carb": False},
    {"name": "Fruit Tart", "calories": 220, "protein": 3, "carbs": 35, "fat": 9, "meal_type": "afternoon_tea", "vegetarian": True, "vegan": False, "gluten_free": False, "low_carb": False},
    {"name": "Cucumber Sandwich", "calories": 120, "protein": 3, "carbs": 20, "fat": 3, "meal_type": "afternoon_tea", "vegetarian": True, "vegan": False, "gluten_free": False, "low_carb": False},
    {"name": "Mini Quiche", "calories": 150, "protein": 6, "carbs": 10, "fat": 9, "meal_type": "afternoon_tea", "vegetarian": True, "vegan": False, "gluten_free": False, "low_carb": False},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plan', methods=['GET'])
def plan():
    return render_template('plan.html')

@app.route('/meals')
def meals():
    dishes = Dish.query.all()
    return render_template('meals.html', dishes=dishes)

@app.route('/api/generate_plan', methods=['POST'])
def generate_plan():
    data = request.get_json()
    target_calories = int(data.get('target_calories', 2000))
    preferences = data.get('preferences', [])
    selected_meals = data.get('selected_meals', ['breakfast', 'lunch', 'dinner', 'snack', 'afternoon_tea'])
    
    # Use target calories directly without activity multiplier
    adjusted_calories = target_calories
    
    # Define meal distribution percentages
    meal_distribution = {
        'breakfast': 0.35,
        'lunch': 0.25,
        'dinner': 0.2,
        'afternoon_tea': 0.1,
        'snack': 0.1
    }
    
    # Calculate calories for selected meals only
    total_percentage = sum(meal_distribution[meal] for meal in selected_meals)
    meal_calories = {}
    for meal in selected_meals:
        meal_calories[meal] = int(adjusted_calories * meal_distribution[meal] / total_percentage)
    
    # Get dishes for each selected meal type, filtered by preferences
    meal_dishes = {}
    for meal in selected_meals:
        meal_dishes[meal] = filter_dishes_by_preferences(Dish.query.filter_by(meal_type=meal).all(), preferences)
    
    # Generate meal combinations for selected meals
    generated_meals = {}
    for meal in selected_meals:
        min_dishes = 2 if meal in ['breakfast', 'lunch', 'dinner'] else 1
        max_dishes = 3 if meal in ['breakfast', 'lunch', 'dinner'] else 2
        generated_meals[meal] = generate_meal_combination(meal_dishes[meal], meal_calories[meal], min_dishes, max_dishes)
    
    # Calculate totals for selected meals only
    total_calories = sum(meal['total_calories'] for meal in generated_meals.values() if meal)
    
    # Build plan with only selected meals
    plan = {
        'total_calories': total_calories,
        'target_calories': adjusted_calories
    }
    
    # Add selected meals to plan
    for meal in selected_meals:
        plan[meal] = generated_meals[meal]
    
    return jsonify(plan)

def generate_meal_combination(dishes, target_calories, min_dishes=2, max_dishes=3):
    """Generate a combination of dishes that best matches the target calories"""
    if not dishes:
        return None
    
    best_combination = None
    best_difference = float('inf')
    
    # Try different combinations of dishes
    for num_dishes in range(min_dishes, min(max_dishes + 1, len(dishes) + 1)):
        # Generate multiple random combinations
        for _ in range(10):  # Try 10 random combinations
            selected_dishes = random.sample(dishes, num_dishes)
            total_calories = sum(dish.calories for dish in selected_dishes)
            
            # Check if this combination is better
            difference = abs(total_calories - target_calories)
            if difference < best_difference:
                best_difference = difference
                best_combination = selected_dishes
    
    if not best_combination:
        return None
    
    # Calculate totals
    total_calories = sum(dish.calories for dish in best_combination)
    total_protein = sum(dish.protein for dish in best_combination)
    total_carbs = sum(dish.carbs for dish in best_combination)
    total_fat = sum(dish.fat for dish in best_combination)
    
    return {
        'dishes': [dish.to_dict() for dish in best_combination],
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fat': total_fat
    }

def filter_dishes_by_preferences(dishes, preferences):
    if not preferences:
        return dishes
    filtered = []
    for dish in dishes:
        if (
            ('vegetarian' in preferences and not dish.vegetarian) or
            ('vegan' in preferences and not dish.vegan) or
            ('gluten_free' in preferences and not dish.gluten_free) or
            ('low_carb' in preferences and not dish.low_carb)
        ):
            continue
        filtered.append(dish)
    return filtered

@app.route('/api/dishes', methods=['GET'])
def get_dishes():
    meal_type = request.args.get('type')
    if meal_type:
        dishes = Dish.query.filter_by(meal_type=meal_type).all()
    else:
        dishes = Dish.query.all()
    
    return jsonify([dish.to_dict() for dish in dishes])

@app.route('/api/dishes', methods=['POST'])
def add_dish():
    data = request.get_json()
    dish = Dish(
        name=data['name'],
        calories=int(data['calories']),
        protein=float(data['protein']),
        carbs=float(data['carbs']),
        fat=float(data['fat']),
        meal_type=data['meal_type'],
        vegetarian=data.get('vegetarian', False),
        vegan=data.get('vegan', False),
        gluten_free=data.get('gluten_free', False),
        low_carb=data.get('low_carb', False)
    )
    db.session.add(dish)
    db.session.commit()
    return jsonify(dish.to_dict()), 201

@app.route('/saved')
def saved():
    plans = SavedPlan.query.order_by(SavedPlan.timestamp.desc()).all()
    return render_template('saved.html', plans=plans)

@app.route('/api/save_plan', methods=['POST'])
def save_plan():
    data = request.get_json()
    plan = data.get('plan')
    if not plan:
        return jsonify({'error': 'No plan data provided'}), 400
    # Calculate totals
    total_calories = plan.get('total_calories', 0)
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    for meal_key in ['breakfast', 'lunch', 'dinner', 'snack', 'afternoon_tea']:
        meal = plan.get(meal_key)
        if meal:
            total_protein += meal.get('total_protein', 0)
            total_carbs += meal.get('total_carbs', 0)
            total_fat += meal.get('total_fat', 0)
    saved = SavedPlan(
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        plan_data=json.dumps(plan)
    )
    db.session.add(saved)
    db.session.commit()
    return jsonify({'success': True, 'id': saved.id})

@app.route('/api/delete_plan/<int:plan_id>', methods=['POST'])
def delete_plan(plan_id):
    plan = SavedPlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Plan not found'}), 404
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'success': True})

def init_db():
    db_path = 'meals.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    with app.app_context():
        db.create_all()
        # Add sample dishes if database is empty
        if Dish.query.count() == 0:
            for dish_data in SAMPLE_DISHES:
                dish = Dish(**dish_data)
                db.session.add(dish)
            db.session.commit()

# Add to_dict method to Dish model
def dish_to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'calories': self.calories,
        'protein': self.protein,
        'carbs': self.carbs,
        'fat': self.fat,
        'meal_type': self.meal_type,
        'vegetarian': self.vegetarian,
        'vegan': self.vegan,
        'gluten_free': self.gluten_free,
        'low_carb': self.low_carb
    }

Dish.to_dict = dish_to_dict

# Optional: Add a global error handler for 403 to help debug
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', message='403 Forbidden: You do not have permission to access this page.'), 403

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 