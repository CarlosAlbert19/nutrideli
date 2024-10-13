import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pulp import *

csv_path = os.path.join(os.path.dirname(__file__), 'nutrition_traducido.csv')
data = pd.read_csv(csv_path).drop('Unnamed: 0', axis=1)
week_days = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
meals = ['Desayuno', 'Comida', 'Cena']
split_values = np.linspace(0, len(data), 8).astype(int) #Crea un array que contiene 8 valores equiespaciados entre 0 y la longitud de los datos de alimentos (data). Estos se utilizarán para dividir los datos.
split_values[-1] = split_values[-1] - 1 #Resta 1 al último valor de split_values para asegurarse de que el último rango no exceda la longitud del DataFrame.



def random_dataset():
    frac_data = data.sample(frac=1).reset_index().drop('index', axis=1) #Baraja los datos de alimentos aleatoriamente para crear variaciones.
    day_data = [] #Lista que almacenará subconjuntos de alimentos para cada día.
    for s in range(len(split_values) - 1): #Recorre los rangos de split_values, dividiendo los datos en partes para cada día de la semana.
        day_data.append(frac_data.loc[split_values[s]:split_values[s + 1]])
    return dict(zip(week_days, day_data)) #Devuelve un diccionario que asigna subconjuntos de datos de alimentos a cada día de la semana.

days_data = random_dataset()

def build_nutritional_values(kg, calories):
    protein_calories = kg * 4
    res_calories = calories - protein_calories
    carb_calories = calories / 2.
    fat_calories = calories - carb_calories - protein_calories
    res = {'Protein Calories': protein_calories, 'Carbohydrates Calories': carb_calories, 'Fat Calories': fat_calories}
    return res

def extract_gram(table):
    protein_grams = table['Protein Calories'] / 4.
    carbs_grams = table['Carbohydrates Calories'] / 4.
    fat_grams = table['Fat Calories'] / 9.
    res = {'Protein Grams': protein_grams, 'Carbohydrates Grams': carbs_grams, 'Fat Grams': fat_grams}
    return res

def convert_to_float(value):
    value = value.replace(' g', '').replace(' mg', '').replace('g', '').replace('mg', '')
    try:
        return float(value)
    except ValueError:
        return 0.0

def model(prob, kg, calories, meal, meal_data):
    G = extract_gram(build_nutritional_values(kg, calories)) #Calcula los gramos de macronutrientes necesarios a partir del peso y calorías.
    E = G['Carbohydrates Grams']
    F = G['Fat Grams']
    P = G['Protein Grams']
    meal_data = meal_data[meal_data.calories != 0] #Filtra los alimentos cuya cantidad de calorías no sea 0.
    #Define listas para los alimentos, sus calorías, y los nutrientes a optimizar.
    food = meal_data.name.tolist()
    c = meal_data.calories.tolist()
    x = pulp.LpVariable.dicts("x", indices=food, lowBound=0, upBound=1.5, cat='Continuous', indexStart=[]) #Variables de decisión para los alimentos, restringidas entre 0 y 1.5 porciones.
    e = meal_data.carbohydrate.tolist()
    f = meal_data.total_fat.tolist()
    p = meal_data.protein.tolist()

    e = [convert_to_float(value) for value in e]
    f = [convert_to_float(value) for value in f]
    p = [convert_to_float(value) for value in p]

    #Se definen las restricciones del problema de programación lineal (calorías mínimas, carbohidratos, proteínas y grasas).
    prob += pulp.lpSum([x[food[i]] * c[i] for i in range(len(food))])
    prob += pulp.lpSum([x[food[i]] * e[i] for i in range(len(x))]) >= E
    prob += pulp.lpSum([x[food[i]] * f[i] for i in range(len(x))]) >= F
    prob += pulp.lpSum([x[food[i]] * p[i] for i in range(len(x))]) >= P
    #Resuelve el problema de optimización.
    prob.solve(pulp.PULP_CBC_CMD(msg=False)) # Si se quiere mostrar todo lo de porcentaje y aciertos, solo borrar lo de los paréntesis


    variables = []
    values = []
    for v in prob.variables(): #Itera sobre todas las variables del problema de optimización (prob). En este contexto, las variables son los diferentes alimentos seleccionados por el modelo.
        variable = v.name
        value = v.varValue
        variables.append(variable)
        values.append(value)
    values = np.array(values).round(2).astype(float) #Convierte la lista de valores a un arreglo de Numpy, los redondea a 2 decimales, y los convierte en números flotantes.
    sol = pd.DataFrame(np.array([food, values]).T, columns=['Food', 'Quantity']) #Crea un DataFrame de pandas llamado sol
    sol['Quantity'] = sol.Quantity.astype(float)
    sol = sol[sol['Quantity'] != 0.0] #Filtra las filas del DataFrame, eliminando los alimentos que no fueron seleccionados por el modelo (aquellos con una cantidad igual a 0). Solo se conservan los alimentos que tienen una cantidad mayor a cero.
    sol.Quantity = sol.Quantity * 100 #Multiplica las cantidades seleccionadas por 100 para convertirlas en gramos. Este paso se basa en que las cantidades inicialmente estaban normalizadas o expresadas en unidades menores, por lo que es necesario convertirlas a cantidades utilizables (en gramos).
    sol = sol.rename(columns={'Quantity': 'Quantity (g)'})
    return sol #Devuelve el DataFrame sol, que contiene los alimentos seleccionados para esa comida y sus respectivas cantidades en gramos.

def random_dataset_day():
    frac_data = data.sample(frac=1).reset_index().drop('index', axis=1)
    day_data = []
    for s in range(len(split_values) - 1):
        day_data.append(frac_data.loc[split_values[s]:split_values[s + 1]])
    return dict(zip(week_days, day_data))

def random_dataset_meal(day_data):
    meal_split = np.linspace(0, len(day_data), 4).astype(int)
    return dict(zip(meals, [day_data.iloc[meal_split[i]:meal_split[i+1]] for i in range(len(meal_split)-1)]))

def better_model(kg, calories):
    days_data = random_dataset_day()
    res_model = []
    for day in week_days:
        day_data = days_data[day]
        meals_data = random_dataset_meal(day_data)
        meal_model = []
        for meal in meals:
            meal_data = meals_data[meal]
            prob = pulp.LpProblem("Diet", LpMinimize)
            sol_model = model(prob, kg, calories, meal, meal_data)
            meal_model.append(sol_model)
        res_model.append(meal_model)
    unpacked = []
    for i in range(len(res_model)):
        unpacked.append(dict(zip(meals, res_model[i])))
    unpacked_tot = dict(zip(week_days, unpacked))
    return unpacked_tot


def calculate_calories_basic(weight, height, sex):
    # Calcular TMB usando una fórmula simplificada
    if sex == 'masculino':
        tmb = 66 + (13.75 * weight) + (5 * height)
    else:
        tmb = 655 + (9.56 * weight) + (1.85 * height)
    
    # Asumir un nivel de actividad moderado para simplificar
    calories = tmb * 1.55
    
    return calories

# weight = 80  # en kg
# height = 180  # en cm
# sex = 'male'  # 'male' o 'female'
# calorias = calculate_calories_basic(weight, height, sex)

# diet = better_model(weight, calorias)
