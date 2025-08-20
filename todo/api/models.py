from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Todo_list(models.Model):
    srno =models.AutoField(primary_key=True, auto_created=True)
    title = models.CharField(max_length=25)
    favorite = models.BooleanField(default=False)
    start_date =models.DateTimeField()
    expirity_date = models.DateTimeField()
    user= models.ForeignKey(User,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title