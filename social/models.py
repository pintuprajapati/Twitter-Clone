from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Post model
class Post(models.Model):
    body = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, blank=True, related_name="likes")
    dislikes = models.ManyToManyField(User, blank=True, related_name="dislikes")
    
    # get the item according to params
    @staticmethod
    def get_post_data(filter_type, filter_by=None):
        if filter_type == "filter":
            return Post.objects.filter(author=filter_by).order_by('-created_on') #ordered by latest date
        elif filter_type == "get":
            return Post.objects.get(id=filter_by)
        elif filter_type == "all":
            return Post.objects.all().order_by('-created_on')
        else: 
            raise Exception("not valid input")

# Comment model
class Comment(models.Model):
    comment = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

# User Profile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, verbose_name='user', related_name='profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=30, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    picture = models.ImageField(upload_to='uploads/profile_pictures', default='uploads/profile_pictures/blank-profile-picture.png', blank=True)
    followers = models.ManyToManyField(User, blank=True, related_name='followers')

    # We will use "signals" to save the userInfo into UserProfile every time it's saved
    # sender - User
    # receiver - decorator(@receiver)
    # instanct - User object being saved
    # created - true/false

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Creates user, doesn't save it to the DB
    if created:
        UserProfile.objects.create(user=instance) # Here instance means "user object - the sender"

@receiver(post_save, sender=User)
def save_user_prfoile(sender, instance, **kwargs):
    instance.profile.save() # instance is actual model that saved in database

 