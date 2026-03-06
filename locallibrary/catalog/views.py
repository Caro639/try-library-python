from django.shortcuts import render

# Create your views here.
from catalog.models import Book, Author, BookInstance, Genre

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib.auth.decorators import permission_required


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

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get("num_visits", 0)
    num_visits += 1
    request.session["num_visits"] = num_visits

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
            "num_visits": num_visits,
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


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 4

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )


class LoanedBooksByStaffListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to staff."""

    permission_required = ("catalog.can_mark_returned",)

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_staff.html"
    paginate_by = 4

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact="o").order_by("due_back")


import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm


@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse("my-staff"))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})

    context = {
        "form": form,
        "book_instance": book_instance,
    }

    return render(request, "catalog/book_renew_librarian.html", context)
