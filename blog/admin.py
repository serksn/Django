from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Tag, Article

# Register your models here.
#admin.site.register(Tag)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'articles_count']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _articles_count=Count('articles', distinct=True)
        )
        return queryset

    def articles_count(self, obj):
        return obj._articles_count

    articles_count.short_description = 'Количество статей'
    articles_count.admin_order_field = '_articles_count'

#admin.site.register(Article)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'author',
        'status_indicator',
        'tags_display',
        'created_at_formatted',
        'updated_at_formatted'
    ]

    list_filter = [
        'is_published',
        'created_at',
        'author',
        'tags'
    ]

    search_fields = ['title', 'content', 'author__username', 'author__email']

    filter_horizontal = ['tags']

    readonly_fields = ['created_at', 'updated_at', 'preview_content']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'author', 'content')
        }),
        ('Категоризация', {
            'fields': ('tags',)
        }),
        ('Публикация', {
            'fields': ('is_published',)
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at', 'preview_content'),
            'classes': ('collapse',)
        })
    )

    date_hierarchy = 'created_at'

    list_per_page = 25

    actions = ['publish_articles', 'unpublish_articles', 'export_to_csv']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('author').prefetch_related('tags')
        return queryset

    def status_indicator(self, obj):
        if obj.is_published:
            color = 'green'
            text = 'Опубликовано'
        else:
            color = 'red'
            text = 'Черновик'

        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color,
            text
        )

    status_indicator.short_description = 'Статус'

    def tags_display(self, obj):
        tags = obj.tags.all()
        if not tags:
            return '-'

        tag_links = []
        for tag in tags:
            tag_links.append(
                format_html(
                    '<span style="background-color: #e3f2fd; padding: 2px 8px; '
                    'border-radius: 3px; margin-right: 5px; display: inline-block;">{}</span>',
                    tag.name
                )
            )

        return format_html(' '.join(tag_links))

    tags_display.short_description = 'Теги'

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d.%m.%Y %H:%M')

    created_at_formatted.short_description = 'Создана'
    created_at_formatted.admin_order_field = 'created_at'

    def updated_at_formatted(self, obj):
        return obj.updated_at.strftime('%d.%m.%Y %H:%M')

    updated_at_formatted.short_description = 'Обновлена'
    updated_at_formatted.admin_order_field = 'updated_at'

    def preview_content(self, obj):
        if len(obj.content) > 200:
            preview = obj.content[:200] + '...'
        else:
            preview = obj.content

        return format_html(
            '<div style="padding: 10px; background-color: #f5f5f5; '
            'border-left: 3px solid #2196F3;">{}</div>',
            preview
        )

    preview_content.short_description = 'Предпросмотр содержания'
    
    def publish_articles(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(
            request,
            f'Опубликовано статей: {updated}',
            level='success'
        )

    publish_articles.short_description = 'Опубликовать выбранные статьи'

    def unpublish_articles(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(
            request,
            f'Снято с публикации статей: {updated}',
            level='warning'
        )

    unpublish_articles.short_description = 'Снять с публикации выбранные статьи'

    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="articles.csv"'
        response.write('\ufeff')  # BOM для корректного отображения кириллицы в Excel

        writer = csv.writer(response)
        writer.writerow(['Заголовок', 'Автор', 'Статус', 'Дата создания', 'Теги'])

        for article in queryset.select_related('author').prefetch_related('tags'):
            tags = ', '.join([tag.name for tag in article.tags.all()])
            status = 'Опубликовано' if article.is_published else 'Черновик'

            writer.writerow([
                article.title,
                article.author.username,
                status,
                article.created_at.strftime('%d.%m.%Y %H:%M'),
                tags
            ])

        return response

    export_to_csv.short_description = 'Экспортировать в CSV'