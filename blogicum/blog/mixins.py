from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse


from .models import Comment, Post
from .forms import CommentForm, PostForm


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin(LoginRequiredMixin, OnlyAuthorMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect('blog:post_detail', self.kwargs['post_id'])

    def get_success_url(self) -> str:
        return reverse('blog:profile', args=[self.request.user.username])

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(
            instance=self.object
        )
        return context


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', args=[self.object.post.id])
