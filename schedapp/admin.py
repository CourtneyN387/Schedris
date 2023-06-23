from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Schedule)
admin.site.register(Other_Course)
admin.site.register(Course)
admin.site.register(ShoppingCart)