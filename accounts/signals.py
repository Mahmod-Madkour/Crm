from .models import Customer
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # add new user to 'customer' Group
        # instance == user
        group = Group.objects.get(name='customer')
        instance.groups.add(group)

        # add new user to Customer table
        Customer.objects.create(user=instance, name=instance.username)

post_save.connect(create_profile, sender=User)
