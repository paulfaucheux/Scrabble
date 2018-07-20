from django.shortcuts import render
from django.views import View
from scrabble_analytics.forms import SubmitLettersForm
from scrabble_analytics.utils import get_clean_list_letters, get_additional_param, get_list_of_words, get_search_result

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
            query = the_form.cleaned_data['list_letters']
            queries = query.split('&')
            list_letters = queries[0].strip()
            letters, free_letter = get_clean_list_letters(list_letters.upper())
            df = get_search_result(letters, free_letter)

            if len(queries) > 1:
                for param in queries:
                    filter_param = param.split(':')
                    label, value = get_additional_param(filter_param)
                    df = df[label].str.contains(value)

            context = {
                "form": the_form,
                "has_result":True,
                "list_letters": letters,
                "free_letter" : free_letter,
                "table" : df.sort_values(by='score',ascending=False)[['words','missing']].groupby(by='missing', axis=0, as_index=False).agg(lambda x: ', '.join(x)).to_html(index = False, classes="table table-striped")
            }
        return render(request, "scrabble/home.html", context)
