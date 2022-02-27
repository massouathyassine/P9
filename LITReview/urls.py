"""LITReview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import ReviewApp.views
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeView,
                                       PasswordChangeDoneView)
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(template_name='review/login.html',
                               redirect_authenticated_user=True),
         name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('home/', ReviewApp.views.home, name='home'),
    path('signup/', ReviewApp.views.signup, name='signup'),
    path('posts/', ReviewApp.views.posts, name='posts'),
    path('subs/', ReviewApp.views.subs, name='subs'),
    path('create_ticket/', ReviewApp.views.create_ticket, name='create_ticket'),
    path('create_review/', ReviewApp.views.create_review, name='create_review'),
    path('ticket_response/<int:ticket_id>/', ReviewApp.views.ticket_response,
         name='ticket_response'),
    path('delete_sub/<int:sub_id>/', ReviewApp.views.delete_sub,
         name='delete_sub'),
    path('edit_ticket/<int:ticket_id>/', ReviewApp.views.edit_ticket,
         name='edit_ticket'),
    path('delete_ticket/<int:ticket_id>/', ReviewApp.views.delete_ticket,
         name='delete_ticket'),
    path('edit_review/<int:review_id>/', ReviewApp.views.edit_review,
         name='edit_review'),
    path('delete_review/<int:review_id>/', ReviewApp.views.delete_review,
         name='delete_review'),
    path('account/', ReviewApp.views.account, name='account'),
    path('change_password/', PasswordChangeView.as_view(
        template_name='review/password_change.html'), name='password_change'),
    path('change_password_done/', PasswordChangeDoneView.as_view(
        template_name='review/password_change_done.html'),
         name='password_change_done'),
    path('delete_account/', ReviewApp.views.delete_account,
         name='delete_account'),
    path('delete_account_confirm/', ReviewApp.views.delete_account_confirm,
         name='delete_account_confirm'),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
