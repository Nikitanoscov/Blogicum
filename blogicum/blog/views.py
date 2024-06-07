from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from django.views.generic import (
    DetailView, CreateView, ListView, UpdateView
)
from django.urls import reverse_lazy

from .const_for_blog import COUNT_POSTS_ON_MAIN
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()

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


class ProfileUpdate(UpdateView):
    model = get_user_model()
    form_class = UserCreationForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:profile')


class PostCreate(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:profile')


class PostDetail(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context["comments"] = self.objects.comments.select_related('author')
        return context


class CommentCreate(CreateView):
    post = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post
        return super().form_valid(form)
    
    def get_success_url(self):
        return redirect('blog:post_detail', kwargs={'pk': self.post.pk})


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
