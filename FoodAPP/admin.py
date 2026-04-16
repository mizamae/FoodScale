from django.contrib import admin

from .models import IngredientFamily, Ingredient

class IngredientFamilyAdmin(admin.ModelAdmin):
    list_display = ("name","short_description","itemCount")
    ordering = ('-name',)

admin.site.register(IngredientFamily, IngredientFamilyAdmin)

class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name","family")
    ordering = ('-name',)

admin.site.register(Ingredient, IngredientAdmin)