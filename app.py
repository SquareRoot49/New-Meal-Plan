from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

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

class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_calories = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    breakfast_dishes = db.Column(db.String(500))  # JSON string of dish IDs
    lunch_dishes = db.Column(db.String(500))
    dinner_dishes = db.Column(db.String(500))
    snack_dishes = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Sample dish data
SAMPLE_DISHES = [
    # Breakfast dishes
    {"name": "Oatmeal", "calories": 150, "protein": 6, "carbs": 27, "fat": 3, "meal_type": "breakfast"},
    {"name": "Fresh Berries", "calories": 50, "protein": 1, "carbs": 12, "fat": 0, "meal_type": "breakfast"},
    {"name": "Greek Yogurt", "calories": 120, "protein": 15, "carbs": 8, "fat": 2, "meal_type": "breakfast"},
    {"name": "Honey", "calories": 60, "protein": 0, "carbs": 17, "fat": 0, "meal_type": "breakfast"},
    {"name": "Scrambled Eggs", "calories": 200, "protein": 14, "carbs": 2, "fat": 15, "meal_type": "breakfast"},
    {"name": "Whole Grain Toast", "calories": 80, "protein": 4, "carbs": 15, "fat": 1, "meal_type": "breakfast"},
    {"name": "Banana", "calories": 100, "protein": 1, "carbs": 26, "fat": 0, "meal_type": "breakfast"},
    {"name": "Almond Butter", "calories": 100, "protein": 4, "carbs": 3, "fat": 8, "meal_type": "breakfast"},
    
    # Lunch dishes
    {"name": "Grilled Chicken Breast", "calories": 250, "protein": 35, "carbs": 0, "fat": 12, "meal_type": "lunch"},
    {"name": "Mixed Greens", "calories": 20, "protein": 2, "carbs": 4, "fat": 0, "meal_type": "lunch"},
    {"name": "Cherry Tomatoes", "calories": 30, "protein": 1, "carbs": 6, "fat": 0, "meal_type": "lunch"},
    {"name": "Olive Oil Dressing", "calories": 100, "protein": 0, "carbs": 0, "fat": 11, "meal_type": "lunch"},
    {"name": "Quinoa", "calories": 200, "protein": 8, "carbs": 39, "fat": 4, "meal_type": "lunch"},
    {"name": "Roasted Vegetables", "calories": 150, "protein": 4, "carbs": 25, "fat": 5, "meal_type": "lunch"},
    {"name": "Turkey Breast", "calories": 180, "protein": 25, "carbs": 0, "fat": 8, "meal_type": "lunch"},
    {"name": "Whole Grain Bread", "calories": 120, "protein": 6, "carbs": 22, "fat": 2, "meal_type": "lunch"},
    {"name": "Lettuce", "calories": 10, "protein": 1, "carbs": 2, "fat": 0, "meal_type": "lunch"},
    {"name": "Mustard", "calories": 10, "protein": 0, "carbs": 2, "fat": 0, "meal_type": "lunch"},
    
    # Dinner dishes
    {"name": "Salmon Fillet", "calories": 300, "protein": 35, "carbs": 0, "fat": 18, "meal_type": "dinner"},
    {"name": "Steamed Broccoli", "calories": 50, "protein": 4, "carbs": 10, "fat": 0, "meal_type": "dinner"},
    {"name": "Brown Rice", "calories": 150, "protein": 3, "carbs": 32, "fat": 1, "meal_type": "dinner"},
    {"name": "Lean Beef Strips", "calories": 250, "protein": 25, "carbs": 0, "fat": 15, "meal_type": "dinner"},
    {"name": "Stir Fry Vegetables", "calories": 100, "protein": 4, "carbs": 15, "fat": 3, "meal_type": "dinner"},
    {"name": "Soy Sauce", "calories": 20, "protein": 2, "carbs": 4, "fat": 0, "meal_type": "dinner"},
    {"name": "Whole Wheat Pasta", "calories": 200, "protein": 8, "carbs": 40, "fat": 1, "meal_type": "dinner"},
    {"name": "Tomato Sauce", "calories": 80, "protein": 2, "carbs": 12, "fat": 3, "meal_type": "dinner"},
    {"name": "Parmesan Cheese", "calories": 120, "protein": 8, "carbs": 2, "fat": 8, "meal_type": "dinner"},
    {"name": "Chickpeas", "calories": 150, "protein": 8, "carbs": 25, "fat": 3, "meal_type": "dinner"},
    {"name": "Coconut Milk", "calories": 100, "protein": 1, "carbs": 2, "fat": 10, "meal_type": "dinner"},
    {"name": "Curry Spices", "calories": 20, "protein": 1, "carbs": 4, "fat": 0, "meal_type": "dinner"},
    
    # Snack dishes
    {"name": "Apple", "calories": 80, "protein": 0, "carbs": 21, "fat": 0, "meal_type": "snack"},
    {"name": "Peanut Butter", "calories": 120, "protein": 6, "carbs": 4, "fat": 10, "meal_type": "snack"},
    {"name": "Mixed Nuts", "calories": 180, "protein": 6, "carbs": 8, "fat": 16, "meal_type": "snack"},
    {"name": "Carrot Sticks", "calories": 50, "protein": 1, "carbs": 12, "fat": 0, "meal_type": "snack"},
    {"name": "Hummus", "calories": 100, "protein": 4, "carbs": 8, "fat": 6, "meal_type": "snack"},
    {"name": "Greek Yogurt", "calories": 120, "protein": 15, "carbs": 8, "fat": 2, "meal_type": "snack"},
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plan')
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
    
    # Calculate meal distribution (40% breakfast, 30% lunch, 25% dinner, 5% snack)
    breakfast_calories = int(target_calories * 0.4)
    lunch_calories = int(target_calories * 0.3)
    dinner_calories = int(target_calories * 0.25)
    snack_calories = int(target_calories * 0.05)
    
    # Get dishes for each meal type
    breakfast_dishes = Dish.query.filter_by(meal_type='breakfast').all()
    lunch_dishes = Dish.query.filter_by(meal_type='lunch').all()
    dinner_dishes = Dish.query.filter_by(meal_type='dinner').all()
    snack_dishes = Dish.query.filter_by(meal_type='snack').all()
    
    # Generate meal combinations
    breakfast = generate_meal_combination(breakfast_dishes, breakfast_calories, 2, 3)
    lunch = generate_meal_combination(lunch_dishes, lunch_calories, 2, 3)
    dinner = generate_meal_combination(dinner_dishes, dinner_calories, 2, 3)
    snack = generate_meal_combination(snack_dishes, snack_calories, 1, 2)
    
    # Calculate totals
    all_meals = [breakfast, lunch, dinner, snack]
    total_calories = sum(meal['total_calories'] for meal in all_meals if meal)
    
    plan = {
        'breakfast': breakfast,
        'lunch': lunch,
        'dinner': dinner,
        'snack': snack,
        'total_calories': total_calories,
        'target_calories': target_calories
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
        meal_type=data['meal_type']
    )
    db.session.add(dish)
    db.session.commit()
    return jsonify(dish.to_dict()), 201

def init_db():
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
        'meal_type': self.meal_type
    }

Dish.to_dict = dish_to_dict

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 