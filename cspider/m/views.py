# coding: utf-8
from django.shortcuts import render

# Create your views here.
from m.models import Snippet
from m.serializers import SnippetSerializer
from rest_framework import generics
from rest_framework import permissions
from m.permissions import IsOwnerOrReadOnly

class SnippetList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)    
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    
    

from django.contrib.auth.models import User
from m.serializers import UserSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

from rest_framework import viewsets
    
#class UserViewSet(viewsets.ReadOnlyModelViewSet):
class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'snippets': reverse('snippet-list', request=request, format=format)
    })
    
from rest_framework import renderers
from rest_framework.response import Response

class SnippetHighlight(generics.GenericAPIView):
    queryset = Snippet.objects.all()
    renderer_classes = (renderers.StaticHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)
    


from rest_framework.decorators import action
from rest_framework.response import Response

class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        

from m.models import Webpage, Crawlpage, Keyword
from m.serializers import CrawlpageSerializer, WebpageSerializer, KeywordSerializer

class CrawlpageViewSet(viewsets.ModelViewSet):
    """
    *This will be shown as description on api*
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    #Additionally we also provide an extra `highlight` action.
    """
    queryset = Crawlpage.objects.all()
    serializer_class = CrawlpageSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


from django_filters.rest_framework import DjangoFilterBackend


class WebpageViewSet(viewsets.ModelViewSet):
    """all crawled page\n
    *WARNING*\n
    Also provide `truncate` action to truncate table
    """
    queryset = Webpage.objects.all()
    serializer_class = WebpageSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    # 使用过滤器 
    filter_backends = (DjangoFilterBackend,)
    # 定义需要使用过滤器的字段
    filter_fields = ('id', 'status', 'crawled')    
    
    @action(detail=False, renderer_classes=[renderers.StaticHTMLRenderer])
    def truncate(self, request, *args, **kwargs):
        return Response(repr(self.queryset.delete()))

class KeywordViewSet(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
