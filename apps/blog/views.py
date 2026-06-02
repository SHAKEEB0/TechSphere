from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from .models import Bookmark, Category, Comment, Like, Post, PostView, Tag


from django.utils import timezone


def home(request):
    now = timezone.now()
    latest = Post.objects.filter(status='published', publish_at__lte=now).order_by('-publish_at')[:8]
    trending = Post.objects.filter(status='published', publish_at__lte=now).order_by('-views_count')[:6]
    popular = Post.objects.filter(status='published', publish_at__lte=now).annotate(total_comments=Count('comments')).order_by('-total_comments')[:6]
    categories = Category.objects.all()[:12]
    return render(request, 'blog/home.html', {
        'latest': latest,
        'trending': trending,
        'popular': popular,
        'categories': categories,
    })


def post_detail(request, category_slug, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    PostView.objects.create(post=post, user=request.user if request.user.is_authenticated else None, ip_address=request.META.get('REMOTE_ADDR'))
    related = Post.objects.filter(category=post.category, status='published').exclude(id=post.id)[:4]
    comments = post.comments.filter(is_public=True, parent__isnull=True)
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'related': related,
        'comments': comments,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published')
    return render(request, 'blog/category_detail.html', {'category': category, 'posts': posts})


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag, status='published')
    return render(request, 'blog/tag_detail.html', {'tag': tag, 'posts': posts})


def search(request):
    query = request.GET.get('q', '')
    posts = Post.objects.filter(status='published')
    if query:
        vector = SearchVector('title', weight='A') + SearchVector('summary', weight='B') + SearchVector('body', weight='C')
        search_query = SearchQuery(query)
        posts = posts.annotate(rank=SearchRank(vector, search_query)).filter(rank__gte=0.1).order_by('-rank')
    return render(request, 'blog/search_results.html', {'posts': posts, 'query': query})
