# coding: utf-8
from django.db import models

# Create your models here.
from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())
KEYWORD_CHOICES = sorted({
    0: '匹配关键字',
    1: '翻页关键字'
    }.items())
WEBPAGE_CHOICES = sorted({
    0: '已抓取',
    1: '匹配的',
    }.items())

from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight


class Snippet(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
    owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)
    highlighted = models.TextField()
    
    class Meta:
        ordering = ('created',)
        
    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = 'table' if self.linenos else False
        options = {'title': self.title} if self.title else {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos,
                                  full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet, self).save(*args, **kwargs)    
        
        
class Crawlpage(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    site = models.URLField(max_length=200, blank=True, default='', unique=True)
    title = models.CharField(max_length=200, blank=True, default='')
    code = models.TextField(blank=True)
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)
    status = models.SmallIntegerField(default=0)
    owner = models.ForeignKey('auth.User', related_name='crawlpage', on_delete=models.SET_NULL, null=True, blank=True)
    highlighted = models.TextField()
    
    class Meta:
        ordering = ('created',)
        
    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = 'table' if self.linenos else False
        options = {'title': self.title} if self.title else {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos,
                                  full=True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super().save(*args, **kwargs)    


class Keyword(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    word = models.CharField(max_length=100, default='', unique=True)
    types = models.SmallIntegerField(default=0, choices=KEYWORD_CHOICES)

    class Meta:
        ordering = ('word',)


class Webpage(models.Model):
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    site = models.URLField(max_length=200, blank=True, default='', unique=True)
    title = models.CharField(max_length=100, blank=True, default='')
    status = models.SmallIntegerField(default=0)
    crawled = models.ForeignKey(Crawlpage, related_name='webpage', on_delete=models.SET_NULL, null=True, blank=True)

