
from django.contrib.auth import models
from django.core.checks import messages
from django.db.models.base import Model
from django.http import request
from django.shortcuts import redirect, render, get_object_or_404
from .models import Author, Category, Post, Comment, Reply
from .utils import update_views
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import UpdateView
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth import login
def home(request):
    forums = Category.objects.all()
    num_posts = Post.objects.all().count()
    num_users = User.objects.all().count()
    num_categories = forums.count()
    last_post = Post.objects.latest("date")
    context = {
        "forums":forums,
        "num_posts":num_posts,
        "num_users":num_users,
        "num_categories":num_categories,
        "last_post":last_post,
        "title": "Home Page"
    }
    return render(request, "forums.html", context)
def detail(request, slug):
    try:
        post = get_object_or_404(Post, slug=slug)
        author = Author.objects.get(user=request.user)

        if "comment-form" in request.POST:
            comment = request.POST.get("comment")
            new_comment, created = Comment.objects.get_or_create(user=author, content=comment)
            post.comments.add(new_comment.id)

        if "reply-form" in request.POST:
            reply = request.POST.get("reply")
            commenr_id = request.POST.get("comment-id")
            comment_obj = Comment.objects.get(id=commenr_id)
            new_reply, created = Reply.objects.get_or_create(user=author, content=reply)
            comment_obj.replies.add(new_reply.id)
        context = {
            "post":post,
            "title": post.title,
        }
        update_views(request, post)
        return render(request, "detail.html", context)
    except:
        return redirect("error404")
    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # redirect to home or another page after login
    else:
        form = AuthenticationForm()   
    return render(request, 'register/sigin.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after successful signup
            return redirect('home')  # Redirect to home or another page after signup
    else:
        form = UserCreationForm()
    return render(request, 'register/signup.html', {'form': form})

def posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    #posts = Post.objects.all()
    posts = Post.objects.filter(approved=True, categories=category)
    paginator = Paginator(posts, 5)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        "posts":posts,
        "forum": category,
        "title": "Posts"
    }
    return render(request, "posts.html", context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            author,created = Author.objects.get_or_create(user=request.user)
            
            # Assign the author to the post
            post.author = author
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

def latest_posts(request):
    posts = Post.objects.all().filter(approved=True)[:10]
    context = {
        "posts":posts,
        "title": "Latest 10 Posts"
    }
    return render(request, "latest-posts.html", context)

#searching
def search_result(request):
    return render(request, "search.html")

#updating the post here
@login_required
def update_post(request , id):
    context = {}
    try:
        user=Author.objects.get(user=request.user)
        post=Post.objects.get(pk=id , user=user)
        form = PostForm(request.POST or None, instance=post)
        if request.method == "POST":
            if form.is_valid():
                print("\n\n its valid")
                author = Author.objects.get(user=request.user)
                new_post = form.save(commit=False)
                new_post.user = author
                new_post.save()
                form.save_m2m()
                return redirect("home")
    except :
        return redirect("home")
    context.update({
    "form": form,
    "title": "Update Post",
})
    return render(request, "update_post.html", context)

#deleting the post here
@login_required
def delete_post(request , id):
    user=Author.objects.get(user=request.user)
    Post.objects.filter(pk=id, user=user).delete()
        #raise NotImplementedError('The post you are trying to delte not found')
    return redirect("home")

def error404(request):
    return render(request,"error404.html")

def profile_error(request):
    return render(request,"profile_error.html")
