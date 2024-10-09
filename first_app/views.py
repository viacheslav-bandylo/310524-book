from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination

from .serializers import BookListSerializer, BookDetailSerializer, BookCreateSerializer, GenreSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets, mixins
from .models.book import *
from .serializers import BookSerializer


class GenreListDetailUpdateViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                                   mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class GenreReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    @action(detail=False, methods=['get'])
    def statistic(self, request):
        genres_with_book_counts = Genre.objects.annotate(book_count=Count('books'))
        data = [
            {
                "id": genre.id,
                "genre": genre.name,
                "book_count": genre.book_count
            }
            for genre in genres_with_book_counts
        ]
        return Response(data)



# class GenreListCreateView(ListCreateAPIView):
#     queryset = Genre.objects.all()
#     serializer_class = GenreSerializer
#
#
# class GenreDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
#     queryset = Genre.objects.all()
#     serializer_class = GenreSerializer
#     lookup_field = 'name'  # Указывает использовать поле 'name' для поиска
#     lookup_url_kwarg = 'genre_name'  # Указывает параметр URL 'genre_name' для получения значения


class BookPagination(PageNumberPagination):
    page_size = 5  # Количество элементов на странице
    page_size_query_param = 'page_size'
    max_page_size = 100


# class BookPagination(CursorPagination):
#     page_size = 2  # Количество элементов на странице
#     ordering = 'published_date'


class BookListCreateView(ListCreateAPIView):
    queryset = Book.objects.select_related('publisher').prefetch_related('genres').all()
    serializer_class = BookSerializer
    pagination_class = BookPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['author', 'publisher']
    search_fields = ['title', 'author', 'published_date']
    ordering_fields = ['published_date', 'price']

    # Добавление кастомной логики перед сохранением
    def create(self, request, *args, **kwargs):
        # Получение данных из запроса
        data = request.data.copy()
        # Кастомная логика: Установка значения по умолчанию для автора, если не указан
        if 'author' not in data or not data['author']:
            data['author'] = 'Unknown Author'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['include_related'] = self.request.query_params.get('include_related', 'false').lower() == 'true'
        return context


class BookDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_object(self):
        # Получение параметра pk из URL
        pk = self.kwargs.get('pk')

        # Попытка найти объект по pk, исключая запрещенные
        try:
            book = self.queryset.get(pk=pk, is_banned=False)
        except Book.DoesNotExist:
            # Обработка ошибки, если объект не найден или запрещен
            raise NotFound(detail=f"Book with id '{pk}' not found or is banned.")

        return book

    # Переопределение метода для добавления кастомной логики
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        # Добавление поля к ответу, проверяющего, что цена со скидкой меньше цены
        if response.data.get('discounted_price') is not None and response.data.get('price') is not None:
            response.data['is_discounted'] = response.data['discounted_price'] < response.data['price']
        else:
            response.data['is_discounted'] = False

        return response

    # Добавление кастомной проверки перед обновлением
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Пример проверки: цена книги не должна быть ниже минимальной
        if serializer.validated_data.get('price', instance.price) < 5.00:
            return Response({'error': 'Price cannot be less than 5.00'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response(serializer.data)

    # Добавление кастомной логики при удалении объекта
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        # Пример кастомной логики: логирование успешного удаления
        print(f"Book deleted: {instance}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpensiveBooksView(ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def list(self, request, *args, **kwargs):
        # Вычисление средней цены
        average_price = Book.objects.aggregate(average_price=Avg('price'))['average_price']
        # Получение книг с ценой выше средней
        queryset = Book.objects.filter(price__gt=average_price)
        # Сериализация данных
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# class BookListCreateView(GenericAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer
#
#     def get(self, request, *args, **kwargs):
#         books = self.get_queryset()
#         serializer = self.get_serializer(books, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class BookDetailUpdateDeleteView(GenericAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer
#
#     def get(self, request, *args, **kwargs):
#         book = self.get_object()
#         serializer = self.get_serializer(book)
#         return Response(serializer.data)
#
#     def put(self, request, *args, **kwargs):
#         book = self.get_object()
#         serializer = self.get_serializer(book, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#     def patch(self, request, *args, **kwargs):
#         book = self.get_object()
#         serializer = self.get_serializer(book, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#     def delete(self, request, *args, **kwargs):
#         book = self.get_object()
#         book.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET', 'POST'])
# def book_list_create(request):
#     if request.method == 'GET':
#         books = Book.objects.all()
#         serializer = BookListSerializer(books, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     elif request.method == 'POST':
#         serializer = BookCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'PUT', 'DELETE'])
# def book_detail_update_delete(request, pk):
#     try:
#         book = Book.objects.get(pk=pk)
#     except Book.DoesNotExist:
#         return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
#
#     if request.method == 'GET':
#         serializer = BookDetailSerializer(book)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     elif request.method == 'PUT':
#         serializer = BookCreateSerializer(book, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == 'DELETE':
#         book.delete()
#         return Response({'message': 'Book deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# class BookListCreateView(APIView):
#     # def get(self, request):
#     #     filters = {}
#     #     # https://127.0.0.1:8000/books/?author=John&published_year=2023
#     #     author = request.query_params.get('author')
#     #     published_year = request.query_params.get('pub_year')
#     #
#     #     if author:
#     #         filters['author'] = author
#     #
#     #     if published_year:
#     #         filters['published_date__year'] = published_year
#     #
#     #     books = Book.objects.filter(**filters)
#     #     serializer = BookDetailSerializer(books, many=True)  # Заменим на BookDetailSerializer чтобы видеть много полей
#     #     return Response(serializer.data)
#
#     def get(self, request):
#         sort_by = request.query_params.get('sort_by', 'title')
#         sort_order = request.query_params.get('sort_order', 'asc')
#
#         books = Book.objects.all()
#
#         if sort_order == 'desc':
#             sort_by = f'-{sort_by}'
#
#         books = books.order_by(sort_by)
#         serializer = BookDetailSerializer(books, many=True)
#         return Response(serializer.data)
#
#
#     def post(self, request):
#         serializer = BookSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class BookDetailUpdateDeleteView(APIView):
#     def get(self, request, pk):
#         try:
#             book = Book.objects.get(pk=pk)
#         except Book.DoesNotExist:
#             return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = BookSerializer(book)
#         return Response(serializer.data)
#
#     def put(self, request, pk):
#         try:
#             book = Book.objects.get(pk=pk)
#         except Book.DoesNotExist:
#             return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = BookSerializer(book, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         try:
#             book = Book.objects.get(pk=pk)
#         except Book.DoesNotExist:
#             return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
#         book.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class BookListView(APIView, PageNumberPagination):
    page_size = 2  # Значение по умолчанию

    def get(self, request):
        books = Book.objects.all()
        page_size = self.get_page_size(request)  # Получение параметра page_size из запроса
        self.page_size = page_size  # Установка значения page_size
        results = self.paginate_queryset(books, request, view=self)
        serializer = BookDetailSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def get_page_size(self, request):
        """
        Переопределение метода get_page_size для поддержки параметра page_size.
        """
        page_size = request.query_params.get('page_size')
        if page_size and page_size.isdigit():
            return int(page_size)
        return self.page_size  # Использование значения по умолчанию


@api_view(['GET'])
def books_by_date_view(request, year, month, day):
    books = Book.objects.filter(published_date__year=year, published_date__month=month, published_date__day=day)
    serializer = BookSerializer(books, many=True)
    return Response({'date': f"{year}-{month}-{day}", 'books': serializer.data})
