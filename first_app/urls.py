from django.urls import path, include, re_path
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'genres', GenreViewSet)
# router.register(r'genres', GenreReadOnlyViewSet)
# router.register(r'genres', GenreListDetailUpdateViewSet)

urlpatterns = [
    # path('genres/', GenreListCreateView.as_view(), name='genres'),
    # path('genres/<str:genre_name>/', GenreDetailUpdateDeleteView.as_view(), name='genres-detail'),
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookDetailUpdateDeleteView.as_view(), name='book-detail-update-delete'),
    path('books/expensive/', ExpensiveBooksView.as_view(), name='book-expensive'),
    # path('books/', book_list_create, name='book-list-create'),  # Для получения всех книг и создания новой книги
    # path('books/<int:pk>/', book_detail_update_delete, name='book-detail-update-delete'),  # Для операций с одной книгой
    # path('books/', BookListView.as_view(), name='book-list-create'),
    # path('books/<int:pk>/', BookDetailUpdateDeleteView.as_view(), name='book-detail-update-delete'),
    re_path(r'^books/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', books_by_date_view, name='books-by-date'),
    path('', include(router.urls)),
]
