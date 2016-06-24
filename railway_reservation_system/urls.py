from django.conf.urls import include, url
from django.contrib import admin
import railway_reservation.views as site
import django.contrib.auth.views

urlpatterns = [
    url(r'^$', site.home, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/logout/$', django.contrib.auth.views.logout, {'next_page': '/'}),
    url('^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/ticket/$', site.ticket, name='ticket'),
    url(r'^accounts/profile/$', site.profile, name='profile'),
    url(r'^about/$', site.about, name='about'),
    url(r'^contact/$', site.contact, name='contact'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^news/(\d+)/$',site.news,name='news-link'),
    url(r'^accounts/reset_password/$',site.password_change,name='change_password'),
    url(r'^accounts/credit/$',site.increase_credit,name='increase_credit')
]

