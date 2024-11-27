from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import json  # Import to parse JSON output

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_recipe(ingredients, recipe_type, allergies, max_time):
    prompt = f"""
    Generate a {recipe_type} recipe using these ingredients: {', '.join(ingredients)}.
    Exclude ingredients with these allergens: {', '.join(allergies)}.
    The total cooking time should not exceed {max_time} minutes.

    **Important:** The recipe should exactly follow this JSON structure, and **only include two recipes** enclosed in square brackets:

    [
        {{
            "title": "Recipe Title",
            "ingredients": [
                {{"name": "Ingredient 1", "quantity": "amount", "unit": "unit"}},
                {{"name": "Ingredient 2", "quantity": "amount", "unit": "unit"}}
            ],
            "instructions": [
                "Instruction. (try to add how long to do this action for)",
                "Instruction. (try to add how long to do this action for)",
                "Instruction. (try to add how long to do this action for)",
                (add more instructions if needed but do not exceed 6)
            ],
            "cooking_time": "Time in minutes",
            "servings": "Servings",
            "healthyMeter": "A score from 1 (least healthy) to 5 (most healthy) based on the ingredients and cooking method",
            "Kcal": "Calories per serving"
        }}
    ]

    Please **output exactly two recipes in this format, without any additional text**. Only the JSON recipe output.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.3
    )
    
    # Parse the output as JSON
    recipe_json = response['choices'][0]['message']['content'].strip()
    try:
        # Convert the response to JSON format to ensure it’s correctly structured
        recipe_data = json.loads(recipe_json)
        return recipe_data
    except json.JSONDecodeError:
        print("JSON parsing error.")
        return []

@app.route('/generate-recipe', methods=['POST'])
def recipe():
    data = request.json
    ingredients = data.get('ingredients', ["tomato", "cheese", "bread"])
    recipe_type = data.get('recipeType', "any")
    allergies = data.get('allergies', [])
    max_time = data.get('maxTime', 30)
    
    recipe = generate_recipe(ingredients, recipe_type, allergies, max_time)
    return jsonify({'recipes': recipe})

if __name__ == '__main__':
    app.run(debug=True)
