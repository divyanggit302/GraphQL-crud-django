from django.db import models

# model

# City Model
class City(models.Model):
    id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=255,null=False,blank=False,unique=True)

    def __str__(self):
        return f'{self.id}, {self.city}'


#Component Model
class Component(models.Model):
    id = models.AutoField(primary_key=True)
    company = models.CharField(max_length=255,unique=True)
    description = models.CharField(max_length=255)
    city = models.ManyToManyField(City,related_name='componentid')


    def __str__(self):
        return f'{self.id}, {self.company}, {self.description}, {self.city}'