# coding=utf-8
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.template import Context
from jdatetime import datetime
from .forms import *
from .models import *


def right_block(request, context):
    if request.method == "GET":
        context['register_form'] = UserRegister(None)
        context['login_form'] = UserLogin(None)
    else:
        if 'password' in request.POST:
            login_form = UserLogin(request.POST)
            if login_form.is_valid():
                username, password = login_form.cleaned_data['user'], login_form.cleaned_data['password']
                user = authenticate(username=username, password=password)
                if user is not None and user.is_active:
                    login(request, user)
                    HttpResponseRedirect('/profile')
                else:
                    context['register_form'] = UserRegister(None)
                    context['login_form'] = login_form
                    context['login_err'] = u'نام کاربری یا کلمه ی عبور نادرست میباشد.'
        elif 'fst_password' in request.POST:
            register_form = UserRegister(request.POST)
            if register_form.is_valid():
                username, email, password = register_form.cleaned_data['uname'], register_form.cleaned_data['email'], \
                                            register_form.cleaned_data['fst_password']
                try:
                    if register_form.cleaned_data['fst_password'] != register_form.cleaned_data['scd_password']:
                        context['register_form'] = UserRegister(request.POST)
                        context['login_form'] = UserLogin(None)
                        context['reg_err'] = u'کلمه عبور یکسان نیست'
                        return render(request, "home.html", context)
                    User.objects.get(username=username)
                    context['register_form'] = UserRegister(request.POST)
                    context['login_form'] = UserLogin(None)
                    context['reg_err'] = u'نام کاربری قبلا استفاده شده است.'
                except User.DoesNotExist:
                    user = User.objects.create_user(username, email, password)
                    user.first_name = register_form.cleaned_data['fst_name']
                    user.last_name = register_form.cleaned_data['lst_name']
                    user.save()
                    login(request, authenticate(username=username, password=password))
                    HttpResponseRedirect('/profile')
            else:
                context['register_form'] = UserRegister(request.POST)
                context['login_form'] = UserLogin(None)
        else:
            context['register_form'] = UserRegister(None)
            context['login_form'] = UserLogin(None)


def home(request):
    context = {'news': New.objects.all()[::-1], 'title': u'خانه'}
    right_block(request, context)
    return render(request, "home.html", context)


@login_required(login_url='/')
def ticket(request):
    context = {'result': None, 'title': u'خرید بلیط'}
    if request.method == "POST":
        if 'destination' in request.POST:
            context['num_of_tickets'] = GetNumOfTickets(None)
            form = ReserveTicket(request.POST)
            if form.is_valid():
                result = Train.objects.filter(origin=form.cleaned_data['origin'],
                                              destination=form.cleaned_data['destination'],
                                              date=form.cleaned_data['date'], train_type=form.cleaned_data['type'])
                context['result'] = result if result else 0
            else:
                context['result'] = 0
            context['reserve_ticket'] = form
        elif 'number_of_child' in request.POST:
            form = GetNumOfTickets(request.POST)
            if form.is_valid():
                train_id, num_ch, num_ad = int(request.POST['train_id']), int(
                    form.cleaned_data['number_of_child']), int(form.cleaned_data['number_of_adult'])
                try:
                    this_user = UserProfile.objects.get(user=request.user)
                    this_train = Train.objects.get(id=train_id)
                    reserved, last_seat, capacity = this_train.reserved, this_train.last_seat, this_train.capacity
                    if num_ch + num_ad + reserved > capacity:
                        context['reserve_error'] = u'تعداد بلیط درخواستی از تعداد بلیط های موجود بیشتر است'
                    elif (num_ad + int(round(num_ch / 2))) * this_train.price > this_user.credit:
                        context['reserve_error'] = u'موجودی حساب کافی نیست'
                        context['reserve_ticket'] = ReserveTicket(None)

                    else:
                        tmp = CancelledTickets.objects.filter(train_id=train_id, Len__gte=num_ad + num_ch).order_by(
                            'From')
                        if tmp:
                            ReservedTicket.objects.create(user=request.user, train=this_train, number_of_child=num_ch,
                                                          number_of_adult=num_ad, seat_number=tmp[0].From)
                            if tmp[0].Len == num_ch + num_ad:
                                CancelledTickets.objects.filter(id=tmp[0].id).delete()
                            else:
                                CancelledTickets.objects.filter(id=tmp[0].id).update(Len=tmp[0].Len - (num_ad + num_ch),
                                                                                     From=tmp[0].From + num_ch + num_ad)
                        else:
                            ReservedTicket.objects.create(user=request.user, train=this_train, number_of_child=num_ch,
                                                          number_of_adult=num_ad, seat_number=this_train.last_seat + 1)
                            Train.objects.filter(id=train_id).update(reserved=reserved + num_ch + num_ad,
                                                                     last_seat=last_seat + num_ch + num_ad)
                        this_user.credit = this_user.credit - (num_ad + int(round(num_ch / 2))) * this_train.price
                        this_user.save()
                        context['result'] = 1
                        context['reserve_ticket'] = ReserveTicket(None)

                except:
                    context['reserve_error'] = u'خطای ناشناخته!'
    else:
        try:
            UserProfile.objects.get(user=request.user)
            context['reserve_ticket'] = ReserveTicket(None)
            context['num_of_tickets'] = GetNumOfTickets(None)
            context['result'] = None
        except:
            context['reserve_error'] = u'برای رزرو بلیط لازم است اطلاعات حساب خود را تکمیل کنید.'

    return render(request, "ticket.html", context)


