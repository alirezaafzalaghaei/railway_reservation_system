from django.contrib.auth.models import User
from django.db import models
from django_jalali.db import models as jmodels


class New(models.Model):
    objects = jmodels.jManager()
    title = models.CharField(max_length=120)
    date = jmodels.jDateField()
    text = models.TextField()
    views = models.IntegerField(default=1)

    def __unicode__(self):
        return self.title


class TrainType(models.Model):
    type = models.CharField(max_length=30)

    def __unicode__(self):
        return self.type


class Train(models.Model):
    objects = jmodels.jManager()
    train_type = models.OneToOneField(TrainType)
    origin = models.CharField(max_length=60, default='')
    destination = models.CharField(max_length=60, default='')
    train_title = models.CharField(max_length=60, default='')
    train_number = models.CharField(max_length=5, default='', unique=True)
    degree = models.CharField(max_length=2, default='')
    date = jmodels.jDateField()
    time = models.TimeField()
    capacity = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)
    last_seat = models.IntegerField(default=0)
    number_of_wagons = models.IntegerField(default=0)
    number_of_coupe_per_wagon = models.IntegerField(default=0)
    price = models.IntegerField(default=0)

    def __unicode__(self):
        return self.origin + ' - ' + self.destination


class ReservedTicket(models.Model):
    objects = jmodels.jManager()
    user = models.ForeignKey(User)
    train = models.ForeignKey(Train)
    number_of_child = models.IntegerField(default=0)
    number_of_adult = models.IntegerField(default=0)
    seat_number = models.IntegerField()
    reserve_time = jmodels.jDateTimeField(auto_now=True)

    def __unicode__(self):
        return self.train.__unicode__()

    def username(self):
        return self.user.username


class Question(models.Model):
    objects = jmodels.jManager()
    user = models.ForeignKey(User,blank=True,null=True)
    title = models.CharField(max_length=100)
    email = models.EmailField()
    question = models.TextField()
    date = jmodels.jDateField(auto_now=True)
    ans = models.TextField(blank=True,null=True)

    def __unicode__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    credit = models.IntegerField(default=0)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=250)
    national_id = models.CharField(max_length=15)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1)
    special = models.CharField(max_length=1)

    def __unicode__(self):
        return self.user.username


class CancelledTickets(models.Model):
    user = models.ForeignKey(User)
    train = models.ForeignKey(Train)
    From = models.IntegerField()
    Len = models.IntegerField()
