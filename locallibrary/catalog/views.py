from django.shortcuts import render

# Create your views here.
from catalog.models import Book, Author, BookInstance, Genre


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Décompte des genres contenant le mot 'Horror' (casse respectée)
    num_genres_with_word = Genre.objects.filter(name__contains="Horror").count()

    # Décompte des titres de livres contenant le mot 'le' (casse respectée)
    num_books_with_word = Book.objects.filter(title__contains="le").count()

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        "index.html",
        context={
            "num_books": num_books,
            "num_instances": num_instances,
            "num_instances_available": num_instances_available,
            "num_authors": num_authors,
            "num_genres_with_word": num_genres_with_word,
            "num_books_with_word": num_books_with_word,
        },
    )


from django.views import generic


class BookListView(generic.ListView):
    model = Book
    paginate_by = 4
    # context_object_name = (
    #     "my_book_list"  # your own name for the list as a template variable
    # )
    # queryset = Book.objects.filter(title__icontains="le")[
    #     :5
    # ]  # Get 5 books containing the title le
    # template_name = "books/my_arbitrary_template_name_list.html"
    # Specify your own template name/location


def books_by_date(request, year, month, day):
    books = Book.objects.filter(
        publish_date__year=year, publish_date__month=month, publish_date__day=day
    )
    return render(
        request, "books_by_date.html", {"books": books, "date": f"{year}/{month}/{day}"}
    )


# views.py
class BookDetailView(generic.DetailView):
    model = Book
    slug_field = "slug"  # champ dans le modèle
    slug_url_kwarg = "stub"  # nom du paramètre dans l'URL


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 4


class AuthorDetailView(generic.DetailView):
    model = Author
