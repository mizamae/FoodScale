from celery import shared_task
import os
import json
import logging
logger = logging.getLogger("celery")

from .models import Ingredient

@shared_task(bind=False,name='FoodAPP_loadDefaultObjects')
def loadDefaultObjects():
    DBFilename = 'DB.json'
    if os.path.isfile(DBFilename):
        with open(DBFilename,'r') as fp:
            BBDD = json.load(fp)

        for alimento in BBDD['alimentos']:
            data = {'id':alimento['id'],'name':alimento['nombre'],'nutrients':{}}
            for family in alimento['nutrients']:
                data['nutrients'][family['name'].lower()]=family['nutrients']
                for i,elem in enumerate(data['nutrients'][family['name'].lower()]):
                    """ cleaning all """
                    if "(" in elem['quant']:
                        elem['quant']=float(elem['quant'].split("(")[1].replace(")",""))
                        elem['unit']=elem['unit'].split("(")[1].replace(")","")
                    elif "-" in elem['quant']:
                        elem['quant']=0
                    else:
                        try:
                            elem['quant']=float(elem['quant'])
                        except: # if it is a traza quantity
                            elem['quant']=1e-6
            ingredient,created = Ingredient.objects.update_or_create(**data)
            if created:
                logger.info("Ingredient " + str(ingredient) +" created")
    else:
        logger.warning("Default DB file was not found at ")