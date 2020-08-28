from django.shortcuts import render
from find_food import wwwe as w


class val:
    links = []
    num = 0


# Create your views here.
def home_view(request, *args, **kwargs):
    if request.method == 'POST' and 'Next_food' in request.POST:
        val.links = w.get_links()
        if val.links is []:

            val.num = 0
        elif val.num is not None:
            val.num += 1

        food = w.whole_food(val.num, val.links)
        return render(request, "home.html", {'name': food.name,
                                             'price': food.price,
                                             'ingredints': food.ingredints,
                                             'link': food.link,
                                             'unfound_list': food.unfound_list})
    return render(request, "home.html", {})
