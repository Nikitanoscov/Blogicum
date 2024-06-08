from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.generic import (
    DeleteView, DetailView, CreateView, ListView, UpdateView
)
from django.urls import reverse_lazy, reverse
from django.db.models import Count

from .const_for_blog import COUNT_POSTS_ON_MAIN
from .forms import CommentForm, PostForm
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


# def index(request):
#     post_list = filter_posts(Post.objects)[:COUNT_POSTS_ON_MAIN]
#     return render(request, 'blog/index.html', context={'post_list': post_list})

class BlogListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    queryset = filter_posts(Post.objects)


class Profile(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10
    queryset = filter_posts(Post.objects)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(
            User,
            username=self.request.user.username
        )
        return context
    
    def get_queryset(self):
        posts_query = self.queryset
        posts_query.annotate(comment_count=Count('comments'))
        return posts_query
    

class ProfileUpdate(UpdateView):
    model = get_user_model()
    form_class = UserCreationForm
    template_name = 'blog/user.html'
    


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse('blog:profile')


class PostDetail(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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


class CommentUpdate(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', args=[self.object.post.id])


class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', args=[self.object.post.id])


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
        context={'category': category, 'post_list': post_list}
    )
