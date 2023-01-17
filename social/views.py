from django.shortcuts import render, HttpResponseRedirect, HttpResponse, redirect
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
            posts = None
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
            posts = None
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
        posts = None
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
            post = Post.get_post_data("get", pk)
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

class PostEditView(LoginRequiredMixin, UpdateView):
    """
    If user of the post/tweet is logged in then he/she can delete the post
    Else it will show relevert error pages
    """
    model = Post
    fields = ['body']
    template_name = 'social/post_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk}) # to redirect on the same page after editing the post

    def get(self, request, *args, **kwargs):
        """
        Will check whether current logged in user is the same as post's author
        If True (post's author and logged in user are same) -> Redirect to "post-edit" page
        If Flase (Not the same user) -> Redirect to "user is not allowed to edit this post" page

        If Post doesn't exists in DB -> Redirect to "Error Page"
        """
        try:
            post = self.get_object()
            if self.request.user == post.author:
                return super().get(request, *args, **kwargs)
            else:
                return render(request, 'social/not_allowed.html')
        except:
            return render(request, 'social/error_page.html')

class PostDeleteView(LoginRequiredMixin, DeleteView):
    """
    If user of the post/tweet is logged in then he/she can delete the post
    Else it will show relevert error pages
    """
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('my-post-list') # once deleted, redirect back to 'my-post-list' url

    def get(self, request, *args, **kwargs):
        """
        Will check whether current logged in user is the same as post's author
        If True (post's author and logged in user are same) -> Redirect to "post-edit" page
        If Flase (Not the same user) -> Redirect to "user is not allowed to edit this post" page

        If Post doesn't exists in DB -> Redirect to "Error Page"
        """
        try:
            post = self.get_object()
            if self.request.user == post.author:
                return super().get(request, *args, **kwargs)
            else:
                return render(request, 'social/not_allowed.html')
        except:
            return render(request, 'social/error_page.html')

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """
    If user of the post/tweet is logged in then he/she can delete the comment on the post
    Else it will show relevert error pages
    """
    model = Comment
    template_name = 'social/comment_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk}) # Will redirect to the that 'post' after comment is deleted

    def get(self, request, *args, **kwargs):
        """
        Will check whether current logged in user is the same as Comment's author
        If True (comment's author and logged in user are same) -> Redirect to "post-delete" page
        If Flase (Not the same user) -> Redirect to "user is not allowed" page

        If Comment doesn't exists in DB -> Redirect to "Error Page"
        """
        try:
            comment = self.get_object()
            if self.request.user == comment.author:
                return super().get(request, *args, **kwargs)
            else:
                return render(request, 'social/not_allowed.html')
        except:
            return render(request, 'social/error_page.html')

class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk) # If primary key matches then store the object into profile
        user = profile.user

        followers = profile.followers.all()        
        number_of_followers = len(followers)

        if number_of_followers == 0:
            is_following = False
        else:                
            for follower in followers:
                if follower == request.user:
                    is_following = True
                    break
                else:
                    is_following = False

        try:
            posts = Post.get_post_data("filter", profile.user)
        except:
            post = None
            return render(request, "social/error_page.html")

        context = {
            'profile': profile,
            'user': user,
            'posts': posts,
            'number_of_followers': number_of_followers,
            'is_following': is_following
        }

        return render(request, 'social/profile.html', context)

# If post/comment doesn't exists
def error_view(request):
    return render(request, "social/error_page.html")

# To edit the profile
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ["name", "bio", "birth_date", "location", "picture"]
    template_name = "social/profile_edit.html"

    # Once submitted, redirect to same url
    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse_lazy('profile', kwargs={'pk': pk})

    def get(self, request, *args, **kwargs):
        """
        Will check whether current logged in user is the same as Profile User
        If True -> Redirect to "post-update" page
        If Flase (Not the same user) -> Redirect to "user is not allowed" page

        If Profile doesn't exists in DB -> Redirect to "Error Page"
        """
        try:
            profile = self.get_object()
            if self.request.user == profile.user:
                return super().get(request, *args, **kwargs)
            else:
                return render(request, 'social/not_allowed.html')
        except:
            return render(request, 'social/error_page.html')      

class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user) # adding logged-in user to the list of followers by using ".add()"
        return redirect('profile', pk=profile.pk)


class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user) # remove from followers list
        return redirect('profile', pk=profile.pk)

class AddLike(LoginRequiredMixin, View):
    print("➡ AddLike entered :")
    """
    When clicking on LIKE button
    Add like to the post if user has not liked yet. If liked then remove the like
    If disliked alredy then remove it and add a like
    """    
    def get(self, request, pk, *args, **kwargs):
        print("➡ pk for add like :", pk)
        # post = Post.get_post_data("get", pk)
        post = Post.objects.get(pk=pk)

        is_disike = False 
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_disike = True
                break
        if is_disike:
            post.dislikes.remove(request.user) # if disliked the post already then remove the dislike

        is_like = False 
        print("➡ is_like :", post.likes.all())
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
            if not is_like:
                post.likes.add(request.user) # if not liked then add a like
            if is_like:
                post.likes.remove(request.user) # if liked then remove a like 

        # checked if the post's author and logged-in users are same or not
        # try:
        #     post = self.get_object()
        #     if self.request.user == post.author:
        #         return super().get(request, *args, **kwargs)
        #     else:
        #         return render(request, 'social/not_allowed.html')
        # except:
        #     return render(request, 'social/error_page.html')
        
        next = request.POST.get('next', '/latest-posts/')
        return HttpResponseRedirect(next)
        
          
class AddDisLike(LoginRequiredMixin, View):
    print("➡ AddDisLike :")

    """
    When clicking on DISLIKE button
    Add dislike to the post if user has not disliked yet. If disliked then remove the like
    If liked alredy then remove it and add a dislike
    """
    
    def get(self, request, pk, *args, **kwargs):
        print("➡ pk :", pk)

        # # checked if the post's author and logged-in users are same or not
        # try:
        #     post = self.get_object()
        #     if self.request.user == post.author:
        #         return super().get(request, *args, **kwargs)
        #     else:
        #         return render(request, 'social/not_allowed.html')
        # except:
        #     return render(request, 'social/error_page.html')

        # post = Post.get_post_data("get", pk)
        post = Post.objects.get(pk=pk)
        print("➡ post :", post)

        is_like = False 
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
        if is_like:
            post.likes.remove(request.user)# if user liked the post already then remove the like

        is_dislike = False 
        print("➡ is_disike :", post.dislikes.all())
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
            if not is_dislike:
                post.dislikes.add(request.user) # if not disliked then add a dislike
            if is_dislike:
                post.dislikes.remove(request.user) # if disliked then remove a dislike
        
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


