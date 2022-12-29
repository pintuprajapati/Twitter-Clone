from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.views import View
from .models import Post, Comment, UserProfile
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
        It will show all the posts/tweets on the platform - ordered by latest date
        """
        try:
            posts = Post.get_post_data("all")
        except:
            post = None
            return render(request, "social/error_page.html")
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
        try:
            posts = Post.get_post_data("filter", request.user)
        except:
            post = None
            return render(request, "social/error_page.html")

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
    """
    Logged in user can see all of his/her posts/tweets in "My Posts" navbar field
    """
    try:
        posts = Post.get_post_data("filter", request.user)
    except:
        post = None
        return render(request, "social/error_page.html")
    
    context = {
        'post_list': posts,
    }
    return render(request, 'social/my_post_list.html', context)

class PostDetailView(View):
    """
    Any user can see all the comments on the post
    Only logged in user can comment on the post
    """
    def get(self, request, pk, *args, **kwargs):
        """
        Show all comment(s) of a post/tweet
        """
        try:
            post = Post.get_post_data("get", pk)
        except:
            post = None
            return render(request, "social/error_page.html")
        form = CommentForm()

        comments = Comment.objects.filter(post=post).order_by('-created_on')

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'social/post_detail.html', context)

    @method_decorator(login_required)
    def post(self, request, pk, *args, **kwargs):
        """
        Only logged in user can Write a comment on a post
        """
        try:
            posts = Post.get_post_data("get", pk)
        except:
            post = None
            return render(request, "social/error_page.html")
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

class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    If user of the post/tweet is logged in then he/she can update the post
    Else it will throw 403 Forbidden Error
    """
    model = Post
    fields = ['body']
    template_name = 'social/post_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk}) # to redirect on the same page after editing the post

    def test_func(self):
        """
        checks whether current logged in user matches the author of the post or not
        Returns Boolean
        If True: User can edit the post
        If False: User can't edit the post (will throw 403 Forbidden Error)

        extra: imported from "UserPassesTestMixin"
        """
        post = self.get_object() # current post's object
        user_of_post = self.request.user == post.author # True or False
        return user_of_post

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    If user of the post/tweet is logged in then he/she can delete the post
    Else it will throw 403 Forbidden Error
    """
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('my-post-list') # once deleted, redirect back to 'my-post-list' url

    def test_func(self):
        """
        checks whether current logged in user matches the author of the post or not
        Returns Boolean
        If True: User can delete the post
        If False: User can't delete the post (will throw 403 Forbidden Error)

        extra: imported from "UserPassesTestMixin"
        """
        post = self.get_object() # current post's object
        user_of_post = self.request.user == post.author # True or False
        return user_of_post

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    If user of the post/tweet is logged in then he/she can delete the comment on the post
    Else it will throw 403 Forbidden Error
    """
    model = Comment
    template_name = 'social/comment_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk}) # Will redirect to the that 'post' after comment is deleted
    
    def test_func(self):
        """
        checks whether current logged in user matches the author of the comment or not
        Returns Boolean
        If True: User can edit the comment
        If False: User can't edit the comment (will throw 403 Forbidden Error)

        extra: imported from "UserPassesTestMixin"
        """
        comment = self.get_object() # current comment's object
        user_of_comment = self.request.user == comment.author # True or False
        return user_of_comment

class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk) # If primary key matches then store the object into profile
        user = profile.user
        try:
            posts = Post.get_post_data("filter", profile.user)
        except:
            post = None
            return render(request, "social/error_page.html")

        context = {
            'profile': profile,
            'user': user,
            'posts': posts
        }

        return render(request, 'social/profile.html', context)

# If post/comment doesn't exists
def error_view(request):
    return render(request, "social/error_page.html")

# To edit the profile
class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = ["name", "bio", "birth_date", "location", "picture"]
    template_name = "social/profile_edit.html"

    # Once submitted, redirect to same url
    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse_lazy('pk', kwargs={'pk': pk})

    def test_func(self):
        profile = self.get_object() # current profile's object
        profile_of_user = self.request.user == profile.user
        return profile_of_user # True or False
