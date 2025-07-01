# Meal Planner Web App

A personalized meal planning web application built with **Flask**, allowing users to generate daily meal plans tailored to their dietary preferences, calorie goals, and activity level. The app includes full nutrition breakdowns and supports meal saving functionality.

---

## Features

- 🍽️ **Generate Personalized Meal Plans**
  - Set daily calorie targets
  - Choose dietary preferences (vegetarian, vegan, gluten-free, low-carb)
  - Select your **activity level** to adjust calorie needs automatically
  - Meals include: **Breakfast, Lunch, Dinner, Snack**, and the newly added **Afternoon Tea**

- **Nutrition Visualization**
  - Interactive pie charts for each meal showing dish-wise calorie distribution
  - Totals for calories, protein, carbohydrates, and fat per day

- **Saved Plans**
  - Save generated plans for later access
  - View all previously saved plans in the **Saved Plan** section

- **Database-Backed Dishes**
  - Meals are generated based on a recipe database (custom or public datasets like [Kaggle Recipe Interaction Dataset](https://www.kaggle.com/datasets))
  - Easy to update or expand

---

## Tech Stack

- **Backend:** Python, Flask, SQLite
- **Frontend:** HTML, CSS (Bootstrap), JavaScript (Chart.js)
- **Database:** SQLite (can be extended)
- **Development Environment:** VS Code + Cursor

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/meal-planner.git
   cd meal-planner
   
   
##Core Cursor Features Used in This Project
Natural Language Code Generation
Cursor allowed you to write plain English prompts (e.g., “Add an ‘Activity Level’ dropdown and update backend logic accordingly”), and it automatically:

Modified HTML forms and frontend UI

Updated JavaScript event handling

Edited Python Flask backend logic

Multi-file Contextual Editing
Cursor understood the full context across multiple files (e.g., app.py, plan.html, app.js, etc.), allowing it to:

Keep frontend and backend in sync

Generate or update logic consistently across views, routes, and templates

Automated UI Enhancements
Cursor helped add UI components like:

Activity Level dropdowns

New meal cards (e.g., “Afternoon Tea”)

Navigation tabs (e.g., “Saved Plans”)

Schema-aware Backend Updates
When dietary filters or new fields (e.g., vegetarian, vegan, etc.) were added:

Cursor updated the SQLAlchemy Dish model

Rebuilt init_db() to recreate the database with the new schema

Ensured frontend filters and backend query logic were correctly linked

Custom Feature Extension with CSV Data
You instructed Cursor to:

Replace hand-written sample data with real-world data from RAW_recipes.csv

Parse and map nutritional info automatically

Load and insert data programmatically on app start

Prompt-Driven Debugging and Refactoring
When your app encountered errors:

You gave Cursor simple error messages or high-level goals

It traced the issue, rewrote broken parts, and removed redundant logic (e.g., outdated database schema, pie chart rendering bugs)

Human-like Version Control Documentation
Cursor generated readable and consistent update logs for each prompt you gave, including:

Description of changes

Files modified

Intention of each code block
