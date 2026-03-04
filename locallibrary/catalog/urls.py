from django.urls import path
from . import views
from django.urls import re_path


urlpatterns = [
    path("", views.index, name="index"),
    path("books/", views.BookListView.as_view(), name="books"),
    # path("book/<int:pk>", views.BookDetailView.as_view(), name="book-detail"),
    re_path(
        r"^book/(?P<stub>[-\w]+)$", views.BookDetailView.as_view(), name="book-detail"
    ),
    path(
        "books/<int:year>/<int:month>/<int:day>/",
        views.books_by_date,
        name="books-by-date",
    ),
    re_path(
        r"^books/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$",
        views.books_by_date,
        name="books-by-date",
    ),
    path("authors/", views.AuthorListView.as_view(), name="authors"),
    path("author/<int:pk>", views.AuthorDetailView.as_view(), name="author-detail"),
]