@login_required(login_url='/')
def profile(request):
    context = {'profile_data': {}, 'edit_form': '', 'title': u'پروفایل', 'questions': ''}

    def get_profile_data(context):
        context['profile_data'] = dict(context['profile_data'].items() + {'first name': request.user.first_name,
                                                                          'last name': request.user.last_name,
                                                                          'email': request.user.email}.items())
        try:
            user_profile = UserProfile.objects.get(user_id=request.user.id)
            context['profile_data'] = dict(
                context['profile_data'].items() + {field.name: field.value_to_string(user_profile) for field in
                                                   user_profile._meta.fields}.items())
        except:
            pass
        today = datetime.today()
        try:
            tickets = ReservedTicket.objects.filter(user_id=request.user.id,
                                                    train__date__gte="%s-%s-%s" % (today.year, today.month, today.day))
            context['tickets'] = tickets
        except:
            pass
        try:
            context['questions'] = Question.objects.filter(user_id=request.user.id, ans__gt='')
        except:
            pass

    if request.method == "GET":
        get_profile_data(context)
        context['edit_form'] = EditProfile(None)
    else:
        if 'cancel-ticket' in request.POST:
            ticket_id = int(request.POST['cancel-ticket'])  # ticket id
            tmp = ReservedTicket.objects.get(id=ticket_id)
            reserved = Train.objects.get(id=tmp.train_id).reserved
            ReservedTicket.objects.filter(id=ticket_id).delete()
            Train.objects.filter(id=tmp.train_id).update(
                reserved=reserved - (tmp.number_of_adult + tmp.number_of_child))
            CancelledTickets.objects.create(train_id=tmp.train_id, From=tmp.seat_number,
                                            Len=tmp.number_of_child + tmp.number_of_adult,user = request.user)
            get_profile_data(context)
            user = UserProfile.objects.get(user = request.user)
            user.credit += 2*tmp.train.price/3
            user.save()
            context['edit_form'] = EditProfile(None)
        elif 'birth_date' in request.POST:
            form = EditProfile(request.POST)
            if form.is_valid():
                phone, address, national_id, birth_date, gender = form.cleaned_data['phone'], form.cleaned_data[
                    'address'], form.cleaned_data['national_id'], form.cleaned_data['birth_date'], form.cleaned_data[
                                                                      'gender']
                try:
                    UserProfile.objects.get(user=request.user).update(phone=phone, address=address,
                                                                      national_id=national_id, birth_date=birth_date,
                                                                      gender=gender)
                except:
                    UserProfile.objects.create(user=request.user, phone=phone, address=address, national_id=national_id,
                                               birth_date=birth_date, gender=gender)

            context['edit_form'] = EditProfile(None)
            get_profile_data(context)
    return render(request, "profile.html", context)


