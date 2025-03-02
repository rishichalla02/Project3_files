import streamlit as st
import numpy as np
import pandas as pd
import time
import base64
from io import BytesIO
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from fpdf import FPDF
import warnings

warnings.filterwarnings('ignore')

# Custom Styling for Navigation Bar and Background
st.markdown(
    """
    <style>
        body {
            background-color: #f0f2f6;
        }

        .nav-bar {
            display: flex;
            justify-content: space-around;
            background-color: darkblue;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .nav-bar a {
            color: white;
            text-decoration: none;
            font-size: 18px;
            transition: all 0.3s ease;
            padding: 10px 15px;
            position: relative;
            overflow: hidden;
        }
        .nav-bar a:hover {
            background-color: rgb(255, 75, 75);
            border-radius: 5px;
            transform: translateY(-3px);
        }
        .nav-bar a::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 0;
            height: 2px;
            background-color: white;
            transition: width 0.3s ease;
        }
        .nav-bar a:hover::after {
            width: 100%;
        }

        /* Sidebar styling */
       .st-emotion-cache-6qob1r {
            background-color: darkblue;
            color: black;
       }

       .st-emotion-cache-1espb9k h2 {
            color: white;
        }

       .st-emotion-cache-6qob1r p {
            color: white;
        }

       .st-emotion-cache-hpex6h {
            color: white;
        }
        
        
        /* Circular progress styling */
        .circular-progress {
            display: inline-block;
            position: relative;
            width: 120px;
            height: 120px;
            margin: 10px;
            text-align: center;
        }
        .circular-progress svg {
            transform: rotate(-90deg);
        }
        .circular-progress .circle-bg {
            fill: none;
            stroke: #e0e0e0;
            stroke-width: 3.8;
        }
        .circular-progress .circle {
            fill: none;
            stroke-width: 3.8;
            stroke-linecap: round;
            transition: stroke-dashoffset 0.5s ease;
        }
        .circular-progress .percentage {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 16px;
            font-weight: bold;
        }
        .circular-progress .label {
            position: absolute;
            bottom: -25px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 14px;
        }
        
        /* Cursor pointer for selectbox */
        .stSelectbox:hover {
            cursor: pointer !important;
        }
        div[data-baseweb="select"] {
            cursor: pointer !important;
        }

        .st-e0, .st-ec, .st-bq, .st-ed, .st-ee {
        cursor: pointer !important;
        }
        
        /* Animation for navigation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .nav-bar a {
            animation: fadeIn 0.5s ease forwards;
            opacity: 0;
        }
        .nav-bar a:nth-child(1) { animation-delay: 0.1s; }
        .nav-bar a:nth-child(2) { animation-delay: 0.2s; }
        .nav-bar a:nth-child(3) { animation-delay: 0.3s; }
        .nav-bar a:nth-child(4) { animation-delay: 0.4s; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Horizontal Navigation Bar
st.markdown(
    """
    <div class='nav-bar'>
        <a href='#home'>Home</a>
        <a href='#about'>About</a>
        <a href='#download-chart'>Download Chart</a>
        <a href='#help'>Help</a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("## Personal Fitness Tracker - SmartFit AI")
st.write("Predict your calorie burn and get personalized fitness recommendations!")

st.sidebar.header("User Input Parameters:")

def user_input_features():
    age = st.sidebar.slider("Age:", 10, 100, 30)
    height = st.sidebar.number_input("Height (cm):", 100, 250, 170)
    weight = st.sidebar.number_input("Weight (kg):", 30, 200, 70)
    bmi = round(weight / ((height / 100) ** 2), 2)
    duration = st.sidebar.slider("Duration (min):", 0, 60, 30)
    heart_rate = st.sidebar.slider("Heart Rate:", 50, 150, 80)
    body_temp = st.sidebar.slider("Body Temperature (C):", 36, 52, 38)
    gender_button = st.sidebar.radio("Gender:", ("Male", "Female"))
    goal = st.sidebar.selectbox("Fitness Goal:", ["Weight Loss", "Muscle Gain", "Maintenance"])

     # NEW FEATURE: Routine Adherence Slider
    adherence = st.sidebar.slider("Expected Routine Adherence (days per week):", 1, 7, 4, 
                                 help="How many days per week do you expect to follow this fitness routine?")

    gender = 1 if gender_button == "Male" else 0
    data_model = {"Age": age,"Height": height, "Weight": weight, "BMI": bmi, "Duration": duration, "Heart_Rate": heart_rate, "Body_Temp": body_temp, "Gender_male": gender}
    return pd.DataFrame(data_model, index=[0]), goal, adherence

df, goal_value, adherence_days = user_input_features()


st.write("---")
st.header("Your Parameters:")

# Creating circular progress bars for each parameter
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

# Function to create circular progress HTML
def create_circular_progress(value, max_value, label, color):
    percentage = min(100, int((value / max_value) * 100))
    return f"""
    <div class="circular-progress">
        <svg width="120" height="120" viewBox="0 0 120 120">
            <circle class="circle-bg" cx="60" cy="60" r="54"></circle>
            <circle class="circle" cx="60" cy="60" r="54" 
                stroke="{color}"
                stroke-dasharray="339.292"
                stroke-dashoffset="{339.292 - (339.292 * percentage) / 100}">
            </circle>
        </svg>
        <div class="percentage">{value}</div>
        <div class="label">{label}</div>
    </div>
    """

with col1:
    st.markdown(create_circular_progress(df["Age"].values[0], 100, "Age", "#FF9800"), unsafe_allow_html=True)

with col2:
    st.markdown(create_circular_progress(df["BMI"].values[0], 40, "BMI", "#4CAF50"), unsafe_allow_html=True)

with col3:
    st.markdown(create_circular_progress(df["Duration"].values[0], 60, "Duration (min)", "#2196F3"), unsafe_allow_html=True)

with col4:
    st.markdown(create_circular_progress(df["Heart_Rate"].values[0], 150, "Heart Rate", "#F44336"), unsafe_allow_html=True)

with col5:
    st.markdown(create_circular_progress(df["Body_Temp"].values[0], 42, "Body Temp (°C)", "#9C27B0"), unsafe_allow_html=True)

with col6:
    gender_val = "Male" if df["Gender_male"].values[0] == 1 else "Female"
    st.markdown(f"""
    <div style="text-align: center; margin-top: 20px;">
        <div style="font-size: 18px; font-weight: bold;">Gender</div>
        <div style="font-size: 24px; margin-top: 10px; color: #3F51B5;">{gender_val}</div>
    </div>
    """, unsafe_allow_html=True)

# Add cursor pointer for fitness goal
st.markdown("""
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const selectboxes = document.querySelectorAll('div[data-baseweb="select"]');
        selectboxes.forEach(box => {
            box.style.cursor = 'pointer';
        });
    });
</script>
""", unsafe_allow_html=True)

# Load data
calories = pd.read_excel("calories.xlsx")
exercise = pd.read_excel("exercise.xlsx")
exercise_df = exercise.merge(calories, on="User_ID").drop(columns="User_ID")
exercise_df["BMI"] = round(exercise_df["Weight"] / ((exercise_df["Height"] / 100) ** 2), 2)

exercise_train_data, exercise_test_data = train_test_split(exercise_df, test_size=0.2, random_state=1)
X_train = pd.get_dummies(exercise_train_data.drop("Calories", axis=1), drop_first=True)
y_train = exercise_train_data["Calories"]
random_reg = RandomForestRegressor(n_estimators=1000, max_features=3, max_depth=6)
random_reg.fit(X_train, y_train)
df = df.reindex(columns=X_train.columns, fill_value=0)
prediction = random_reg.predict(df)

st.write("---")
st.header("Calorie Prediction:")
st.write(f"### {round(prediction[0], 2)} kilocalories")

# NEW FEATURE: Walking distance calculation
st.write("---")
st.header("Walking Distance to Burn Calories")

# Calculate walking distance needed to burn calories
# Average person burns approximately 65 calories per kilometer walked
calories_per_km = 65
# Calculate based on predicted calories and user's BMI
# Heavier people burn more calories walking, so adjust based on BMI
bmi_factor = df['BMI'].values[0] / 25  # Normalize against BMI of 25
adjusted_calories_per_km = calories_per_km * bmi_factor

# Calculate kilometers needed
kilometers_needed = round(prediction[0] / adjusted_calories_per_km, 2)

# Display walking distance with some helpful context
st.write(f"### {kilometers_needed} kilometers")
st.write(f"You would need to walk approximately {kilometers_needed} kilometers to burn {round(prediction[0], 2)} calories.")

# Add some helpful tips based on the walking distance
if kilometers_needed < 5:
    st.info("💡 Tip: This is a manageable walking distance for most people. Try breaking it into smaller walks throughout the day!")
elif kilometers_needed < 10:
    st.info("💡 Tip: This is a moderate walking distance. Consider walking part of your commute or taking longer walks on weekends.")
else:
    st.info("💡 Tip: This is a substantial distance. For more effective calorie burning, you might want to combine walking with other exercises.")

# Recommendations
st.write("---")
st.header("Dietary & Fitness Recommendations")
if goal_value == "Weight Loss":
    st.write("### Suggested Diet: High-protein, low-carb meals")
elif goal_value == "Muscle Gain":
    st.write("### Suggested Diet: High-calorie, protein-rich meals")
else:
    st.write("### Suggested Diet: Balanced nutrition")

# NEW FEATURE: Specific Food Suggestions based on fitness goal
st.write("---")
st.header("Recommended Foods for Your Goal")

# Define food suggestions for each goal
weight_loss_foods = {
    "Proteins": ["Chicken breast", "Turkey", "Egg whites", "Greek yogurt", "Tofu", "White fish", "Cottage cheese"],
    "Carbs": ["Quinoa", "Brown rice", "Sweet potatoes", "Oats", "Beans", "Lentils"],
    "Fats": ["Avocado", "Olive oil", "Nuts (in moderation)", "Chia seeds", "Flaxseeds"],
    "Vegetables": ["Leafy greens", "Broccoli", "Cauliflower", "Bell peppers", "Cucumber", "Asparagus", "Zucchini"],
    "Fruits": ["Berries", "Grapefruit", "Apples", "Watermelon"]
}

muscle_gain_foods = {
    "Proteins": ["Chicken breast", "Steak", "Salmon", "Eggs", "Greek yogurt", "Whey protein", "Tuna", "Lean ground beef"],
    "Carbs": ["Brown rice", "Quinoa", "Sweet potatoes", "Oats", "Whole grain pasta", "Bananas"],
    "Fats": ["Avocado", "Nuts and nut butters", "Olive oil", "Coconut oil", "Full-fat dairy", "Fatty fish"],
    "Vegetables": ["Spinach", "Broccoli", "Mixed vegetables", "Kale", "Sweet potatoes"],
    "Fruits": ["Bananas", "Apples", "Berries", "Dried fruits"]
}

maintenance_foods = {
    "Proteins": ["Chicken", "Fish", "Eggs", "Greek yogurt", "Beans", "Lentils", "Tofu"],
    "Carbs": ["Brown rice", "Whole grain bread", "Quinoa", "Oats", "Potatoes"],
    "Fats": ["Avocado", "Olive oil", "Nuts", "Seeds", "Fatty fish"],
    "Vegetables": ["Leafy greens", "Broccoli", "Carrots", "Bell peppers", "Tomatoes", "Cucumber"],
    "Fruits": ["Apples", "Bananas", "Berries", "Oranges", "Pears"]
}

# Display appropriate food recommendations based on user's goal
if goal_value == "Weight Loss":
    food_recommendations = weight_loss_foods
    bmi_value = df['BMI'].values[0]
    
    st.write("### Foods to Help You Reach Your Weight Loss Goal")
    st.write("Focus on high-protein, nutrient-dense foods with plenty of fiber to keep you feeling full.")
    
    # Additional advice based on BMI
    if bmi_value > 30:
        st.info("📌 Your BMI suggests focusing on a calorie deficit of 500-750 calories per day for healthy weight loss.")
    elif bmi_value > 25:
        st.info("📌 Your BMI suggests focusing on a moderate calorie deficit of 300-500 calories per day.")
    else:
        st.info("📌 Your BMI is in a healthy range. Focus on quality nutrition rather than significant calorie restriction.")

elif goal_value == "Muscle Gain":
    food_recommendations = muscle_gain_foods
    st.write("### Foods to Support Muscle Growth")
    st.write("Focus on protein-rich foods and sufficient carbohydrates to fuel your workouts.")
    st.info("📌 Aim to consume 1.6-2.2g of protein per kg of bodyweight daily for optimal muscle growth.")

else:  # Maintenance
    food_recommendations = maintenance_foods
    st.write("### Foods for Maintaining Your Current Physique")
    st.write("Focus on balanced nutrition with adequate amounts of all macronutrients.")
    st.info("📌 Aim to match your calorie intake with your energy expenditure for weight maintenance.")

# Create expandable sections for each food category
for category, foods in food_recommendations.items():
    with st.expander(f"{category} - Click to expand"):
        # Create columns for food items
        cols = st.columns(2)
        for i, food in enumerate(foods):
            cols[i % 2].write(f"- {food}")

# Sample meal plan based on goal
st.write("### Sample Daily Meal Plan")
if goal_value == "Weight Loss":
    st.markdown("""
    - **Breakfast**: Greek yogurt with berries and a sprinkle of nuts
    - **Lunch**: Grilled chicken salad with olive oil dressing
    - **Snack**: Apple with a small handful of almonds
    - **Dinner**: Baked white fish with steamed vegetables
    - **Evening**: Herbal tea
    """)
elif goal_value == "Muscle Gain":
    st.markdown("""
    - **Breakfast**: Oatmeal with banana, whey protein and peanut butter
    - **Lunch**: Chicken breast, brown rice and mixed vegetables
    - **Pre-workout**: Greek yogurt with berries
    - **Post-workout**: Protein shake with banana
    - **Dinner**: Salmon with sweet potatoes and broccoli
    - **Evening**: Cottage cheese with a small handful of nuts
    """)
else:  # Maintenance
    st.markdown("""
    - **Breakfast**: Eggs with whole grain toast and avocado
    - **Lunch**: Quinoa bowl with vegetables and lean protein
    - **Snack**: Greek yogurt with fruit
    - **Dinner**: Stir-fry with vegetables and tofu
    - **Evening**: Small serving of dark chocolate or fruit
    """)

# NEW FEATURE: Recommended Beverages
st.write("---")
st.header("Recommended Beverages for Your Fitness Goal")

# Define drinks and juices for each fitness goal
weight_loss_drinks = {
    "Juices": [
        {"name": "Green Juice", "benefits": "Low-calorie, nutrient-dense, aids metabolism", "ingredients": "Cucumber, celery, spinach, green apple, lemon"},
        {"name": "Carrot & Ginger Juice", "benefits": "Packed with nutrients, aids digestion", "ingredients": "Carrots, ginger, lemon, apple"},
        {"name": "Watermelon Juice", "benefits": "Low-calorie, hydrating, natural sweetness", "ingredients": "Watermelon, mint leaves, lime (optional)"}
    ],
    "Teas & Infusions": [
        {"name": "Green Tea", "benefits": "Contains catechins that may aid fat burning", "ingredients": "Green tea leaves, optional lemon or honey"},
        {"name": "Cinnamon Tea", "benefits": "May help regulate blood sugar levels", "ingredients": "Cinnamon sticks, hot water, optional honey"}
    ],
    "Smoothies": [
        {"name": "Berry Protein Smoothie", "benefits": "Filling, antioxidant-rich, low-calorie", "ingredients": "Mixed berries, protein powder, almond milk, ice"}
    ],
    "Avoid": "Fruit juices with added sugars, alcoholic beverages, sugary sodas and energy drinks"
}

muscle_gain_drinks = {
    "Juices": [
        {"name": "Beet & Berry Juice", "benefits": "May improve workout performance and recovery", "ingredients": "Beets, mixed berries, apple, ginger"},
        {"name": "Pineapple & Turmeric Juice", "benefits": "Anti-inflammatory, aids recovery", "ingredients": "Pineapple, turmeric, black pepper, orange"}
    ],
    "Protein Drinks": [
        {"name": "Classic Protein Shake", "benefits": "Supports muscle growth and recovery", "ingredients": "Whey protein, milk/water, banana, ice"},
        {"name": "Chocolate Cherry Recovery Shake", "benefits": "Supports recovery after intense workouts", "ingredients": "Chocolate protein powder, cherries, yogurt, honey"}
    ],
    "Pre-Workout": [
        {"name": "Banana Coffee Energizer", "benefits": "Natural energy boost for workouts", "ingredients": "Banana, cold coffee, protein powder, almond milk"}
    ],
    "Avoid": "Alcohol (limits protein synthesis), excessive caffeine which can cause dehydration"
}

maintenance_drinks = {
    "Juices": [
        {"name": "Balanced Green Juice", "benefits": "Nutrient-dense, good source of vitamins", "ingredients": "Kale, cucumber, apple, celery, lemon"},
        {"name": "Carrot Orange Juice", "benefits": "Vitamin-rich, immune support", "ingredients": "Carrots, oranges, ginger, turmeric"}
    ],
    "Smoothies": [
        {"name": "Complete Nutrition Smoothie", "benefits": "Balanced macronutrients and micronutrients", "ingredients": "Greek yogurt, banana, spinach, berries, nut butter, chia seeds"}
    ],
    "Teas & Infusions": [
        {"name": "Herbal Tea Medley", "benefits": "Hydration with various health benefits", "ingredients": "Rotating variety of herbal teas like chamomile, mint, rooibos"}
    ],
    "Avoid": "Excessive sugary drinks and alcohol, which provide empty calories"
}

# Function to display drink recommendation cards
def display_drink_card(drink):
    st.markdown(
        f"""
        <div style="background-color:#f8f9fa; padding:15px; border-radius:10px; margin-bottom:15px;">
            <h4 style="color:#4CAF50;">{drink['name']}</h4>
            <p><strong>Benefits:</strong> {drink['benefits']}</p>
            <p><strong>Ingredients:</strong> {drink['ingredients']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Display appropriate drink recommendations based on goal
if goal_value == "Weight Loss":
    drinks = weight_loss_drinks
    st.write("### Beverages to Support Weight Loss")
    st.write("These drinks can help you stay hydrated while supporting your weight loss goals. They're low in calories but high in nutrients.")
    
elif goal_value == "Muscle Gain":
    drinks = muscle_gain_drinks
    st.write("### Beverages to Support Muscle Growth")
    st.write("These drinks focus on providing nutrition that supports recovery and muscle building. Protein and anti-inflammatory ingredients are key.")
    
else:  # Maintenance
    drinks = maintenance_drinks
    st.write("### Beverages for Overall Health Maintenance")
    st.write("These balanced drinks provide a good mix of nutrients to support your overall health and fitness maintenance.")

# Display drink categories with expandable sections
for category, items in drinks.items():
    if category != "Avoid":
        with st.expander(f"{category} - Click to see options"):
            for drink in items:
                display_drink_card(drink)
    else:
        st.warning(f"⚠️ **Beverages to Avoid:** {items}")

# Hydration tips based on user's BMI and goals
st.write("### Hydration Schedule")
water_intake = round(df['BMI'].values[0] * 0.035 * 1000, 2)
caffeine_limit = "300mg (about 2-3 cups of coffee)" if goal_value == "Weight Loss" else "400mg (about 3-4 cups of coffee)"

st.markdown(f"""
- Morning: 500ml water upon waking + 1 recommended morning beverage
- Mid-morning: 500ml water
- Lunch: 500ml water with meal
- Afternoon: One of the recommended juices or teas
- Pre/Post Workout: {500 if goal_value == "Muscle Gain" else 300}ml water
- Evening: Herbal tea or infused water
- Limit caffeine to {caffeine_limit} per day
- Total daily water intake goal: {water_intake}ml
""")


# NEW FEATURE: Fitness Days Prediction
st.write("---")
st.header("Fitness Progress Prediction")

# Calculate predicted days to reach fitness goals based on adherence
def predict_fitness_days(bmi, goal, adherence, age):
    base_days = 0
    
    # Baseline days based on BMI and goal
    if goal == "Weight Loss":
        if bmi > 30:
            base_days = 120
        elif bmi > 25:
            base_days = 90
        else:
            base_days = 60
    elif goal == "Muscle Gain":
        if bmi < 20:
            base_days = 100
        elif bmi < 25:
            base_days = 80
        else:
            base_days = 120
    else:  # Maintenance
        base_days = 60
    
    # Adjust based on adherence (7 days = optimal)
    adherence_factor = 7 / adherence
    
    # Age adjustment (older people might need more time)
    age_factor = 1 + max(0, (age - 30) / 100)
    
    # Final prediction
    predicted_days = round(base_days * adherence_factor * age_factor)
    
    return predicted_days

# Get predicted days
predicted_days = predict_fitness_days(
    df['BMI'].values[0], 
    goal_value, 
    adherence_days,
    df['Age'].values[0]
)

# Progress milestones
milestone1 = round(predicted_days * 0.25)
milestone2 = round(predicted_days * 0.5)
milestone3 = round(predicted_days * 0.75)

st.write(f"### Based on your parameters and {adherence_days} days/week routine adherence:")
st.markdown(f"""
- **Expected time to reach your {goal_value} goal:** {predicted_days} days
- **First results visible:** Around day {milestone1}
- **Halfway point:** Around day {milestone2}
- **Significant progress:** Around day {milestone3}
""")

# Adherence impact visualization
st.subheader("Impact of Routine Adherence")
adherence_impact = []
for days in range(1, 8):
    impact_days = predict_fitness_days(
        df['BMI'].values[0], 
        goal_value, 
        days,
        df['Age'].values[0]
    )
    adherence_impact.append({"Days Per Week": days, "Time to Goal (days)": impact_days})

impact_df = pd.DataFrame(adherence_impact)
st.line_chart(impact_df.set_index("Days Per Week"))
st.write("*Increasing your weekly routine adherence can significantly reduce the time needed to reach your fitness goals.*")



st.write("---")
st.header("Hydration Tracker")
st.write(f"Recommended daily water intake: {round(df['BMI'].values[0] * 0.035 * 1000, 2)} ml")

# Download as PDF
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Add title and styling
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, "Personal Fitness Tracker Report", ln=True, align="C")
    pdf.line(10, 20, 200, 20)
    pdf.ln(5)
    
    # User Parameters
    pdf.set_font("Arial", "B", size=14)
    pdf.cell(200, 10, "Your Parameters:", ln=True)
    pdf.set_font("Arial", size=12)
    
    # Display all user inputs
    for col in df.columns:
        display_name = col.replace('_', ' ')
        pdf.cell(200, 8, f"{display_name}: {df[col].values[0]}", ln=True)
    
    # Show gender and fitness goal
    gender_val = "Male" if df["Gender_male"].values[0] == 1 else "Female"
    pdf.cell(200, 8, f"Gender: {gender_val}", ln=True)
    pdf.cell(200, 8, f"Fitness Goal: {goal_value}", ln=True)
    pdf.cell(200, 8, f"Expected Routine Adherence: {adherence_days} days per week", ln=True)
    
    # Calorie Prediction
    pdf.ln(5)
    pdf.set_font("Arial", "B", size=14)
    pdf.cell(200, 10, "Calorie Prediction:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, f"Estimated Calories Burned: {round(prediction[0], 2)} kilocalories", ln=True)
    
    # Walking Distance
    pdf.ln(5)
    pdf.set_font("Arial", "B", size=14)
    pdf.cell(200, 10, "Walking Distance to Burn Calories:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, f"Distance Required: {kilometers_needed} kilometers", ln=True)
    
    # Dietary Recommendations
    pdf.ln(5)
    pdf.set_font("Arial", "B", size=14)
    pdf.cell(200, 10, "Dietary & Fitness Recommendations:", ln=True)
    pdf.set_font("Arial", size=12)
    
    if goal_value == "Weight Loss":
        pdf.cell(200, 8, "Suggested Diet: High-protein, low-carb meals", ln=True)
    elif goal_value == "Muscle Gain":
        pdf.cell(200, 8, "Suggested Diet: High-calorie, protein-rich meals", ln=True)
    else:
        pdf.cell(200, 8, "Suggested Diet: Balanced nutrition", ln=True)
    
    # Food Recommendations
    pdf.ln(5)
    pdf.set_font("Arial", "B", size=14)
    pdf.cell(200, 10, "Recommended Foods:", ln=True)
    pdf.set_font("Arial", size=12)
    
    # Get the appropriate food recommendations based on goal
    if goal_value == "Weight Loss":
        food_recommendations = weight_loss_foods
    elif goal_value == "Muscle Gain":
        food_recommendations = muscle_gain_foods
    else:
        food_recommendations = maintenance_foods
    
    # Add food categories to PDF
    for category, foods in food_recommendations.items():
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(200, 8, f"{category}:", ln=True)
        pdf.set_font("Arial", size=12)
        
        # Add food items with Latin-1 compatible bullet points
        for food in foods:
            pdf.cell(10, 8, "- ", ln=0)
            pdf.cell(190, 8, food, ln=1)
    
    # Sample Meal Plan
    pdf.ln(5)
    pdf.set_font("Arial", "B", size=14)
    pdf.cell(200, 10, "Sample Daily Meal Plan:", ln=True)
    pdf.set_font("Arial", size=12)
    
    if goal_value == "Weight Loss":
        meals = ["Breakfast: Greek yogurt with berries and a sprinkle of nuts",
                "Lunch: Grilled chicken salad with olive oil dressing",
                "Snack: Apple with a small handful of almonds",
                "Dinner: Baked white fish with steamed vegetables",
                "Evening: Herbal tea"]
    elif goal_value == "Muscle Gain":
        meals = ["Breakfast: Oatmeal with banana, whey protein and peanut butter",
                "Lunch: Chicken breast, brown rice and mixed vegetables",
                "Pre-workout: Greek yogurt with berries",
                "Post-workout: Protein shake with banana",
                "Dinner: Salmon with sweet potatoes and broccoli",
                "Evening: Cottage cheese with a small handful of nuts"]
    else:  # Maintenance
        meals = ["Breakfast: Eggs with whole grain toast and avocado",
                "Lunch: Quinoa bowl with vegetables and lean protein",
                "Snack: Greek yogurt with fruit",
                "Dinner: Stir-fry with vegetables and tofu",
                "Evening: Small serving of dark chocolate or fruit"]
    
    for meal in meals:
        pdf.cell(10, 8, "- ", ln=0)
        pdf.cell(190, 8, meal, ln=1)
    
    # Recommended Beverages
    pdf.ln(5)
    pdf.set_font("Arial", "B", size=14)
    pdf.cell(200, 10, "Recommended Beverages:", ln=True)
    pdf.set_font("Arial", size=12)
    
    # Get appropriate drinks based on goal
    if goal_value == "Weight Loss":
        drinks = weight_loss_drinks
    elif goal_value == "Muscle Gain":
        drinks = muscle_gain_drinks
    else:
        drinks = maintenance_drinks
    
    # Add drink categories to PDF
    for category, items in drinks.items():
        if category != "Avoid":
            pdf.set_font("Arial", "B", size=12)
            pdf.cell(200, 8, f"{category}:", ln=True)
            pdf.set_font("Arial", size=12)
            
            for drink in items:
                pdf.set_font("Arial", "B", size=11)
                pdf.cell(200, 8, drink["name"], ln=True)
                pdf.set_font("Arial", "I", size=10)
                pdf.cell(200, 6, f"Benefits: {drink['benefits']}", ln=True)
                pdf.cell(200, 6, f"Ingredients: {drink['ingredients']}", ln=True)
                pdf.ln(2)
        else:
            pdf.set_font("Arial", "B", size=12)
            pdf.cell(200, 8, "Beverages to Avoid:", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 8, items, ln=True)
    
    # Hydration Guide
    pdf.ln(5)
    pdf.set_font("Arial", "B", size=14)
    pdf.cell(200, 10, "Hydration Guide:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, f"Recommended daily water intake: {round(df['BMI'].values[0] * 0.035 * 1000, 2)} ml", ln=True)
    
    # Hydration schedule
    caffeine_limit = "300mg (about 2-3 cups of coffee)" if goal_value == "Weight Loss" else "400mg (about 3-4 cups of coffee)"
    hydration_items = [
        f"Morning: 500ml water upon waking + 1 recommended morning beverage",
        f"Mid-morning: 500ml water",
        f"Lunch: 500ml water with meal",
        f"Afternoon: One of the recommended juices or teas",
        f"Pre/Post Workout: {500 if goal_value == 'Muscle Gain' else 300}ml water",
        f"Evening: Herbal tea or infused water",
        f"Limit caffeine to {caffeine_limit} per day"
    ]
    
    for item in hydration_items:
        pdf.cell(10, 8, "- ", ln=0)
        pdf.cell(190, 8, item, ln=1)
    
    # Fitness Progress Prediction
    pdf.add_page()
    pdf.set_font("Arial", "B", size=14)
    pdf.cell(200, 10, "Fitness Progress Prediction:", ln=True)
    pdf.set_font("Arial", size=12)
    
    # Milestone calculations
    milestone1 = round(predicted_days * 0.25)
    milestone2 = round(predicted_days * 0.5)
    milestone3 = round(predicted_days * 0.75)
    
    pdf.cell(200, 8, f"Expected time to reach your {goal_value} goal: {predicted_days} days", ln=True)
    pdf.cell(200, 8, f"First results visible: Around day {milestone1}", ln=True)
    pdf.cell(200, 8, f"Halfway point: Around day {milestone2}", ln=True)
    pdf.cell(200, 8, f"Significant progress: Around day {milestone3}", ln=True)
    
    # Motivational message
    pdf.ln(10)
    pdf.set_font("Arial", "B", size=14)
    pdf.cell(200, 10, "Your Motivation:", ln=True)
    pdf.set_font("Arial", "I", size=12)
    pdf.multi_cell(0, 8, "Remember: Consistency is key to achieving your fitness goals. Small steps taken daily lead to significant results over time. Stay hydrated, follow your meal plan, and maintain your exercise routine. You've got this!")
    
    # Footer with date
    pdf.ln(10)
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    pdf.set_font("Arial", "I", size=10)
    pdf.cell(0, 10, f"Report generated on {today}", ln=True, align="R")
    
    return pdf.output(dest='S').encode('latin1')
    
st.write("---")
st.header("Download Your Fitness Report")
pdf_data = create_pdf()
st.download_button("Download PDF Report", data=pdf_data, file_name="fitness_report.pdf", mime="application/pdf")


# About Section
st.write("---")
st.header("About")
st.header("Personal Fitness Tracker: Your Journey to a Healthier You")
st.write("This app helps You to track your fitness progress, predict calorie burn, get dietary recommendations, hydration tracking, and yoga suggestions. It also provide you a daily fitness Chart.")
st.write("The Personal Fitness Tracker is an easy-to-use app that helps you reach your fitness goals.")
st.header("What This App Does")
st.write("Track Your Stats: Enter your basic information like age, weight, and activity level to get started.")
st.write("Predict Calories Burned: See how many calories you'll burn during your workout based on your personal details.")
st.write("Set Fitness Goals: Choose what you want to achieve – lose weight, build muscle, or maintain your current fitness.")
st.write("Timeline to Success: Our new feature shows you how long it might take to reach your goals based on how often you exercise each week. The more consistent you are, the faster you'll see results!")
st.write("Drink Recommendations: Get personalized suggestions for healthy beverages that support your fitness goals, whether you're trying to lose weight or build muscle.")
st.write("Hydration Guide: Learn how much water you should drink each day and follow a simple schedule to stay hydrated.")
st.write("Create Your Fitness Report: Download a personalized PDF report that includes all your stats, predictions, and recommendations to keep you on track.")

# Help Section
st.write("---")
st.header("Help")
st.header("How It Helps You")
st.write("This app takes the guesswork out of fitness by giving you a clear path to follow. It shows you:")
st.write("How your consistency affects your results")
st.write("What to drink to support your workouts")
st.write("When you can expect to see changes in your body")
st.write("How to stay properly hydrated")
feedback = st.text_area("Provide your feedback here:")
if st.button("Submit Feedback"):
    st.success("Thank you for your feedback!")