from django.contrib import admin

from .models import Item, Bid
# Register your models here.

admin.site.register([Item, Bid])