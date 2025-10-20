"""
Sample recipe data for vector database validation
"""

SAMPLE_RECIPES = [
    {
        "name": "Classic Chocolate Chip Cookies",
        "ingredients": [
            "2 1/4 cups all-purpose flour",
            "1 tsp baking soda",
            "1 tsp salt",
            "1 cup butter, softened",
            "3/4 cup granulated sugar",
            "3/4 cup brown sugar",
            "2 large eggs",
            "2 tsp vanilla extract",
            "2 cups chocolate chips"
        ],
        "instructions": [
            "Preheat oven to 375°F",
            "Mix flour, baking soda, and salt in a bowl",
            "Cream butter and sugars until fluffy",
            "Beat in eggs and vanilla",
            "Gradually add flour mixture",
            "Stir in chocolate chips",
            "Drop rounded tablespoons on ungreased baking sheets",
            "Bake 9-11 minutes until golden brown"
        ],
        "prep_time": "15 minutes",
        "cook_time": "10 minutes",
        "servings": "48 cookies"
    },
    {
        "name": "Beef Stir Fry",
        "ingredients": [
            "1 lb beef sirloin, sliced thin",
            "2 tbsp vegetable oil",
            "1 bell pepper, sliced",
            "1 onion, sliced",
            "2 cloves garlic, minced",
            "1 tbsp fresh ginger, minced",
            "3 tbsp soy sauce",
            "1 tbsp cornstarch",
            "2 tsp sesame oil",
            "Green onions for garnish"
        ],
        "instructions": [
            "Heat oil in a large wok or skillet over high heat",
            "Add beef and stir-fry for 2-3 minutes until browned",
            "Add bell pepper and onion, stir-fry 2 minutes",
            "Add garlic and ginger, stir-fry 30 seconds",
            "Mix soy sauce and cornstarch, add to pan",
            "Stir-fry until sauce thickens",
            "Drizzle with sesame oil and garnish with green onions"
        ],
        "prep_time": "20 minutes",
        "cook_time": "8 minutes",
        "servings": "4"
    },
    {
        "name": "Margherita Pizza",
        "ingredients": [
            "1 pizza dough ball",
            "1/2 cup pizza sauce",
            "8 oz fresh mozzarella, sliced",
            "1/4 cup fresh basil leaves",
            "2 tbsp olive oil",
            "Salt and pepper to taste",
            "Flour for dusting"
        ],
        "instructions": [
            "Preheat oven to 475°F with pizza stone if available",
            "Roll out dough on floured surface",
            "Spread sauce evenly, leaving border for crust",
            "Add mozzarella slices",
            "Drizzle with olive oil",
            "Season with salt and pepper",
            "Bake 12-15 minutes until crust is golden",
            "Top with fresh basil before serving"
        ],
        "prep_time": "30 minutes",
        "cook_time": "15 minutes",
        "servings": "2-3"
    },
    {
        "name": "Chicken Caesar Salad",
        "ingredients": [
            "2 chicken breasts",
            "1 head romaine lettuce, chopped",
            "1/2 cup Caesar dressing",
            "1/4 cup parmesan cheese, grated",
            "1 cup croutons",
            "2 tbsp olive oil",
            "Salt and pepper to taste",
            "1 lemon, juiced"
        ],
        "instructions": [
            "Season chicken with salt, pepper, and olive oil",
            "Grill chicken 6-7 minutes per side until cooked through",
            "Let chicken rest, then slice",
            "Toss romaine with Caesar dressing",
            "Top with sliced chicken, parmesan, and croutons",
            "Squeeze lemon juice over salad",
            "Serve immediately"
        ],
        "prep_time": "15 minutes",
        "cook_time": "15 minutes",
        "servings": "2"
    },
    {
        "name": "Banana Bread",
        "ingredients": [
            "3 ripe bananas, mashed",
            "1/3 cup melted butter",
            "3/4 cup sugar",
            "1 egg, beaten",
            "1 tsp vanilla extract",
            "1 tsp baking soda",
            "Pinch of salt",
            "1 1/2 cups all-purpose flour",
            "Optional: 1/2 cup chopped walnuts"
        ],
        "instructions": [
            "Preheat oven to 350°F",
            "Grease a 4x8 inch loaf pan",
            "Mix melted butter and mashed bananas",
            "Stir in sugar, egg, and vanilla",
            "Sprinkle baking soda and salt over mixture and mix",
            "Add flour and mix until just combined",
            "Fold in nuts if using",
            "Pour into prepared pan",
            "Bake 60-65 minutes until toothpick comes out clean"
        ],
        "prep_time": "15 minutes",
        "cook_time": "65 minutes",
        "servings": "8 slices"
    }
]

def get_random_recipe():
    """Get a random recipe from the sample recipes"""
    import random
    return random.choice(SAMPLE_RECIPES)

def format_recipe_for_summary(recipe):
    """Format recipe data for LLM summarization"""
    ingredients_text = ", ".join(recipe["ingredients"])
    instructions_text = ". ".join(recipe["instructions"])
    
    return f"""
Recipe: {recipe["name"]}

Ingredients: {ingredients_text}

Instructions: {instructions_text}

Prep Time: {recipe["prep_time"]}
Cook Time: {recipe["cook_time"]}
Servings: {recipe["servings"]}
"""