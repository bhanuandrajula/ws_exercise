from django.db import models


# Create your models here.
from django.urls import reverse


class adset(models.Model):
    title = models.CharField(max_length=120)
    author = models.TextField(blank=False,null =False)
    price = models.DecimalField(max_digits=1000, decimal_places=2)
    summary = models.TextField()
    addedfield = models.BooleanField(default=True) # added new filed so we should add default value while make migrations or add values blank=True,null =True

    def get_absolute_url(self):
        #return f"/products/{self.id}"
        return reverse("products:product-detail",kwargs={"my_id":self.id})

# Create your models here.

