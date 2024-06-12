from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse


from .models import Post, Comment
from .forms import PostForm


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin(LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self) -> HttpResponseRedirect:
        if '/create/' not in self.request.path:
            return redirect('blog:post_detail', self.kwargs[self.pk_url_kwarg])
        return super().handle_no_permission()

    def get_success_url(self) -> str:
        return reverse('blog:profile', args=[self.request.user.username])

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if '/delete/' in self.request.path:
            context['form'] = PostForm(
                self.request.POST or self.request.GET,
                instance=get_object_or_404(
                    Post,
                    pk=self.kwargs['post_id']
                )
            )
        print(context)
        return context


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', args=[self.object.post.id])
