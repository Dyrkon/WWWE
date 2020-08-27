from django.db import models


# Create your models here.
class Food(models.Model):
    name = models.TextField(default='Jmeno jidla')
    price = models.FloatField(default='Cena jidla')
    link = models.TextField(default='link na recept')
    ingredients = models.TextField(default='Ingredience')
    u_ingredients = models.TextField(default='Nenalezene polozky')
