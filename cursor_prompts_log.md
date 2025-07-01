## Prompt 1 – 2025-06-30

**Prompt:**  
I’m learning to build websites with Python, and I want to create a site that helps people plan their daily meals based on their desired calorie intake. Help me design this website.

**Files Modified:**  
- app.py  
- templates/index.html  
- templates/plan.html  
- static/css/style.css  

**Description of Change:**  
Set up the initial Flask web app structure:
- Created `app.py` to define the Flask server
- Added route `/` to render a homepage with a form for users to input target calorie intake
- Added basic HTML templates for home and meal plan display
- Linked a simple CSS file for basic styling

## Prompt 2 – 2025-06-30

**Prompt:**  
Right now, each meal (breakfast, lunch, dinner, snack) only shows one item. I want to improve this by allowing each meal to include 2–3 dishes. Each dish should have its own calories, protein, carbs, and fat. The total nutritional value of each meal should be shown as the sum of its dishes. Please update the code accordingly.

**Files Modified:**  
- app.py  
- templates/plan.html  
- (possibly data source or helper functions, if any)

**Description of Change:**  
- Updated the meal data structure to support multiple dishes per meal (breakfast, lunch, dinner, snack), each with its own nutritional values  
- Aggregated the total calories, protein, carbs, and fat for each meal from its dishes  
- Modified the HTML layout of `plan.html` to:
  - Display total nutritional values at the top of each meal card  
  - List 2–3 dishes per meal, each showing its own nutrition  
- Updated logic to ensure the top-level daily totals reflect the sum of all dishes across all meals

## Prompt 3 – 2025-06-30

**Prompt:**  
For each meal section (breakfast, lunch, dinner, snack), I want to add a pie chart that shows the calorie distribution across its dishes. Each chart should display the proportion of calories from each dish in that meal.

**Files Modified:**  
- templates/plan.html  
- static/js/app.js  
- static/css/style.css  
- (possibly app.py or the backend if any changes were made to pass dish-level calorie data to the frontend)

**Description of Change:**  
- Added a pie chart to each meal card (breakfast, lunch, dinner, snack) showing the calorie distribution across its individual dishes
- Used Chart.js (or a similar JS charting library) to render the charts in the frontend
- Updated `plan.html` to include canvas elements for each chart
- Enhanced `app.js` to dynamically populate the calorie values for each chart based on the meal data
- Adjusted layout and styles in `style.css` to position the charts cleanly within each card

## Prompt 4 – 2025-06-30

**Prompt:**  
I want to add a "Dietary Preferences" section to the meal planner interface. This section should include checkboxes for the following options:

- Vegetarian  
- Vegan  
- Gluten-Free  
- Low-Carb

These options should be placed near the "Set Your Goals" section. When the user checks one or more boxes and clicks "Generate Meal Plan", the recommended meals should only include dishes that match the selected preferences.

Please update the frontend to show these checkboxes and the backend logic to filter out dishes that do not meet the selected criteria.

**Files Modified:**  
- templates/index.html  
- app.py  
- templates/plan.html  
- (possibly data source: meals or dishes with new dietary tags)  
- static/css/style.css  
- static/js/app.js (if checkbox values are passed via JavaScript)

**Description of Change:**  
- Added a "Dietary Preferences" section with four checkboxes (Vegetarian, Vegan, Gluten-Free, Low-Carb) near the calorie input form  
- Updated form submission logic to send selected preferences to the backend when generating a new meal plan  
- Updated backend filtering logic in `app.py` to exclude dishes that don't match all selected dietary tags  
- Annotated dishes in the database (or internal dish list) with dietary metadata  
- Ensured generated meals for each section (breakfast, lunch, dinner, snack) now respect the user’s selected dietary restrictions  

## Prompt 5 – 2025-06-30

**Prompt:**  
I want to add an "Activity Level" selection to the meal planner interface. Users should be able to choose their level of physical activity from a dropdown menu.

This dropdown should appear below the "Dietary Preferences" section.

Please update both the frontend and backend logic to apply this multiplier to the user's calorie goal when generating the plan.

**Files Modified:**  
- templates/index.html  
- app.py  
- static/css/style.css (if styling was added)

**Description of Change:**  
- Added a dropdown menu labeled "Activity Level" below the "Dietary Preferences" section in the form  
- Provided five options for user selection:
  - Sedentary (×1.2)  
  - Lightly Active (×1.375)  
  - Moderately Active (×1.55)  
  - Very Active (×1.725)  
  - Extra Active (×1.9)
- Updated backend logic in `app.py` to read the selected activity level and apply the corresponding multiplier to the user-entered base calorie target  
- Adjusted the total calorie goal accordingly before generating the meal plan

## Prompt 6 – 2025-06-30

**Prompt:**  
I want to add a fifth meal section called "Afternoon Tea" to my meal planner.

**Files Modified:**  
- templates/plan.html  
- app.py  
- static/js/app.js  
- static/css/style.css (if any adjustments were made)  

**Description of Change:**  
- Added a new meal type called "Afternoon Tea" alongside Breakfast, Lunch, Dinner, and Snack  
- Updated the backend logic to generate and return a fifth meal under the key `afternoon_tea`  
- Adjusted nutrition summary calculations to include data from the fifth meal  
- Rendered the new section in the frontend UI with:
  - Meal title
  - 2–3 dishes
  - Pie chart showing calorie distribution among dishes
  - Total nutrition summary
- Ensured consistent styling and behavior with other meal sections