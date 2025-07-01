from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import os
from sqlalchemy.types import JSON as SQLAlchemyJSON
import json
import pandas as pd
import ast

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
    activity_multiplier = float(data.get('activity_multiplier', 1.2))
    # Apply activity multiplier
    adjusted_calories = int(target_calories * activity_multiplier)
    # Calculate meal distribution (e.g., 35% breakfast, 25% lunch, 20% dinner, 10% afternoon tea, 10% snack)
    breakfast_calories = int(adjusted_calories * 0.35)
    lunch_calories = int(adjusted_calories * 0.25)
    dinner_calories = int(adjusted_calories * 0.2)
    afternoon_tea_calories = int(adjusted_calories * 0.1)
    snack_calories = int(adjusted_calories * 0.1)
    # Get dishes for each meal type, filtered by preferences
    breakfast_dishes = filter_dishes_by_preferences(Dish.query.filter_by(meal_type='breakfast').all(), preferences)
    lunch_dishes = filter_dishes_by_preferences(Dish.query.filter_by(meal_type='lunch').all(), preferences)
    dinner_dishes = filter_dishes_by_preferences(Dish.query.filter_by(meal_type='dinner').all(), preferences)
    afternoon_tea_dishes = filter_dishes_by_preferences(Dish.query.filter_by(meal_type='afternoon_tea').all(), preferences)
    snack_dishes = filter_dishes_by_preferences(Dish.query.filter_by(meal_type='snack').all(), preferences)
    # Generate meal combinations
    breakfast = generate_meal_combination(breakfast_dishes, breakfast_calories, 2, 3)
    lunch = generate_meal_combination(lunch_dishes, lunch_calories, 2, 3)
    dinner = generate_meal_combination(dinner_dishes, dinner_calories, 2, 3)
    afternoon_tea = generate_meal_combination(afternoon_tea_dishes, afternoon_tea_calories, 1, 2)
    snack = generate_meal_combination(snack_dishes, snack_calories, 1, 2)
    # Calculate totals
    all_meals = [breakfast, lunch, dinner, afternoon_tea, snack]
    total_calories = sum(meal['total_calories'] for meal in all_meals if meal)
    plan = {
        'breakfast': breakfast,
        'lunch': lunch,
        'dinner': dinner,
        'afternoon_tea': afternoon_tea,
        'snack': snack,
        'total_calories': total_calories,
        'target_calories': adjusted_calories,
        'activity_multiplier': activity_multiplier
    }
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
        try:
            # Read first 10,000 rows from CSV in data/ directory
            df = pd.read_csv('data/RAW_recipes.csv', nrows=10000)
            meal_types = ['breakfast', 'lunch', 'dinner', 'snack', 'afternoon_tea']
            loaded_count = 0
            
            for _, row in df.iterrows():
                try:
                    # Parse nutrition string to list
                    nutrition_str = row['nutrition']
                    if not isinstance(nutrition_str, str):
                        continue
                    
                    nutrition = ast.literal_eval(nutrition_str)
                    if not (isinstance(nutrition, list) and len(nutrition) >= 4):
                        continue
                    
                    # Extract nutrition values according to specification:
                    # nutrition[0] = calories, nutrition[1] = protein, nutrition[2] = fat, nutrition[3] = carbs
                    calories = int(nutrition[0]) if nutrition[0] > 0 else 100
                    protein = float(nutrition[1]) if nutrition[1] > 0 else 5.0
                    fat = float(nutrition[2]) if nutrition[2] > 0 else 5.0
                    carbs = float(nutrition[3]) if nutrition[3] > 0 else 15.0
                    
                    # Randomly assign meal type
                    meal_type = random.choice(meal_types)
                    
                    # Create dish
                    dish = Dish(
                        name=row['name'][:100],  # Truncate if too long
                        calories=calories,
                        protein=protein,
                        carbs=carbs,
                        fat=fat,
                        meal_type=meal_type,
                        vegetarian=False,  # Set to False for now
                        vegan=False,
                        gluten_free=False,
                        low_carb=False
                    )
                    db.session.add(dish)
                    loaded_count += 1
                    
                except (ValueError, IndexError, SyntaxError, TypeError) as e:
                    # Skip rows with invalid data
                    continue
            
            db.session.commit()
            print(f"Loaded {loaded_count} dishes from CSV")
            
        except Exception as e:
            print(f"Error loading CSV: {e}")
            # If CSV loading fails, the database will be empty
            pass

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
    init_db()  # Initialize database with CSV data
    app.run(debug=True, port=5001) 