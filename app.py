from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Meal(db.Model):
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
    breakfast_id = db.Column(db.Integer, db.ForeignKey('meal.id'))
    lunch_id = db.Column(db.Integer, db.ForeignKey('meal.id'))
    dinner_id = db.Column(db.Integer, db.ForeignKey('meal.id'))
    snack_id = db.Column(db.Integer, db.ForeignKey('meal.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Sample meal data
SAMPLE_MEALS = [
    # Breakfast options
    {"name": "Oatmeal with Berries", "calories": 300, "protein": 12, "carbs": 45, "fat": 8, "meal_type": "breakfast"},
    {"name": "Greek Yogurt with Honey", "calories": 250, "protein": 20, "carbs": 25, "fat": 5, "meal_type": "breakfast"},
    {"name": "Scrambled Eggs with Toast", "calories": 350, "protein": 18, "carbs": 30, "fat": 15, "meal_type": "breakfast"},
    {"name": "Smoothie Bowl", "calories": 280, "protein": 15, "carbs": 40, "fat": 6, "meal_type": "breakfast"},
    
    # Lunch options
    {"name": "Grilled Chicken Salad", "calories": 400, "protein": 35, "carbs": 15, "fat": 20, "meal_type": "lunch"},
    {"name": "Quinoa Bowl", "calories": 450, "protein": 18, "carbs": 60, "fat": 12, "meal_type": "lunch"},
    {"name": "Turkey Sandwich", "calories": 380, "protein": 25, "carbs": 45, "fat": 12, "meal_type": "lunch"},
    {"name": "Vegetable Soup", "calories": 200, "protein": 8, "carbs": 25, "fat": 8, "meal_type": "lunch"},
    
    # Dinner options
    {"name": "Salmon with Vegetables", "calories": 500, "protein": 40, "carbs": 20, "fat": 25, "meal_type": "dinner"},
    {"name": "Beef Stir Fry", "calories": 450, "protein": 30, "carbs": 35, "fat": 20, "meal_type": "dinner"},
    {"name": "Pasta with Tomato Sauce", "calories": 400, "protein": 12, "carbs": 60, "fat": 10, "meal_type": "dinner"},
    {"name": "Vegetarian Curry", "calories": 350, "protein": 15, "carbs": 45, "fat": 12, "meal_type": "dinner"},
    
    # Snack options
    {"name": "Apple with Peanut Butter", "calories": 200, "protein": 6, "carbs": 25, "fat": 10, "meal_type": "snack"},
    {"name": "Mixed Nuts", "calories": 180, "protein": 6, "carbs": 8, "fat": 16, "meal_type": "snack"},
    {"name": "Carrot Sticks with Hummus", "calories": 150, "protein": 5, "carbs": 20, "fat": 6, "meal_type": "snack"},
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
    meals = Meal.query.all()
    return render_template('meals.html', meals=meals)

@app.route('/api/generate_plan', methods=['POST'])
def generate_plan():
    data = request.get_json()
    target_calories = int(data.get('target_calories', 2000))
    
    # Calculate meal distribution (40% breakfast, 30% lunch, 25% dinner, 5% snack)
    breakfast_calories = int(target_calories * 0.4)
    lunch_calories = int(target_calories * 0.3)
    dinner_calories = int(target_calories * 0.25)
    snack_calories = int(target_calories * 0.05)
    
    # Select meals for each type
    breakfast_meals = Meal.query.filter_by(meal_type='breakfast').all()
    lunch_meals = Meal.query.filter_by(meal_type='lunch').all()
    dinner_meals = Meal.query.filter_by(meal_type='dinner').all()
    snack_meals = Meal.query.filter_by(meal_type='snack').all()
    
    # Find meals closest to target calories for each meal type
    def find_best_meal(meals, target_cals):
        if not meals:
            return None
        return min(meals, key=lambda x: abs(x.calories - target_cals))
    
    breakfast = find_best_meal(breakfast_meals, breakfast_calories)
    lunch = find_best_meal(lunch_meals, lunch_calories)
    dinner = find_best_meal(dinner_meals, dinner_calories)
    snack = find_best_meal(snack_meals, snack_calories)
    
    plan = {
        'breakfast': breakfast.to_dict() if breakfast else None,
        'lunch': lunch.to_dict() if lunch else None,
        'dinner': dinner.to_dict() if dinner else None,
        'snack': snack.to_dict() if snack else None,
        'total_calories': sum([m.calories for m in [breakfast, lunch, dinner, snack] if m]),
        'target_calories': target_calories
    }
    
    return jsonify(plan)

@app.route('/api/meals', methods=['GET'])
def get_meals():
    meal_type = request.args.get('type')
    if meal_type:
        meals = Meal.query.filter_by(meal_type=meal_type).all()
    else:
        meals = Meal.query.all()
    
    return jsonify([meal.to_dict() for meal in meals])

@app.route('/api/meals', methods=['POST'])
def add_meal():
    data = request.get_json()
    meal = Meal(
        name=data['name'],
        calories=int(data['calories']),
        protein=float(data['protein']),
        carbs=float(data['carbs']),
        fat=float(data['fat']),
        meal_type=data['meal_type']
    )
    db.session.add(meal)
    db.session.commit()
    return jsonify(meal.to_dict()), 201

def init_db():
    with app.app_context():
        db.create_all()
        
        # Add sample meals if database is empty
        if Meal.query.count() == 0:
            for meal_data in SAMPLE_MEALS:
                meal = Meal(**meal_data)
                db.session.add(meal)
            db.session.commit()

# Add to_dict method to Meal model
def meal_to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'calories': self.calories,
        'protein': self.protein,
        'carbs': self.carbs,
        'fat': self.fat,
        'meal_type': self.meal_type
    }

Meal.to_dict = meal_to_dict

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 