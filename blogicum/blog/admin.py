from django.contrib import admin
from .models import Category, Post, Location


class PostAdmin(admin.ModelAdmin):
    model = Post


class LocationAdmin(admin.ModelAdmin):
    model = Location


class CategoryAdmin(admin.ModelAdmin):
    model = Category


admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Location)
