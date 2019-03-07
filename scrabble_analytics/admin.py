from django.contrib import admin
from scrabble_analytics.models import Words, WordsSet, SavedSearchParameters, SavedSearchResults
# Register your models here.
admin.site.register(WordsSet)
admin.site.register(Words)
admin.site.register(SavedSearchParameters)
admin.site.register(SavedSearchResults)
