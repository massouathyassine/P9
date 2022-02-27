from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from itertools import chain
from django.core.paginator import Paginator
from . import forms, models


def default(request):
    """
    View for the default page of the app, where user can signup or log in
    :param request: HTTP request
    :return: either the home fedd of the user, or the register page
    """
    form = forms.SignUpForm()

    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            # auto-login user
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)

    return render(request, 'review/login.html', {'form': form})


@login_required
def home(request):
    """
    View for the user's home feed
    :param request: HTTP request
    :return: user's home feed
    """
    if models.UserFollows.objects.filter(user=request.user):
        own_tickets = models.Ticket.objects.filter(user=request.user)
        # getting followed users' tickets
        follow_tickets = models.Ticket.objects.filter(
            user__in=models.UserFollows.objects.filter(
                user=request.user).values_list('followed_user'))

        own_reviews = models.Review.objects.filter(user=request.user)
        # getting followed users' ReviewApp
        follow_reviews = models.Review.objects.filter(
            user__in=models.UserFollows.objects.filter(
                user=request.user).values_list('followed_user'))

        # getting user tickets' response even if the person who answered is not
        # follow by user
        other_reviews = models.Review.objects.filter(
            ticket__user=request.user).difference(own_reviews, follow_reviews)

        tickets_and_reviews = sorted(
            chain(own_tickets, follow_tickets, own_reviews, follow_reviews,
                  other_reviews), key=lambda element: element.time_created,
            reverse=True)
    else:
        tickets = models.Ticket.objects.all()
        reviews = models.Review.objects.all()
        tickets_and_reviews = sorted(chain(tickets, reviews),
                                     key=lambda element: element.time_created,
                                     reverse=True)

    paginator = Paginator(tickets_and_reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'instances': page_obj}
    return render(request, 'review/home.html', context)


def signup(request):
    """
    signup page
    :param request: hTTP request
    :return: home page if registration is correct, or load itself if it fails
    """
    form = forms.SignUpForm()

    if request.method == 'POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # auto-loging user
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)

    context = {'form': form}

    return render(request, 'review/signup.html', context)


@login_required
def posts(request):
    """
    user's posts page
    :param request: HTTP request
    :return: user's posts
    """
    tickets = models.Ticket.objects.filter(user=request.user)
    reviews = models.Review.objects.filter(user=request.user)
    tickets_and_reviews = sorted(chain(tickets, reviews),
                                 key=lambda element: element.time_created,
                                 reverse=True)
    paginator = Paginator(tickets_and_reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'instances': page_obj, 'own_post': True}
    return render(request, 'review/posts.html', context)


@login_required
def subs(request):
    """
    user's follow page, with followed users and followers
    :param request: HTTP request
    :return: follow page
    """
    context = {}
    main_user = models.UserFollows()

    if models.UserFollows.objects.filter(user=request.user):
        context['followed'] = models.UserFollows.objects.filter(
            user=request.user)

    if models.UserFollows.objects.filter(followed_user=request.user):
        context['following'] = models.UserFollows.objects.filter(
            followed_user=request.user)

    if request.method == 'POST':
        searched_user = request.POST.get('username')
        try:
            followed_user = User.objects.get(username=searched_user)
            main_user.followed_user = followed_user
            main_user.user = request.user
            main_user.save()
            return redirect('subs')
        except User.DoesNotExist:
            context['error'] = 'Aucun utilisateurs trouvé !'
            return render(request, 'review/subs.html', context)

    return render(request, 'review/subs.html', context)


@login_required
def delete_sub(request, sub_id):
    """
    function for stop following an user
    :param request: HTTP request
    :param sub_id: if of the UserFollow entry
    :return: reload the subs page
    """
    sub = models.UserFollows.objects.get(id=sub_id)
    sub.delete()
    return redirect('subs')


