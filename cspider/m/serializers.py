from rest_framework import serializers
from m.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES


class SnippetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    code = serializers.CharField(style={'base_template': 'textarea.html'})
    linenos = serializers.BooleanField(required=False)
    language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
    style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')
    owner = serializers.ReadOnlyField(source='owner.username')
    

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Snippet.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.code = validated_data.get('code', instance.code)
        instance.linenos = validated_data.get('linenos', instance.linenos)
        instance.language = validated_data.get('language', instance.language)
        instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance
    
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import password_changed

class UserSerializer(serializers.ModelSerializer):
    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())

    def update(self, instance, validated_data):
        """Only change password in PUT method"""
        password_changed(validated_data.password, instance)
        return self.list(instance.pk)

    class Meta:
        model = User
        #fields = ('id', 'username', 'password', 'snippets')
        fields = '__all__'
        
from m.models import Webpage, Crawlpage, Keyword

class CrawlpageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crawlpage
        #fields = '__all__'
        #fields = ('id', 'site', 'code', 'status')
        exclude = ('highlighted',)


class WebpageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Webpage
        fields = '__all__'


class KeywordSerializer(serializers.ModelSerializer):

    class Meta:
        model = Keyword
        fields = '__all__'
