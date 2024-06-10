from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.generic import (
    DeleteView, DetailView, CreateView, ListView, UpdateView
)
from django.urls import reverse

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post


User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


def filter_posts(query):
    return query.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=now()
    )


class BlogListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = filter_posts(
            Post.objects
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        return queryset


class Profile(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.username == self.kwargs['slug']:
            qs = Post.objects.select_related(
                'author', 'category', 'location'
            ).filter(
                author__username=self.kwargs['slug']
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        else:
            qs = filter_posts(
                Post.objects
            ).filter(
                author__username=self.kwargs['slug']
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(
            User,
            username=self.kwargs['slug']
        )
        return context


class ProfileUpdate(OnlyAuthorMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = ProfileForm(
            self.request.POST or None,
            instance=self.get_object()
        )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        form = context['form']
        if form.is_valid():
            form.save()
        return super().form_valid(form)


def profile_update(request):
    instance = get_object_or_404(User, username=request.user.username)
    form = ProfileForm(
        request.POST or None,
        instance=instance
    )
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user.username)
    return render(
        request,
        'blog/user.html',
        context
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


class PostUpdate(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if post.author != request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', args=[self.object.id])


class PostDelete(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(
            self.request.POST or self.request.GET,
            instance=get_object_or_404(
                Post,
                pk=self.kwargs['post_id']
            )
        )
        return context

    def get_success_url(self) -> str:
        return reverse('blog:profile', args=[self.request.user.username])


class PostDetail(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if post.is_published is False or \
            post.category.is_published is False or \
                post.pub_date > now():

            if post.author != self.request.user:
                raise Http404
        context['form'] = CommentForm()
        context["comments"] = self.object.comments.select_related('author')
        return context


class CommentCreate(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.object.post.id])


class CommentUpdate(OnlyAuthorMixin, LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', args=[self.object.post.id])


class CommentDelete(OnlyAuthorMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', args=[self.object.post.id])

    def get_context_data(self, **kwargs):
        context = None
        return context


class CategoryList(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'author', 'category', 'location'
        ).filter(
            category__slug=self.kwargs['slug'],
            is_published=True,
            pub_date__lte=now()
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['slug']
        )
        return context


def post_detail(request, post_id):
    post = get_object_or_404(
        filter_posts(Post.objects), pk=post_id
    )
    return render(request, 'blog/detail.html', context={'post': post})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    post_list = filter_posts(category.posts.all())
    return render(
        request,
        'blog/category.html',
        context={'category': category, 'page_obj': post_list}
    )
