from django.shortcuts import render
from django.views import View
from scrabble_analytics.forms import SubmitLettersForm
from scrabble_analytics.models import WordsObject
from scrabble_analytics.utils import get_clean_list_letters, get_list_of_words

class HomeView(View):
    def get(self, request, *args, **kwargs):
        the_form = SubmitLettersForm()
        context = {
            "form": the_form,
            "has_result":False,
        }
        return render(request, "scrabble/home.html", context)
    
    def post(self, request, *args, **kwargs):
    
        the_form = SubmitLettersForm(request.POST)
        if the_form.is_valid():
            list_letters = the_form.cleaned_data['list_letters']

            letters, free_letter = get_clean_list_letters(list_letters.upper())
            df = get_list_of_words(letters, free_letter+1)

            context = {
                "form": the_form,
                "has_result":True,
                "list_letters": letters,
                "free_letter" : free_letter,
                "table" : df.sort_values(by='score',ascending=False)[['words','missing']].groupby(by='missing', axis=0, as_index=False).agg(lambda x: ', '.join(x)).to_html(index = False, classes="table table-striped")
            }
        return render(request, "scrabble/home.html", context)
