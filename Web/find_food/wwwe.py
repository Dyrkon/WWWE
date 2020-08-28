import re
from collections import namedtuple

import requests
from bs4 import BeautifulSoup

# from . import values

cbookquery_n = 'https://www.recepty.cz/vyhledavani/pokrocile?showResults=1&rating=3&mess=2&catalog%5B0%5D=541&catalog' \
               '%5B1%5D=543&catalog%5B2%5D=544&catalog%5B3%5D=545&catalog%5B4%5D=542&catalog%5B5%5D=546&catalog%5B6' \
               '%5D=547&catalog%5B7%5D=654&catalog%5B8%5D=660&catalog%5B9%5D=662&catalog%5B10%5D=664&catalog%5B11%5D' \
               '=670&catalog%5B12%5D=655&catalog%5B13%5D=656&catalog%5B14%5D=657&catalog%5B15%5D=659&catalog%5B16%5D' \
               '=667&catalog%5B17%5D=669&catalog%5B18%5D=713&catalog%5B19%5D=714&catalog%5B20%5D=716&catalog%5B21%5D' \
               '=724&catalog%5B22%5D=740&catalog%5B23%5D=715&catalog%5B24%5D=717&catalog%5B25%5D=718&catalog%5B26%5D' \
               '=719&catalog%5B27%5D=720&catalog%5B28%5D=722&catalog%5B29%5D=730&catalog%5B30%5D=741&catalog%5B31%5D' \
               '=738&catalog%5B32%5D=739&catalog%5B33%5D=755&catalog%5B34%5D=765&catalog%5B35%5D=774 '

# variables
base_web = "https://www.recepty.cz/"
unfound_list = []


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
        raw_price = soup.find("div", class_="pricePerOffer pricePer").text.replace(',', '.')
        try:
            price = ''.join(re.findall(r'\d+\.\d+', raw_price))
            price = float(price)
        except AttributeError:
            raise AttributeError

        return price * float(quant)
    except AttributeError:
        unfound_list.append(item_name)


def multiply_quant(quant, amount):
    bruh = 0
    for i in quant:
        bruh = float(i)
        bruh *= float(amount)
    return bruh


def get_name(food_link):
    r = requests.get(food_link)
    soup = BeautifulSoup(r.content, "lxml")
    return soup.find('h1', class_='recipe-title-box__title', text=True).text


def get_quant(string):
    if '.' in string:
        if (out := '.'.join(re.findall(r'\d+\.\d+', string))) != '':
            return float(out)
    else:
        if (out := ''.join(re.findall(r'\d+', string))) != '':
            return float(out)


def does_contain(contains, string):
    con = r'\b' + contains + r'\b'
    if re.findall(con, string):
        return True
    else:
        return False


def get_price(ingredients_link):
    ingrediencs = get_ingrediencts(ingredients_link)
    food_name = get_name(ingredients_link)
    unfound_list.clear()
    ingredienc_output = []
    price = 0
    price_total = 0
    for ing in ingrediencs:
        if does_contain(',', ing):
            ing = ing.replace(',', '.', 1)
        quantity = get_quant(ing)
        if quantity:
            if does_contain('ks', ing):
                ing_to_search = str(ing).replace(str(int(quantity)) + '  ks ', "", 1)
                price = find_price(ing_to_search, quantity)
            elif does_contain('g', ing):
                ing_to_search = str(ing).replace(str(int(quantity)) + '  g ', "", 1)
                price = find_price(ing_to_search, quantity * 0.001)
            elif does_contain('ml', ing):
                ing_to_search = str(ing).replace(str(int(quantity)) + '  ml ', "", 1)
                price = find_price(ing_to_search, quantity * 0.001)
            elif does_contain('lžička', ing):
                ing_to_search = str(ing).replace(str(int(quantity)) + '  lžička ', "", 1)
                price = find_price(ing_to_search, quantity * 0.006)
            elif does_contain('lžíce', ing):
                ing_to_search = str(ing).replace(str(int(quantity)) + '  lžíce ', "", 1)
                price = find_price(ing_to_search, quantity * 0.006)
            elif does_contain('dl', ing):
                ing_to_search = str(ing).replace(str(int(quantity)) + '  dl ', "", 1)
                price = find_price(ing_to_search, quantity * 10)
            elif does_contain('stroužek', ing):
                ing_to_search = str(ing).replace(str(int(quantity)) + '  stroužek ', "", 1)
                price = find_price(ing_to_search, quantity * 0.02)
            elif does_contain('l', ing):
                ing_to_search = str(ing).replace(str(int(quantity)) + '  l ', "", 1)
                price = find_price(ing_to_search, quantity * 1)
            else:
                continue

        else:
            ing_to_search = str(ing)
            price = find_price(ing_to_search, 1)

        if ing_to_search is not None and not []:
            ingredienc_output.append(ing_to_search)
            if price is not None:
                price_total += price

    for ing_o in ingredienc_output:
        if ing_o in unfound_list:
            ingredienc_output.remove(ing_o)

    jidlo = namedtuple("jidlo", ["ingredints", "price", "name", 'link', "unfound_list"])
    return jidlo(', '.join(ingredienc_output), round(price_total), food_name, ingredients_link, ', '.join(unfound_list))


def whole_food(food_num, links):
    return get_price(links[food_num])
