from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.views import View
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required



class PostListView(View):
    """
    Any user can see the latest post/tweet but only logged in user can write a new post/tweet
    """

    def get(self, request, *args, **kwargs):
        """
        It will show all the posts/tweets on the plateform - ordered by latest date
        """
        posts = Post.objects.all().order_by('-created_on') # all posts - ordered by latest date
        form = PostForm()

        context = {
            'post_list': posts,
            'form': form
        }
        return render(request, 'social/post_list.html', context)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """
        Only logged in user can write a new post/tweet
        """
        posts = Post.objects.filter(author=request.user).order_by('-created_on')
        form = PostForm(request.POST)

        if form.is_valid():
            new_post = form.save(commit=False) # Creates object "new_post" but doesn't save it into database (created on memory level only)
            new_post.author = request.user 
            new_post.save()
            return HttpResponseRedirect('/latest-posts/') # once post/tweet is posted, it will redirect to same url/page

        context = {
            'post_list': posts,
            'form': form
        }

        return render(request, 'social/post_list.html', context)

@login_required(login_url='index')
def my_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_on') # all posts - ordered by latest date
    form = PostForm()

    context = {
        'post_list': posts,
        'form': form
    }
    return render(request, 'social/my_post_list.html', context)

# To comment on a post
class PostDetailView(LoginRequiredMixin, View):
    # To show the comment
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()

        comments = Comment.objects.filter(post=post).order_by('-created_on')

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'social/post_detail.html', context)

    # To write a comment and save it
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
            return HttpResponseRedirect('/post/'+str(pk)) # after commenting, it will redirect to same page and form() will be blank again
        
        comments = Comment.objects.filter(post=post).order_by('-created_on')

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'social/post_detail.html', context)

# Update view
class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['body']
    template_name = 'social/post_edit.html'

    # to redirect the same page after editing
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})


    def test_func(self):
        """
        checks whether current logged in user matchs the author of the post or not
        Returns Boolean
        If True: User can edit the post
        If False: User can't edit the post (will throw 403 Forbidden Error)

        extra: imported from "UserPassesTestMixin"
        """
        post = self.get_object() # current post's object
        return self.request.user == post.author


# Delete The Post View
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('my-post-list') # once deleted, go back to latest post list page

    def test_func(self):
        """
        checks whether current logged in user matchs the author of the post or not
        Returns Boolean
        If True: User can edit the post
        If False: User can't edit the post (will throw 403 Forbidden Error)

        extra: imported from "UserPassesTestMixin"
        """
        post = self.get_object() # current post's object
        return self.request.user == post.author

# Delete the Comment
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'social/comment_delete.html'

    # to redirect the same page after editing
    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})
    
    def test_func(self):
        """
        checks whether current logged in user matchs the author of the post or not
        Returns Boolean
        If True: User can edit the post
        If False: User can't edit the post (will throw 403 Forbidden Error)

        extra: imported from "UserPassesTestMixin"
        """
        post = self.get_object() # current post's object
        return self.request.user == post.author
