from django.urls import path
from .views import my_profile_view, invite_received_view, accounts_list_view, invite_accounts_list_view

app_name = 'profile'

urlpatterns = [
    path('', my_profile_view, name='my-profile-view'),
    path('invites/', invite_received_view, name='invites-view'),
    path('all-profile/', accounts_list_view, name='all-profile-view'),
    path('to-invite/', invite_accounts_list_view, name='invite-profiles-view')
]
