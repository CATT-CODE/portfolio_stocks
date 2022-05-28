from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Account(models.Model):

	# user = models.OneToOneField(User, on_delete=models.CASCADE)

	def generate_account_num():
		not_unique = True
		while not_unique:
			unique_num = get_random_string(8, allowed_chars='0123456789')
			if not Account.objects.filter(id=unique_num):
				not_unique = False
		return str(unique_num)

	id = models.CharField(max_length=8, blank=True, editable=False, unique=True, primary_key=True, default=generate_account_num)
	username = models.CharField(max_length=20, unique=True)
	password = models.CharField(max_length=20)
	firstName = models.CharField(max_length=20)
	lastName = models.CharField(max_length=20)
	cashBalance = models.FloatField(default=50000.0)
	overallValue = models.FloatField(default=0.0)

	def __str__(self):
		return self.id


class Transaction(models.Model):
	timeDate = models.DateTimeField()
	symbol = models.CharField(max_length=10)
	shares = models.FloatField()
	buyOrSell = models.CharField(max_length=1, choices=[('B','Buy'), ('S','Sell')])
	cashPrice = models.FloatField()
	account = models.ForeignKey(Account, on_delete=models.CASCADE)

class Positions(models.Model):
	symbol = models.CharField(max_length=10)
	shares = models.FloatField()
	avgPricePerShare = models.FloatField()
	currentValue = models.FloatField(default=0.0)
	account = models.ForeignKey(Account, on_delete=models.CASCADE)

# @receiver(post_save, sender=User)
# def create_user_account(sender, instance, created, **kwargs):
#     if created:
#         Account.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_accouprofile(sender, instance, **kwargs):
#     instance.profile.save()