def about(request):
    context = {'title': u'درباره ی ما'}
    right_block(request, context)
    return render(request, "about.html", context)


def contact(request):
    context, form = {'title': u'تماس با ما'}, 0
    right_block(request, context)
    if request.method == "GET":
        form = ContactUS(None)
    else:
        if 'title' in request.POST:
            form = ContactUS(request.POST)
            if form.is_valid():
                title = form.cleaned_data['title']
                question = form.cleaned_data['question']
                email = form.cleaned_data['email']
                Question.objects.create(user_id=request.user.id, title=title, email=email, question=question)

                context['message'] = u'ارسال شد'
                if not request.user.is_authenticated():
                    template = get_template('contact_template.txt')
                    context2 = Context({
                        'contact_name': title,
                        'contact_email': email,
                        'form_content': question,
                    })
                    content = template.render(context2)

                    email = EmailMessage(
                        "New contact form submission",
                        content,
                        "Your website" + '',
                        ['alirezaafzalaghaei@gmail.com'],
                        headers={'Reply-To': email}
                    )
                    email.send()
        else:
            form = ContactUS(None)
    context['form'] = form
    return render(request, "contact.html", context)


def news(request, dynamic_view_url):
    context = {'new_info': {}}
    right_block(request, context)
    try:
        new = New.objects.get(id=dynamic_view_url)
        context['new_info'] = {field.name: field.value_to_string(new) for field in new._meta.fields}
        context['new_info'].update(date=new.date)
        context['title'] = new.title
        New.objects.filter(id=dynamic_view_url).update(views=new.views + 1)
    except:
        context['title'] = u"خبر پیدا نشد!"
        context['not_found_error'] = u"خبر پیدا نشد!"

    return render(request, "news.html", context)


def password_change(request):
    context = {'title': u'ریست کردن پسورد'}
    right_block(request, context)
    if request.method == "GET":
        context['ch_pass'] = ChangePassword(None)
    else:
        if 'old_pass' in request.POST:
            form = ChangePassword(request.POST)
            if form.is_valid():
                if form.cleaned_data['new_pass'] != form.cleaned_data['confirm_pass']:
                    context['error'] = u'پسورد های جدید یکسان نیست'
                else:
                    try:
                        user = User.objects.get(username=form.cleaned_data['user_name'],
                                                email=form.cleaned_data['email'])
                        if user.check_password(form.cleaned_data['old_pass']):
                            user.set_password(form.cleaned_data['new_pass'])
                            user.save()
                            context['ch_pass'] = ChangePassword(request.POST)
                            context['error'] = u'کلمه عبور با موفقیت تغییر یافت'
                        else:
                            context['error'] = u'کلمه ی عبور وارد شده صحیح نیست'
                            context['ch_pass'] = ChangePassword(request.POST)
                    except Exception as ex:
                        context['error'] = u'چنین کاربری یافت نشد'
        else:
            context['ch_pass'] = ChangePassword(None)
    return render(request, "change_password.html", context)


@login_required(login_url='/')
def increase_credit(request):
    context = {'title': u'افزایش اعتبار'}
    if request.method == "GET":
        try:
            user = UserProfile.objects.get(user=request.user)
            context['error'] = u'موجودی فعلی = ' + str(user.credit)
        except:
            context['error'] = u'برای افزایش اعتبار لازم است اطلاعات پروفایل خود را تکمیل کید.'
            return render(request, "increase_credit.html", context)
        context['form'] = Credit(None)
    else:
        form = Credit(request.POST)
        if form.is_valid():
            user = UserProfile.objects.get(user=request.user)
            user.credit += int(form.cleaned_data['credit'])
            user.save()
            context['error'] = u'موجودی فعلی = ' + str(user.credit)
            context['form'] = Credit(None)
        else:
            context['error'] = u'خطایی رخ داد!'
    right_block(request, context)

    return render(request, "increase_credit.html", context)
