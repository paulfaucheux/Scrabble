from django.db import models
from scrabble_analytics.toolbox import get_score

# Create your models here.

class WordsSet(models.Model):
    Wordset_name = models.CharField(max_length = 20)

class Words(models.Model):
    Word_name = models.CharField(max_length = 20)
    Length = models.IntegerField()
    Score = models.IntegerField()
    Word_set = models.ForeignKey(WordsSet, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.Word_name) + ' Length: ' + str(self.Length) + ' Score: ' + str(self.Score)

    def __unicode__(self): #used fr python2
        return str(self.Word_name) + ' Length: ' + str(self.Length) + ' Score: ' + str(self.Score)

    def save(self, *args, **kwargs):
        if self.Length is None:
            self.Length = len(self.Word_name)
        if self.Score is None:
            self.Score = get_score(self.Word_name)
        super(Words, self).save(*args, **kwargs)

class SavedSearchParameters(models.Model):
    Letters_list = models.CharField(max_length = 20)
    Created_date = models.DateTimeField(auto_now_add=True)

    #def delete_everything(self):
    #    SavedSearchParameters.objects.all().delete()

class SavedSearchResults(models.Model):
    Word_name = models.CharField(max_length = 20)
    Missing = models.CharField(max_length = 20)
    Length = models.IntegerField()
    Score = models.IntegerField()
    Pksearch = models.ForeignKey(SavedSearchParameters, on_delete=models.CASCADE)

    #def delete_everything(self):
    #    SavedSearchResults.objects.all().delete()
