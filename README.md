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
