from django.shortcuts import render, HttpResponseRedirect
from django.views import View
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy

class PostListView(View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-created_on') # all posts - ordered by latest date
        form = PostForm()

        context = {
            'post_list': posts,
            'form': form
        }
        return render(request, 'social/post_list.html', context)
    
    def post(self, request, *args, **kwargs):
        posts = Post.objects.filter(author=request.user).order_by('-created_on')
        form = PostForm(request.POST)

        if form.is_valid():
            # Create object "new_post" but don't save it into database
            # created on memory level only, Later we can assign some values to "new_post" obj and save it to the database
            new_post = form.save(commit=False)
            new_post.author = request.user 
            new_post.save()
            return HttpResponseRedirect('/latest-posts/')

        context = {
            'post_list': posts,
            'form': form
        }

        return render(request, 'social/post_list.html', context)

# To view my posts only
def my_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_on') # all posts - ordered by latest date
    form = PostForm()

    context = {
        'post_list': posts,
        'form': form
    }
    return render(request, 'social/my_post_list.html', context)

# To comment on a post
class PostDetailView(View):
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

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
            return HttpResponseRedirect('/post/'+str(pk))
        
        comments = Comment.objects.filter(post=post).order_by('-created_on')

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'social/post_detail.html', context)

# Update view
class PostEditView(UpdateView):
    model = Post
    fields = ['body']
    template_name = 'social/post_edit.html'

    # to redirect page after editing
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

# Delete View
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('latest-post-list') # once deleted, go back to latest post list page
