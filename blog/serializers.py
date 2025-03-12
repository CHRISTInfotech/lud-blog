from rest_framework import serializers
from users.models import Blog

class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)  # Fetch author's name
    author_affiliation = serializers.CharField(source='author.affiliation', read_only=True)  # Fetch author's affiliation
    category_name = serializers.CharField(source='category.name', read_only=True)  # Fetch category name

    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'category_name', 'author_name', 'author_affiliation', 'created_at']
