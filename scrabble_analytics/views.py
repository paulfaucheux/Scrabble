from django.shortcuts import render

class HomeView(View):
    def get(self, request, *args, **kwargs):
        the_form = SubmitLettersForm()
        context = {
            "title": 'New Game'
            , "form": the_form
        }
        return render(request, "darts/home.html", context)