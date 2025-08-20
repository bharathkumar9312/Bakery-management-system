from django.db import models
from django.contrib.auth.models import User
import datetime
import os

def getFileName(request,filename):
    now_time=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename="%s%s"%(now_time,filename)
    return os.path.join("uploads/",new_filename)

# for category table
class Category(models.Model):
    name=models.CharField(max_length=150,null=False,blank=False)
    image=models.ImageField(upload_to=getFileName,null=False,blank=False)
    status=models.BooleanField(default=False,help_text="0-show,1-Hidden")
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    

# for product Table   
class Product(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    name=models.CharField(max_length=150,null=False,blank=False)
    product_image=models.ImageField(upload_to=getFileName,null=False,blank=False)
    
    original_price=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Original Price (General)")
    selling_price=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Selling Price (General)")
    
    # Cake prices
    price_half_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Price (0.5 Kg)")
    price_one_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Price (1 Kg)")
    
    # New fields for Milkshake/Pizza prices
    price_small = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Price (Small)")
    price_medium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Price (Medium)")
    price_large = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Price (Large)")

    
    status=models.BooleanField(default=False,help_text="0-show,1-Hidden")
    trending=models.BooleanField(default=False,help_text="0-default,1-Hidden")
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

