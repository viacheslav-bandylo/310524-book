from datetime import timezone

from rest_framework import serializers
from .models import Book, Publisher
from .models.book import Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class BookDetailSerializer(serializers.ModelSerializer):
    # publisher = PublisherSerializer()  # Вложенный сериализатор
    # publisher = serializers.StringRelatedField()

    class Meta:
        model = Book
        fields = '__all__'


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'author']


class AllBooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'author', 'published_date']
        # fields = '__all__'
        # exclude = ['publisher']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

    def to_representation(self, instance):
        # Использование параметра include_related из контекста
        representation = super().to_representation(instance)
        if self.context.get('include_related'):
            representation['genres'] = [genre.name for genre in instance.genres.all()]
        else:
            representation.pop('genres', None)
        return representation


class BookCreateSerializer(serializers.ModelSerializer):
    publisher_name = serializers.CharField(required=False)

    class Meta:
        model = Book
        fields = ['title', 'author', 'published_date', 'price', 'publisher_name']

    def create(self, validated_data):
        publisher_name = validated_data.pop('publisher_name')
        established_date = timezone.now()
        publisher, created = Publisher.objects.get_or_create(name=publisher_name, established_date=established_date)
        book = Book.objects.create(publisher=publisher, **validated_data)
        return book

