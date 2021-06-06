from django.shortcuts import render
from .models import Account, Relationship
from .forms import AccountModelForm

def my_profile_view(request):
    account = Account.objects.get(user=request.user)
    form = AccountModelForm(request.POST or None, request.FILES or None, instance=account)
    confirm = False

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            comfirm = True
 
    context = {
        'account': account,
        'form': form,
        'confirm': confirm,
    }
    return render(request, 'profiles/myprofile.html', context)


def invite_received_view(request):
    account = Account.objects.get(user=request.user)
    queryset = Relationship.objects.invitation_received(account)

    context = {
        'queryset': queryset
    }

    return render(request, 'profiles/invites.html', context)


def accounts_list_view(request):
    user = request.user
    queryset = Account.objects.get_all_accounts(user)

    context = {
        'queryset': queryset
    }

    return render(request, 'profiles/profile_list.html', context)


def invite_accounts_list_view(request):
    user = request.user
    queryset = Account.objects.get_all_accounts_to_invite(user)

    context = {
        'queryset': queryset
    }

    return render(request, 'profiles/to_invite_list.html', context)