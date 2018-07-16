from django.db import models
from scrabble_analytics.toolbox import get_score

# Create your models here.
class Words(models.Model):
    Word_name = models.CharField(max_length = 20)
    Length   = models.IntegerField()
    Score    = models.IntegerField()
    
    def __str__(self):
        return str(self.Word_name) + ' Length: ' + str(self.Length) + ' Score: ' + str(self.Score)

    def __unicode__(self): #used fr python2
        return str(self.Word_name) + ' Length: ' + str(self.Length) + ' Score: ' + str(self.Score)

    def save(self, *args, **kwargs):
        if self.Length == None:
            self.Length = len(self.Word_name)
        if self.Score == None:
            self.Score = get_score(self.Word_name)
        super(Words, self).save(*args, **kwargs)
