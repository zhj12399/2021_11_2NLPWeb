from django.db import models


# Create your models here.
class Record(models.Model):
    time = models.DateTimeField(verbose_name='time')
    chinese = models.CharField(max_length=100,verbose_name='chinese')
    english = models.CharField(max_length=100,verbose_name='english')
    chinese_pri = models.CharField(max_length=100,verbose_name='chinese_pri')
    answer = models.CharField(max_length=100,verbose_name='answer')

    class Meta:
        db_table='nlp_record'
        verbose_name = 'nlp_record'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.chinese_pri+self.english+self.answer
