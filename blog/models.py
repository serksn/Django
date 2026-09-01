from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        abstract = True

class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)
   
    def with_author_and_tags(self):
        return self.select_related('author').prefetch_related('tags')
   
    def recent_first(self):
        return self.order_by('-created_at')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    #avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
            verbose_name = 'тэг'
            verbose_name_plural = 'тэги'

class Article(TimeStampedModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    published_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    
    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ['-published_date']
        verbose_name = 'статья'
        verbose_name_plural = 'статьи'
    
    def __str__(self):
            return self.title