from django.shortcuts import render, redirect
from .models import *
from profiles.models import Account
from .forms import PostModelForm, CommentModelForm
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages


def post_comment_create_and_list_view(request):
    qs = Post.objects.all()
    account = Account.objects.get(user=request.user)

    post_form = PostModelForm()
    comment_form = CommentModelForm()
    post_add = False

    if 'submit_post_form' in request.POST:
        print(request.POST)
        post_form = PostModelForm(request.POST, request.FILES)
        account = Account.objects.get(user=request.user)
        if post_form.is_valid():
            instance = post_form.save(commit=False)
            instance.author = account
            instance.save()

            post_form = PostModelForm()
            post_add = True
            return redirect('posts:main-post-view')

    if 'submit_comment_form' in request.POST:
        comment_form = CommentModelForm(request.POST)
        if comment_form.is_valid():
            instance = comment_form.save(commit=False)
            instance.user = account
            instance.post = Post.objects.get(id = request.POST.get('post_id'))
            instance.save()

            comment_form = CommentModelForm()
            return redirect('posts:main-post-view')



    context = {
        'qs': qs,
        'account': account,
        'post_form': post_form,
        'comment_form': comment_form,
        'post_added': post_add,
    }
    return render(request, 'posts/main.html', context)


def like_unlike_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        account = Account.objects.get(user=user)

        if account in post_obj.liked.all():
            post_obj.liked.remove(account)
        else:
            post_obj.liked.add(account)

        like, created = Like.objects.get_or_create(user=account, post_id=post_id)

        if not created:
            if like.value == 'Like':
                like.value= 'Unlike'
            else:
                like.value='Like'
        else:
            like.value = 'Like'

        post_obj.save()
        like.save()

        return redirect('posts:main-post-view')



class PostDeleteView(DeleteView):
    model = Post
    template_name = 'posts/confirm_delete.html'
    success_url = reverse_lazy('posts:main-post-view')

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        post = Post.objects.get(pk=pk)
        if not post.author.user == self.request.user:
            messages.warning(self.request, 'You need to be the author of the post inorder to delete it')
        return post


class PostUpdateView(UpdateView):
    form_class = PostModelForm
    model = Post
    template_name = 'posts/update.html'
    success_url = reverse_lazy('posts:main-post-view')

    def form_valid(self, form):
        account = Account.objects.get(user=self.request.user)
        if form.instance.author == account:
            return super().form_valid(form)
        else:
            form.add_error(None, 'You need to be an author to update the post')
            return super().form_invalid(form)