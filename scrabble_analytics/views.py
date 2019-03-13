from django.shortcuts import render
from django.views import View
from scrabble_analytics.forms import SubmitLettersForm
from scrabble_analytics.utils import get_clean_list_letters, get_search_result, get_parameter_value, filtered_dataframe, return_error_page

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
            #df.to_excel('test.xlsx')
            if len(queries) > 1: #Do we have parameters in the query?
                for parameter in queries[1:]:

                    label, value = get_parameter_value(parameter)
                    if (label is None) and (value is None):
                        return return_error_page(request,'The label and/or the value are not correct')
                    df = filtered_dataframe(df,label,value)
                    if df is None:
                        return return_error_page(request,'The label and/or the value are not correct')
            if df is not None:
                context = {
                    "form": the_form,
                    "has_result":True,
                    "list_letters": letters,
                    "free_letter" : free_letter,
                    "table" : df.sort_values(by='score',ascending=False)[['words','missing']].groupby(by='missing', axis=0, as_index=False).agg(lambda x: ', '.join(x)).to_html(index = False, classes="table table-striped")
                }
                print('the request is: ',request)
                return render(request, "scrabble/home.html", context)
            else:
                return return_error_page(request,'The set of data to return is NULL')
        else:
            return return_error_page(request,'The form is not valid!')

def About(request, *args, **kwargs):
    return render(request, 'scrabble/about.html')
