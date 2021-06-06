from django.db import models
from django.contrib.auth.models import User
from .utils import get_random_code
from django.template.defaultfilters import slugify 
from posts.models import *
from django.db.models import Q


class AccountManager(models.Manager):

    def get_all_accounts_to_invite(self, sender):
        accounts = Account.objects.all().exclude(user=sender)
        account = Account.objects.get(user=sender)
        queryset = Relationship.objects.filter(Q(sender=account) | Q(receiver=account))
        print(queryset)
        print('#################################')

        accepted = set([])
        for relationship in queryset:
            if relationship.status == 'accepted':
                accepted.add(relationship.receiver)
                accepted.add(relationship.sender)
        print(accepted)
        print('#################################')

        available = [account for account in accounts if account not in accepted]
        print(available)
        print('##################################')
        return available


    def get_all_accounts(self, me):
        accounts = Account.objects.all().exclude(user=me)
        return accounts


class Account(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="no bio..", max_length=300)
    email = models.EmailField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(default='avatar.png', upload_to='')
    friends = models.ManyToManyField(User, blank=True, related_name='friends')
    slug = models.SlugField(unique=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = AccountManager()

    def get_friends(self):
        return self.friends.all()

    def get_friends_no(self):
        return self.friends.all().count()

    def get_post_no(self):
        return self.author_posts.all().count()

    def get_likes_given_no(self):
        likes = self.like_set.all()
        total_liked = 0

        for item in likes:
            if item.value == 'Like':
                total_liked += 1
            return total_liked

    def get_likes_received_no(self):
        posts = self.author_posts.all()
        total_liked = 0

        for item in posts:
            total_liked += item.liked.all().count()
        return total_liked

    def __str__(self):
        return str(self.user)

    def get_all_authors_posts(self):
        return self.author_posts.all()

    def save(self, *args, **kwargs):
        ex = False
        if self.first_name and self.last_name:
            to_slug = slugify(str(self.first_name) + " " + str(self.last_name))
            ex = Account.objects.filter(slug=to_slug).exists()
            while ex:
                to_slug = slugify(to_slug + " " + str(get_random_code()))
                ex = Account.objects.filter(slug=to_slug).exists()

        else:
            to_slug = str(self.user)
        
        self.slug = to_slug
        super().save(*args, **kwargs)


STATUS_CHOICES = (
    ('send', 'send'),
    ('accepted', 'accepted')
)


class RelationshipManager(models.Manager):
    def invitation_received(self, receiver):
        queryset = Relationship.objects.filter(receiver=receiver, status='send')
        return queryset

class Relationship(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add = True)

    objects = RelationshipManager()

    def __str__(self):
        return f"{self.sender} - {self.receiver} - {self.status}"

