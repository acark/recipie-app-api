
"""
 Database modals
"""
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


#admin@example.com
#admin123
#admin12345
class UserManager(BaseUserManager):
    """Manager for users"""
    def create_user(self, email, password=None, **extra_fields):
        """create , save and return a new user"""

        if not email:
            raise ValueError("User must have an email address!")
        # self.model is the user model, here we create an instance of the user model
        user = self.model(email=self.normalize_email(email) , **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """create and return new superuser"""

        user = self.create_user(email , password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """user in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default= False)

    objects = UserManager()
    #we change the default authentication field with custom email field
    USERNAME_FIELD = "email"


class Recipe(models.Model):
    """recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link= models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title