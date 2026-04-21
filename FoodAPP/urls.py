from django.urls import path
from . import views

# Source - https://stackoverflow.com/a/48868140
# Posted by neverwalkaloner, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-16, License - CC BY-SA 3.0



urlpatterns = [
    path("calculator/<negint:dayOffset>", views.calculator, name="FoodAPP_calculator"),
    # path("createmeal/", views.createMeal, name="FoodAPP_createMeal"),
    path("ingredient-autocomplete/", views.ingredient_autocomplete, name="FoodAPP_ingredientAutocomplete"),
    path("meal/<negint:dayOffset>", views.viewDayMeals, name="FoodAPP_viewDayMeals"),
    path("meal/nutrients/<negint:dayOffset>", views.viewDayNutrients, name="FoodAPP_viewDayNutrients"),
    path("meal/nutrients/graph/nutrients/<negint:dayOffset>", views.viewDayNutrientsGraph, name="FoodAPP_graphDayNutrients"),
    path("meal/nutrients/graph/fat/<negint:dayOffset>", views.viewDayFatGraph, name="FoodAPP_graphDayFat"),
    path("meal/nutrients/table/fat/<negint:dayOffset>", views.viewDayFatTable, name="FoodAPP_tableDayFat"),
    path("meal/nutrients/table/vitamins/<negint:dayOffset>", views.viewDayVitaminsTable, name="FoodAPP_tableDayVitamins"),
    path("meal/nutrients/table/minerals/<negint:dayOffset>", views.viewDayMineralsTable, name="FoodAPP_tableDayMinerals"),
    path("meal/addingredient/<negint:dayOffset>", views.addIngredient, name="FoodAPP_addIngredient"),
    path("meal/removeingredient/<int:pk>", views.removeIngredient, name="FoodAPP_removeIngredient"),
    path("meal/editingredient/<int:pk>", views.editIngredient, name="FoodAPP_editIngredient"),
    
]