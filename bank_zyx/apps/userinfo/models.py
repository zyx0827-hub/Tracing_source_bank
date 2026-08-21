from django.db import models

# Create your models here.
class UserInfo(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    pid = models.CharField(unique=True, max_length=18)
    telephone = models.CharField(unique=True, max_length=20)
    address = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'user_info'