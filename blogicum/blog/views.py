from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    DeleteView, CreateView, ListView, UpdateView
)
from django.urls import reverse, reverse_lazy

from .const_for_blog import CONST_PAGINATE
from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Post
from .mixins import OnlyAuthorMixin, PostMixin, CommentMixin

User = get_user_model()


class BlogListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = CONST_PAGINATE
    queryset = Post.objects.published().count_comment()


class Profile(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = CONST_PAGINATE

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        author = self.get_author()
        posts = author.posts.count_comment()
        if self.request.user != author:
            return posts.published()
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        return context


def profile_update(request):
    form = ProfileForm(
        request.POST or None,
        instance=get_object_or_404(
            User,
            username=request.user.username
        )
    )
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user.username)
    return render(
        request,
        'blog/user.html',
        context={'form': form}
    )


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str: 
        return reverse('blog:profile', args=[self.request.user.username])


class PostUpdate(PostMixin, UpdateView):

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', args=[self.object.id])


class PostDelete(PostMixin, OnlyAuthorMixin, DeleteView):
    pass


class PostDetail(ListView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'comments'
    pk_url_kwarg = 'post_id'
    paginate_by = CONST_PAGINATE

    def get_object(self):
        return get_object_or_404(Post, pk=self.kwargs['post_id'])

    def get_queryset(self) -> QuerySet[Any]:
        return self.get_object().comments.select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        if self.request.user != post.author:
            queryset = Post.objects.published()
            post = get_object_or_404(queryset, pk=self.kwargs['post_id'])
        context['post'] = post
        context['form'] = CommentForm()
        return context


class CommentCreate(CommentMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdate(CommentMixin, OnlyAuthorMixin, UpdateView):
    pass


class CommentDelete(CommentMixin, OnlyAuthorMixin, DeleteView):
    pass
    # def get_context_data(self, **kwargs):
    #     context = None
    #     return context


class CategoryList(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = CONST_PAGINATE

    def get_object(self):
        return get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['category_slug']
        )

    def get_queryset(self):
        return self.get_object().posts.published().count_comment()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object()
        return context


class RegistrationCreate(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')
