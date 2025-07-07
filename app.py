# Flask Meal Planning Application
# This application helps users generate personalized meal plans based on calorie targets and dietary preferences

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import os
from sqlalchemy.types import JSON as SQLAlchemyJSON
import json

# Initialize Flask application
app = Flask(__name__)

# Database configuration - using SQLite for simplicity
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class Dish(db.Model):
    """
    Represents a single food dish with nutritional information and dietary attributes.
    Each dish belongs to a specific meal type (breakfast, lunch, dinner, snack, afternoon_tea).
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name of the dish
    calories = db.Column(db.Integer, nullable=False)   # Calories per serving
    protein = db.Column(db.Float, nullable=False)      # Protein in grams
    carbs = db.Column(db.Float, nullable=False)        # Carbohydrates in grams
    fat = db.Column(db.Float, nullable=False)          # Fat in grams
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack, afternoon_tea
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When dish was added
    
    # Dietary restriction flags
    vegetarian = db.Column(db.Boolean, default=False)  # Suitable for vegetarians
    vegan = db.Column(db.Boolean, default=False)       # Suitable for vegans
    gluten_free = db.Column(db.Boolean, default=False) # Gluten-free option
    low_carb = db.Column(db.Boolean, default=False)    # Low carbohydrate option

class MealPlan(db.Model):
    """
    Represents a complete meal plan for a specific date with target calories.
    Stores dish IDs as JSON strings for each meal type.
    """
    id = db.Column(db.Integer, primary_key=True)
    target_calories = db.Column(db.Integer, nullable=False)  # Daily calorie target
    date = db.Column(db.Date, nullable=False)                # Date for the meal plan
    breakfast_dishes = db.Column(db.String(500))  # JSON string of dish IDs for breakfast
    lunch_dishes = db.Column(db.String(500))      # JSON string of dish IDs for lunch
    dinner_dishes = db.Column(db.String(500))     # JSON string of dish IDs for dinner
    snack_dishes = db.Column(db.String(500))      # JSON string of dish IDs for snacks
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SavedPlan(db.Model):
    """
    Stores saved meal plans with calculated nutritional totals.
    Used for the saved plans feature where users can view their history.
    """
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # When plan was saved
    total_calories = db.Column(db.Integer, nullable=False)       # Total calories in the plan
    total_protein = db.Column(db.Float, nullable=False)          # Total protein in grams
    total_carbs = db.Column(db.Float, nullable=False)            # Total carbs in grams
    total_fat = db.Column(db.Float, nullable=False)              # Total fat in grams
    plan_data = db.Column(db.Text, nullable=False)               # Complete plan as JSON string

# ============================================================================
# SAMPLE DATA - Pre-populated dishes for demonstration
# ============================================================================

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

# ============================================================================
# ROUTES - Web pages
# ============================================================================

@app.route('/')
def index():
    """Home page - displays the main landing page for the meal planning app."""
    return render_template('index.html')

@app.route('/plan', methods=['GET'])
def plan():
    """Meal plan generation page - where users can create new meal plans."""
    return render_template('plan.html')

@app.route('/meals')
def meals():
    """Meals management page - displays all available dishes and allows adding new ones."""
    dishes = Dish.query.all()  # Get all dishes from database
    return render_template('meals.html', dishes=dishes)

@app.route('/saved')
def saved():
    """Saved plans page - shows history of previously saved meal plans."""
    plans = SavedPlan.query.order_by(SavedPlan.timestamp.desc()).all()  # Most recent first
    return render_template('saved.html', plans=plans)


# ============================================================================
# API ENDPOINTS - Backend functionality
# ============================================================================
@app.route('/api/generate_plan', methods=['POST'])
def generate_plan():
    """
    Core meal plan generation endpoint.
    
    Receives:
    - target_calories: Daily calorie target
    - preferences: List of dietary preferences (vegetarian, vegan, gluten_free, low_carb)
    - selected_meals: Which meals to include (breakfast, lunch, dinner, snack, afternoon_tea)
    
    Returns:
    - Complete meal plan with dishes for each selected meal type
    - Nutritional totals for the entire day
    """
    data = request.get_json()
    target_calories = int(data.get('target_calories', 2000))
    preferences = data.get('preferences', [])
    selected_meals = data.get('selected_meals', ['breakfast', 'lunch', 'dinner', 'snack', 'afternoon_tea'])
    
    # Calculate calorie distribution across meals
    # Default distribution percentages for each meal type
    meal_distribution = {
        'breakfast': 0.35,    # 35% of daily calories
        'lunch': 0.25,        # 25% of daily calories
        'dinner': 0.2,        # 20% of daily calories
        'afternoon_tea': 0.1, # 10% of daily calories
        'snack': 0.1          # 10% of daily calories
    }
    
    # Adjust distribution based on selected meals
    adjusted_calories = target_calories
    total_percentage = sum(meal_distribution[meal] for meal in selected_meals)
    meal_calories = {}
    
    # Calculate calories for each selected meal
    for meal in selected_meals:
        meal_calories[meal] = int(adjusted_calories * meal_distribution[meal] / total_percentage)
    
    # Filter dishes by preferences for each meal type
    meal_dishes = {}
    for meal in selected_meals:
        meal_dishes[meal] = filter_dishes_by_preferences(Dish.query.filter_by(meal_type=meal).all(), preferences)
    
    # Generate meal combinations for each selected meal
    generated_meals = {}
    for meal in selected_meals:
        # Set minimum and maximum dishes per meal type
        min_dishes = 2 if meal in ['breakfast', 'lunch', 'dinner'] else 1
        max_dishes = 3 if meal in ['breakfast', 'lunch', 'dinner'] else 2
        generated_meals[meal] = generate_meal_combination(meal_dishes[meal], meal_calories[meal], min_dishes, max_dishes)
    
    # Calculate total calories from generated meals
    total_calories = sum(meal['total_calories'] for meal in generated_meals.values() if meal)
    
    # Calorie adjustment logic - if total is off by more than 10%, adjust the largest meal
    if abs(total_calories - adjusted_calories) > 0.1 * adjusted_calories:
        # Find the meal with the highest calories
        largest_meal = max((m for m in generated_meals.values() if m), key=lambda m: m['total_calories'])
        # Find the dish with the highest calories in that meal
        largest_dish = max(largest_meal['dishes'], key=lambda d: d['calories'])
        
        # Calculate needed adjustment
        diff = adjusted_calories - total_calories
        # Scale the dish (limit scaling between 0.5x and 1.5x to keep portions reasonable)
        scale = max(0.5, min(1.5, (largest_dish['calories'] + diff) / largest_dish['calories']))
        
        # Apply scaling to all nutritional values
        largest_dish['calories'] *= scale
        largest_dish['protein'] *= scale
        largest_dish['carbs'] *= scale
        largest_dish['fat'] *= scale
        
        # Add scaling indicator to dish name if significantly scaled
        if 'name' in largest_dish:
            largest_dish['name'] += f" (x{scale:.2f})"
        
        # Recalculate meal totals
        largest_meal['total_calories'] = sum(d['calories'] for d in largest_meal['dishes'])
        largest_meal['total_protein'] = sum(d['protein'] for d in largest_meal['dishes'])
        largest_meal['total_carbs'] = sum(d['carbs'] for d in largest_meal['dishes'])
        largest_meal['total_fat'] = sum(d['fat'] for d in largest_meal['dishes'])
        
        # Recalculate total calories
        total_calories = sum(meal['total_calories'] for meal in generated_meals.values() if meal)
    
    # Prepare final plan response
    plan = {
        'total_calories': total_calories,
        'target_calories': adjusted_calories
    }
    
    # Add each meal to the plan
    for meal in selected_meals:
        plan[meal] = generated_meals[meal]
    
    return jsonify(plan)

def generate_meal_combination(dishes, target_calories, min_dishes=2, max_dishes=3):
    """
    Generates an optimal combination of dishes for a specific meal.
    
    Algorithm:
    1. Try different numbers of dishes (min_dishes to max_dishes)
    2. For each dish count, try multiple random combinations
    3. If needed, scale one dish to better match target calories
    4. Return the combination that best matches the target
    
    Args:
        dishes: List of available dishes for this meal type
        target_calories: Target calories for this meal
        min_dishes: Minimum number of dishes to include
        max_dishes: Maximum number of dishes to include
    
    Returns:
        Dictionary with dishes, total calories, and macronutrient totals
    """
    if not dishes:
        return None
    
    best_combination = None
    best_difference = float('inf')
    best_scaled = None
    
    # Try different combinations of dishes
    for num_dishes in range(min_dishes, min(max_dishes + 1, len(dishes) + 1)):
        for _ in range(20):  # Try 20 random combinations for better fit
            selected_dishes = random.sample(dishes, num_dishes)
            total_calories = sum(dish.calories for dish in selected_dishes)
            difference = abs(total_calories - target_calories)
            
            # Try scaling the last dish if we have multiple dishes and need adjustment
            if difference > 0 and num_dishes > 1:
                # Calculate calories from all dishes except the last one
                base_calories = sum(dish.calories for dish in selected_dishes[:-1])
                remaining = target_calories - base_calories
                last_dish = selected_dishes[-1]
                
                if last_dish.calories > 0:
                    # Scale the last dish to fill the remaining calories
                    # Limit scaling between 0.5x and 1.5x for reasonable portions
                    scale = max(0.5, min(1.5, remaining / last_dish.calories))
                    
                    # Calculate scaled nutritional values
                    scaled_calories = last_dish.calories * scale
                    scaled_protein = last_dish.protein * scale
                    scaled_carbs = last_dish.carbs * scale
                    scaled_fat = last_dish.fat * scale
                    total_scaled = base_calories + scaled_calories
                    scaled_difference = abs(total_scaled - target_calories)
                    
                    # Update best scaled combination if this is better
                    if scaled_difference < best_difference:
                        best_difference = scaled_difference
                        best_scaled = [
                            *selected_dishes[:-1],  # All dishes except the last
                            {
                                'id': last_dish.id,
                                'name': last_dish.name + (f" (x{scale:.2f})" if abs(scale-1)>0.01 else ""),
                                'calories': scaled_calories,
                                'protein': scaled_protein,
                                'carbs': scaled_carbs,
                                'fat': scaled_fat,
                                'meal_type': last_dish.meal_type,
                                'vegetarian': last_dish.vegetarian,
                                'vegan': last_dish.vegan,
                                'gluten_free': last_dish.gluten_free,
                                'low_carb': last_dish.low_carb
                            }
                        ]
            
            # Update best combination if this unmodified combination is better
            if difference < best_difference:
                best_difference = difference
                best_combination = selected_dishes
    
    # Return the best scaled combination if available
    if best_scaled:
        dishes_out = best_scaled
        total_calories = sum(d['calories'] if isinstance(d, dict) else d.calories for d in dishes_out)
        total_protein = sum(d['protein'] if isinstance(d, dict) else d.protein for d in dishes_out)
        total_carbs = sum(d['carbs'] if isinstance(d, dict) else d.carbs for d in dishes_out)
        total_fat = sum(d['fat'] if isinstance(d, dict) else d.fat for d in dishes_out)
        
        return {
            'dishes': [d if isinstance(d, dict) else d.to_dict() for d in dishes_out],
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat
        }
    
    # Return the best unmodified combination if no scaling was done
    if not best_combination:
        return None
    
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
    """
    Filters dishes based on dietary preferences.
    
    Args:
        dishes: List of dishes to filter
        preferences: List of dietary preferences (vegetarian, vegan, gluten_free, low_carb)
    
    Returns:
        Filtered list of dishes that match all specified preferences
    """
    if not preferences:
        return dishes  # Return all dishes if no preferences specified
    
    filtered = []
    for dish in dishes:
        # Skip dish if it doesn't match any of the specified preferences
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
    """
    API endpoint to retrieve dishes.
    
    Query parameters:
    - type: Optional meal type filter (breakfast, lunch, dinner, snack, afternoon_tea)
    
    Returns:
    - List of dishes (filtered by type if specified)
    """
    meal_type = request.args.get('type')
    if meal_type:
        dishes = Dish.query.filter_by(meal_type=meal_type).all()
    else:
        dishes = Dish.query.all()
    
    return jsonify([dish.to_dict() for dish in dishes])

@app.route('/api/dishes', methods=['POST'])
def add_dish():
    """
    API endpoint to add a new dish to the database.
    
    Expected JSON data:
    - name: Dish name
    - calories: Calories per serving
    - protein: Protein in grams
    - carbs: Carbohydrates in grams
    - fat: Fat in grams
    - meal_type: Type of meal (breakfast, lunch, dinner, snack, afternoon_tea)
    - vegetarian, vegan, gluten_free, low_carb: Boolean dietary flags
    
    Returns:
    - Created dish data with 201 status code
    """
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

@app.route('/api/save_plan', methods=['POST'])
def save_plan():
    """
    API endpoint to save a generated meal plan.
    
    Expected JSON data:
    - plan: Complete meal plan object with all meals and nutritional data
    
    Returns:
    - Success confirmation with saved plan ID
    """
    data = request.get_json()
    plan = data.get('plan')
    
    if not plan:
        return jsonify({'error': 'No plan data provided'}), 400
    
    # Calculate total nutritional values across all meals
    total_calories = plan.get('total_calories', 0)
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    
    # Sum up macronutrients from all meals
    for meal_key in ['breakfast', 'lunch', 'dinner', 'snack', 'afternoon_tea']:
        meal = plan.get(meal_key)
        if meal:
            total_protein += meal.get('total_protein', 0)
            total_carbs += meal.get('total_carbs', 0)
            total_fat += meal.get('total_fat', 0)
    
    # Create and save the plan
    saved = SavedPlan(
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        plan_data=json.dumps(plan)  # Store complete plan as JSON string
    )
    db.session.add(saved)
    db.session.commit()
    
    return jsonify({'success': True, 'id': saved.id})

@app.route('/api/delete_plan/<int:plan_id>', methods=['POST'])
def delete_plan(plan_id):
    """
    API endpoint to delete a saved meal plan.
    
    Args:
        plan_id: ID of the plan to delete
    
    Returns:
        Success confirmation or 404 if plan not found
    """
    plan = SavedPlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Plan not found'}), 404
    
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'success': True})

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """
    Initialize the database and populate with sample data.
    
    This function:
    1. Removes existing database file (if any)
    2. Creates all database tables
    3. Populates with sample dishes if database is empty
    """
    db_path = 'meals.db'
    if os.path.exists(db_path):
        os.remove(db_path)  # Remove existing database for fresh start
    
    with app.app_context():
        db.create_all()  # Create all database tables
        
        # Add sample dishes if database is empty
        if Dish.query.count() == 0:
            for dish_data in SAMPLE_DISHES:
                dish = Dish(**dish_data)
                db.session.add(dish)
            db.session.commit()

# ============================================================================
# MODEL METHODS
# ============================================================================

def dish_to_dict(self):
    """
    Convert a Dish model instance to a dictionary for JSON serialization.
    
    Returns:
        Dictionary representation of the dish with all attributes
    """
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

# Attach the to_dict method to the Dish model
Dish.to_dict = dish_to_dict

# ============================================================================
# ERROR HANDLING
# ============================================================================

@app.errorhandler(403)
def forbidden(e):
    """Handle 403 Forbidden errors with a user-friendly message."""
    return render_template('error.html', message='403 Forbidden: You do not have permission to access this page.'), 403

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    init_db()  # Initialize database with sample data
    app.run(debug=True)  # Start Flask development server 