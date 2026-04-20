# https://adiramadhan17.medium.com/django-crud-with-bootstrap-modal-form-with-htmx-3cbe3830ecfa
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
import datetime
from .forms import CombinationPositionFormSet, CombinationPositionInlineForm, CombinationPositionInTable
from .models import Meal, CombinationPosition, Ingredient
import logging
logger = logging.getLogger("users")

@login_required
def calculator(request,dayOffset=0):
    day = datetime.date.today() + datetime.timedelta(days=dayOffset)
    return render(request, 'FoodAPP/calculator.html',{'back_to':'home','day':day,'dayOffset':dayOffset}) 

@login_required
def addIngredient(request,dayOffset):
    day = datetime.date.today() + datetime.timedelta(days=dayOffset)
    if request.method == "POST":
        # we have to do this to assign teh ingrdient field before form validation
        updated_data = request.POST.copy()
        updated_data.update({'ingredient': Ingredient.objects.get(name=updated_data['ingredientInput'])}) 
        form = CombinationPositionInTable(data=updated_data)
        if form.is_valid():
            mealType = int(form.cleaned_data.get('mealType'))
            ingredient = form.cleaned_data.get('ingredient')
            quantity = form.cleaned_data.get('quantity')
            try:
                meal = Meal.objects.get(dateTime__date=day,type=mealType,owner=request.user)
            except Meal.DoesNotExist:
                MyTime = timezone.now().time().replace(microsecond=0)
                meal = Meal.objects.create(dateTime=datetime.datetime.combine(day, MyTime),type=mealType,owner=request.user)
            meal.appendIngredient(quantity=quantity,ingredient=ingredient)
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "ingredientListChanged": None,
                        "showMessage": f"{ingredient.name} añadido."
                    })
                })
        else:
            return render(request, 'FoodAPP/ingredientAddForm.html', {
                'form': form,
            })
    else:
        form = CombinationPositionInTable()
    return render(request, 'FoodAPP/ingredientAddForm.html', {
        'form': form,
    })

@login_required
def viewDayMeals(request,dayOffset):
    day = datetime.date.today() + datetime.timedelta(days=dayOffset)
    meals = Meal.objects.filter(dateTime__date=day,owner = request.user).order_by("type")
    positions=[]
    for meal in meals:
        positions+=list(meal.ingredients)
    return render(request, 'FoodAPP/mealingredients.html', {'positions': positions,'day':day})

@login_required
def viewDayNutrients(request,dayOffset):
    day = datetime.date.today() + datetime.timedelta(days=dayOffset)
    positions=Meal.accumulateDailyNutrients(day=day,user=request.user)
    return render(request, 'FoodAPP/daynutrients.html', {'positions': positions})

@login_required
def viewDayNutrientsGraph(request,dayOffset):
    day = datetime.date.today() + datetime.timedelta(days=dayOffset)
    figure = Meal.getNutrientsPlot(day,request.user)
    return render(request, 'FoodAPP/daynutrientsgraph.html', {'nutrientsPlot':figure})

def ingredient_autocomplete(request):
    q = request.GET.get("q", "")
    ingredients = []

    if q:
        ingredients = Ingredient.objects.filter(name__icontains=q)[:10]

    return render(request, "FoodAPP/ingredient_options.html", {
        "ingredients": ingredients
    })

@login_required
def editIngredient(request,pk):
    pos = CombinationPosition.objects.get(pk=pk)
    if request.method == "POST":
        form = CombinationPositionInTable(request.POST,**{'editing':True})
        if form.is_valid():
            if 'quantity' in form.changed_data:
                quantity = form.cleaned_data.get('quantity')
                pos.updateQuantity(newQuantity=quantity)
            return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "ingredientListChanged": None,
                        "showMessage": f"Cantidad de {pos.ingredient.name} modificada."
                    })
                })
        else:
            return render(request, 'FoodAPP/ingredientEditForm.html', {
                'form': form,
            })
    else:
        
        form = CombinationPositionInTable(instance=pos,**{'editing':True})
        return render(request, 'FoodAPP/ingredientEditForm.html', {
            'form': form,
        })

@csrf_exempt
@login_required
def removeIngredient(request,pk):
    pos = CombinationPosition.objects.get(pk=pk)
    if request.method == "POST":
        pos.delete()
        return HttpResponse(
                status=204,
                headers={
                    'HX-Trigger': json.dumps({
                        "ingredientListChanged": None,
                        "showMessage": f"{pos.ingredient.name} eliminado."
                    })
                })