@login_required
def create_ticket(request):
    """
    view for creating a ticket
    :param request: HTTP request
    :return: a TicketForm page, or user's home feed
    """
    ticket_form = forms.TicketForm()
    if request.method == 'POST':
        ticket_form = forms.TicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('home')

    context = {'ticket_form': ticket_form}
    return render(request, 'review/create_ticket.html', context)


@login_required
def create_review(request):
    """
    view for create a ReviewApp
    :param request: HTTP request
    :return: a ReviewForm page, or user's home feed
    """
    ticket_form = forms.TicketForm()
    review_form = forms.ReviewForm()
    if request.method == 'POST':
        ticket_form = forms.TicketForm(request.POST, request.FILES)
        review_form = forms.ReviewForm(request.POST)
        if all([ticket_form.is_valid(), review_form.is_valid()]):
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.reviewed = True
            ticket.save()
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect('home')
    context = {'ticket_form': ticket_form, 'review_form': review_form}
    return render(request, 'review/create_review.html', context)


@login_required
def ticket_response(request, ticket_id):
    """
    view for creating a ticket response
    :param request: HTTP request
    :param ticket_id: id of the ticket
    :return: a ReviewForm or the user's home feed
    """
    ticket = get_object_or_404(models.Ticket, id=ticket_id)
    review_form = forms.ReviewForm()
    if request.method == 'POST':
        review_form = forms.ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            ticket.reviewed = True
            ticket.save()
        return redirect('home')
    context = {'ticket': ticket, 'review_form': review_form, 'response': True}
    return render(request, 'review/ticket_response.html', context)


@login_required
def edit_ticket(request, ticket_id):
    """
    view for editing a ticket
    :param request: HTTP request
    :param ticket_id: ticket's id
    :return: a TicketForm or the user's posts page
    """
    ticket = models.Ticket.objects.get(id=ticket_id)
    edit_form = forms.TicketForm(instance=ticket)

    if request.method == 'POST':
        edit_form = forms.TicketForm(request.POST, instance=ticket)
        if edit_form.is_valid():
            edit_form.save()
            return redirect('posts')

    context = {'ticket_form': edit_form}

    return render(request, 'review/create_ticket.html', context)


@login_required
def delete_ticket(request, ticket_id):
    """
    function for deleting a ticket
    :param request: HTTP request
    :param ticket_id: ticket's id
    :return: user's posts page
    """
    ticket = models.Ticket.objects.get(id=ticket_id)
    ticket.delete()
    return redirect('posts')


@login_required
def edit_review(request, review_id):
    """
    View for editing a ReviewApp
    :param request: HTTP request
    :param review_id: reviews's id
    :return: a ReviewForm page, or user's posts page
    """
    review = get_object_or_404(models.Review, id=review_id)
    edit_form = forms.ReviewForm(instance=review)
    ticket = get_object_or_404(models.Ticket, id=review.ticket.id)

    if request.method == 'POST':
        edit_form = forms.ReviewForm(request.POST, instance=review)
        if edit_form.is_valid():
            edit_form.save()
            return redirect('posts')

    context = {'review_form': edit_form, 'ticket': ticket}
    return render(request, 'review/ticket_response.html', context)


@login_required
def delete_review(request, review_id):
    """
    function for deleting a ReviewApp
    :param request: HTTP request
    :param review_id: ReviewApp's id
    :return: user's posts page
    """
    review = models.Review.objects.get(id=review_id)
    review.ticket.reviewed = False
    review.ticket.save()
    review.delete()
    return redirect('posts')


@login_required
def account(request, ):
    """
    view of user's account
    :param request: HTTP request
    :return: user's account page
    """
    return render(request, 'review/account.html')


@login_required
def delete_account(request):
    """
    view for confirming the user's account deletion
    :param request: HTTP request
    :return: confirmation page
    """
    return render(request, 'review/delete_user.html')


@login_required
def delete_account_confirm(request):
    """
    function that delete user's account
    :param request: HTTP request
    :return: logout page
    """
    user = request.user
    user.delete()
    return redirect('logout')
