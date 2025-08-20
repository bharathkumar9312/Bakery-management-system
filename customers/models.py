from django.db import models

# for customers Details
class Customers(models.Model):
    name=models.CharField(max_length=150,null=True,blank=True)
    Phone_number=models.CharField(max_length=15,null=True,blank=True)
    Address=models.TextField(max_length=150,null=True,blank=True)

    def __str__(self):
        return self.name
