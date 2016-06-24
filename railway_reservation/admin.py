from django.contrib import admin
from .models import *
from django_jalali.admin.filters import JDateFieldListFilter
import django_jalali.admin as jadmin


class NewsAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "title", "date"]
    list_filter = (
        ('date', JDateFieldListFilter),
    )
    exclude = ('views',)

    class Meta:
        model = New


class TrainAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "degree", "date", 'time', 'capacity', 'reserved', 'train_number', 'train_title',
                    'train_type', 'price']
    exclude = ('reserved', 'last_seat',)
    list_filter = (
        ('date', JDateFieldListFilter),
        ('time', JDateFieldListFilter),
    )

    class Meta:
        model = Train


class UserProfiles(admin.ModelAdmin):
    list_display = ["__unicode__", "national_id", "gender", "credit", "username", "first_name", "last_name", "email"]
    readonly_fields = ['email', 'username', 'first_name', 'last_name']

    def username(self, obj):
        return obj.user.username

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    def email(self, obj):
        return obj.user.email

    class Meta:
        model = UserProfile


class Types(admin.ModelAdmin):
    class Meta:
        model = TrainType


class ContactAdmin(admin.ModelAdmin):
    class Meta:
        model = Question


class ReservedAdmin(admin.ModelAdmin):
    list_display = ['__unicode__','username','number_of_child', 'number_of_adult']
    class Meta:
        model = ReservedTicket

admin.site.register(New, NewsAdmin)
admin.site.register(Train, TrainAdmin)
admin.site.register(UserProfile, UserProfiles)
admin.site.register(TrainType, Types)
admin.site.register(Question,ContactAdmin)
admin.site.register(ReservedTicket,ReservedAdmin)