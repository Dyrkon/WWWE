import re
from collections import namedtuple

import requests
from bs4 import BeautifulSoup

from food_variables import *


def get_links():
    link_list = []
    r = requests.get(cbookquery_n)
    soup = BeautifulSoup(r.content, "lxml")

    recipies = soup.find_all('a', class_='loading-placeholder', href=True)
    for rec in recipies:
        link_list.append(base_web + rec.get("href"))
    return link_list


def get_ingrediencts(in_link):
    ingredients = []
    r = requests.get(in_link)
    soup = BeautifulSoup(r.content, "lxml")
    ings = soup.find_all("div", class_='ingredient-assignment__desc')
    for ing in ings:
        ingredients.append(ing_parse(ing.text).strip())
    return ingredients


def ing_parse(string):
    output = ""
    word_end = True
    for i in string:
        if ' ' != i and '\n' != i:
            output += i
            word_end = False
        elif '\n' == i or ' ' == i and output != '' and not word_end:
            output += ' '
            word_end = True
        else:
            continue
    return output


def find_price(item_name, quant):
    try:
        r = requests.get(f"https://www.rohlik.cz/hledat/{item_name}?companyId=1")
        soup = BeautifulSoup(r.content, "lxml")
        return round(
            float(soup.find("div", class_="pricePerOffer pricePer").text.strip(' Kč/kg').replace(',', '.')) * quant, 2)

    except:
        unfound_list.append(item_name)

def quant_multiply(quant, amount):
    bruh = 0
    for i in quant:
        bruh = float(i)
        bruh *= float(amount)
    return bruh


def get_name(food_link):
    r = requests.get(food_link)
    soup = BeautifulSoup(r.content, "lxml")
    return soup.find('h1', class_='recipe-title-box__title', text=True).text


def get_price(ingredients_link):
    ingrediencs = get_ingrediencts(ingredients_link)
    food_name = get_name(ingredients_link)
    unfound_list.clear()
    ingredienc_output = []
    price = 0
    price_total = 0
    for ing in ingrediencs:
        if ',' in ing:
            quantity = re.findall(r'\d+\.\d+', ing)
        else:
            quantity = re.findall(r'\d+', ing)
        if quantity:
            if ' ks ' in ing:
                ing_to_search = str(ing).strip(str(quantity) + ' ks ')
                price = find_price(ing_to_search, quantity)
            elif ' ml' in ing:
                ing_to_search = str(ing).strip(str(quantity) + ' ml ')
                price = find_price(ing_to_search,quant_multiply(quantity, 0.001))
            elif ' lžička' in ing:
                ing_to_search = str(ing).strip(str(quantity) + ' lžička ')
                price = find_price(ing_to_search, quant_multiply(quantity, 0.006))
            elif ' lžíce ' in ing:
                ing_to_search = str(ing).strip(str(quantity) + ' lžíce ')
                price = find_price(ing_to_search, quant_multiply(quantity, 0.006))
            elif ' dl ' in ing:
                ing_to_search = str(ing).strip(str(quantity) + ' dl ')
                price = find_price(ing_to_search, quant_multiply(quantity, 10))
            elif ' stroužek ' in ing:
                ing_to_search = str(ing).strip(str(quantity) + ' stroužek ')
                price = find_price(ing_to_search, quant_multiply(quantity, 0.02))
            elif '  g ' in ing:
                ing_to_search = str(ing).strip(str(quantity) + '  g ')
                price = find_price(ing_to_search, quant_multiply(quantity, 0.001))
            elif ' l ' in ing:
                ing_to_search = str(ing).strip(str(quantity) + ' l ')
                price = find_price(ing_to_search, quant_multiply(quantity, 1))
            else:
                continue
        else:
            ing_to_search = str(ing)
            price = find_price(ing_to_search, 0.3)

        if ing_to_search is not None and not []:
            ingredienc_output.append(ing_to_search)
            if price is not None:
                price_total += price

    for ing_o in ingredienc_output:
        if ing_o in unfound_list:
            ingredienc_output.remove(ing_o)

    jidlo = namedtuple("jidlo", ["ingredints", "price", "name", 'link', "unfound_list"])
    return jidlo(ingredienc_output, price_total, food_name, ingredients_link, unfound_list)

def run_food():
    for link in get_links():
        polozka = get_price(link)
        print('Jmeno: ' + polozka.name)
        print('Ingredience: ' + str(polozka.ingredints))
        # print(polozka.ingredints)
        print("Cena: " + str(polozka.price) + 'Kč')
        # print(polozka.cena)
        print('Nenalezene položky: ')
        if unfound_list:
            print(unfound_list)
        print(polozka.link)