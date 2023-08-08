from django.contrib.auth.models import User
from django.db import models

class MedReport(models.Model):
    patient_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    fullname = models.CharField("Enter Full Name", max_length=50)
    email = models.EmailField("Enter Email")
    phone = models.CharField("Enter Phone Number", max_length=10)
    gender = models.CharField("Enter Gender", max_length=10)
    age = models.IntegerField("Enter Age")
    img = models.ImageField(upload_to="images/")
    test_type = models.CharField("Test Type", max_length=50)
    results = models.CharField("Prediction Results", max_length=50)

    def __str__(self):
        return self.fullname