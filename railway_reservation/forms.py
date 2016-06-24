# coding=utf-8
from django import forms
from .models import *
from captcha.fields import CaptchaField


class ReserveTicket(forms.Form):
    try:
        train_types = [(train.train_type_id, train.train_type_id) for train in Train.objects.all()]
        all_trains = zip(
            *[((train.origin, train.origin), (train.destination, train.destination)) for train in Train.objects.all()])
        origins = list(set(all_trains[0]))
        destinations = list(set(all_trains[1]))
    except:
        origins = []
        destinations = []
    try:
        choices = [(type.id, type.type) for type in TrainType.objects.all()]
    except Exception as ex:
        print(ex.message)
        choices = []
    origin = forms.ChoiceField(choices=origins, label=u'مبداء', required=True)
    destination = forms.ChoiceField(choices=destinations, label=u'مقصد', required=True)
    date = forms.CharField(widget=forms.TextInput(attrs={'class': 'datepicker'}), required=True, label=u'تاریخ حرکت')
    type = forms.ChoiceField(choices=choices, label=u'نوع قطار', required=True)


class UserLogin(forms.Form):
    user = forms.CharField(required=True, max_length=30, label=u'نام کاربری')
    password = forms.CharField(required=True, max_length=30, label=u'کلمه عبور', widget=forms.PasswordInput)


class UserRegister(forms.Form):
    uname = forms.CharField(max_length=30, min_length=4, required=True, label=u'نام کاربری',
                            widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    email = forms.EmailField(required=True, label=u'رایانامه', widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    fst_name = forms.CharField(max_length=30, min_length=4, required=True, label=u'نام',
                               widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    lst_name = forms.CharField(max_length=30, min_length=4, required=True, label=u'نام خانوادگی',
                               widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    fst_password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'off'}), required=True,
                                   label=u'کلمه عبور')
    scd_password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'off'}), required=True,
                                   label=u'تکرار کلمه عبور')
    captcha = CaptchaField(label=u'کد امنیتی')


class GetNumOfTickets(forms.Form):
    number_of_child = forms.IntegerField(label=u'تعداد خردسال', required=True, initial=0)
    number_of_adult = forms.IntegerField(label=u'تعداد بزرگسال', required=True, initial=0)


class EditProfile(forms.Form):  # profile edit!
    phone = forms.CharField(max_length=15, label=u'تلفن همراه', required=True)
    address = forms.CharField(max_length=200, label=u'آدرس', required=True)
    national_id = forms.CharField(max_length=12, label=u'شماره ملی', required=True)
    birth_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'datepicker'}), label=u'تاریخ تولد',
                                 required=True)
    gender = forms.ChoiceField(choices=[('m', u'مرد'), ('f', u'زن')], label=u'جنسیت', required=True)


class ContactUS(forms.Form):
    title = forms.CharField(max_length=100, label=u'عنوان پیام', required=True)
    email = forms.EmailField(label=u'رایانامه', required=True)
    question = forms.CharField(widget=forms.Textarea, label=u'متن پیام', required=True)
    captcha = CaptchaField(label=u'کد امنیتی', required=True)


class ChangePassword(forms.Form):
    email = forms.EmailField(label=u'ایمیل', required=True)
    user_name = forms.CharField(max_length=32, label=u'نام کاربری')
    old_pass = forms.CharField(max_length=32, widget=forms.PasswordInput, label=u'کلمه عبور فعلی')
    new_pass = forms.CharField(max_length=32, widget=forms.PasswordInput, label=u'کلمه عبور جدید')
    confirm_pass = forms.CharField(max_length=32, widget=forms.PasswordInput, label=u'تکرار کلمه عبور جدید')


class Credit(forms.Form):
    credit = forms.IntegerField(min_value=0, initial=0)
