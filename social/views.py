from django.shortcuts import render, HttpResponseRedirect
from django.views import View
from .models import Post
from .forms import PostForm

class PostListView(View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.filter(author=request.user).order_by('-created_on') # all posts - ordered by latest date
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
            return HttpResponseRedirect('/posts/')

        context = {
            'post_list': posts,
            'form': form
        }

        return render(request, 'social/post_list.html', context)

