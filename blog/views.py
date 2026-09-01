from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Avg, Q
from django.db.models.functions import Length
from django.contrib.auth import get_user_model

from .models import Article, Tag

User = get_user_model()

# Create your views here.
def home(request):
    articles = Article.objects.published().with_author_and_tags().recent_first()[:20]
    
    context = {'articles': articles}
    return render(request, 'home.html', context)

def article_detail(request, article_id):
    article = get_object_or_404(
        Article.objects.published().with_author_and_tags(),
        id=article_id
    )

    # Находим похожие статьи по тегам
    related_articles = Article.objects.published().filter(
        tags__in=article.tags.all()
    ).exclude(
        id=article.id
    ).annotate(
        same_tags=Count('id')
    ).order_by('-same_tags', '-published_date').with_author_and_tags()[:5]

    return render(request, 'article_detail.html', {
        'article': article,
        'related_articles': related_articles
    })

def authors_stats(request):
    authors = User.objects.annotate(
        total_articles=Count('articles', filter=Q(articles__is_published=True)),
        avg_content_length=Avg(Length('articles__content'), filter=Q(articles__is_published=True)),
        total_tags=Count('articles__tags', distinct=True, filter=Q(articles__is_published=True))
    ).filter(
        total_articles__gt=0
    ).order_by('-total_articles')

    return render(request, 'authors_stats.html', {
        'authors': authors
    })
    
def search(request):
    query = request.GET.get('q', '')

    if query:
        articles = Article.objects.published().filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(tags__name__icontains=query)
        ).distinct().with_author_and_tags().recent_first()[:50]
    else:
        articles = Article.objects.none()

    return render(request, 'search.html', {
        'articles': articles,
        'query': query
    })

def tag_articles(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    articles = Article.objects.published().filter(
        tags=tag
    ).with_author_and_tags().recent_first()
    
    return render(request, 'tag_articles.html', {
        'tag': tag,
        'articles': articles
    })

def books(request):
    books_list = Books.objects.all()
    return JsonResponse({'books': list(books_list.values())})
    
@csrf_exempt
def create_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Article.objects.create(title=title, content=content, is_published=False)
        return JsonResponse({'status': 'success', 'message': f'Article "{title}" created successfully!'})
    return render(request, 'create_article.html')