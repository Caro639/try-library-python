from django.db import models
from django.urls import reverse  # Cette fonction est utilisée pour formater les URL
import uuid  # Ce module est nécessaire à la gestion des identifiants unique (RFC 4122) pour les copies des livres
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils.text import slugify
from django.conf import settings
from datetime import date


# Create your models here.
class Genre(models.Model):
    """Cet objet représente une catégorie ou un genre littéraire."""

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a book genre (e.g. Science Fiction)",
    )

    def __str__(self):
        """Cette fonction est obligatoirement requise par Django.
        Elle retourne une chaîne de caractère pour identifier l'instance de la classe d'objet.
        """
        return self.name

    def get_absolute_url(self):
        """Cette fonction est requise pas Django, lorsque vous souhaitez détailler le contenu d'un objet."""
        return reverse("genre-detail", args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("name"),
                name="genre_name_case_insensitive_unique",
                violation_error_message="Genre with this name already exists (case-insensitive).",
            ),
        ]


class Language(models.Model):
    """Cet objet représente une langue (e.g. Anglais, Français, Japonais, etc.)."""

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a book language (e.g. English, French, Japanese)",
    )

    def __str__(self):
        """Cette fonction est obligatoirement requise par Django.
        Elle retourne une chaîne de caractère pour identifier l'instance de la classe d'objet.
        """
        return self.name

    def get_absolute_url(self):
        """Cette fonction est requise pas Django, lorsque vous souhaitez détailler le contenu d'un objet."""
        return reverse("language-detail", args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("name"),
                name="language_name_case_insensitive_unique",
                violation_error_message="Language with this name already exists (case-insensitive).",
            ),
        ]


class Book(models.Model):
    """Cet objet représente un livre (mais ne traite pas les copies présentes en rayon)."""

    title = models.CharField(max_length=200)

    # La clé étrangère (ForeignKey) est utilisée car elle représente correcte le modèle de relation en livre et son auteur :
    #  Un livre a un seul auteur, mais un auteur a écrit plusieurs livres.
    # Le type de l'objet Author est déclré comme une chaîne de caractère car
    # la classe d'objet Author n'a pas encore été déclarée dans le fichier
    author = models.ForeignKey("Author", on_delete=models.RESTRICT, null=True)

    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book"
    )
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>',
    )

    # Le type ManyToManyField décrit correctement le modèle de relation en un livre et un genre.
    #  un livre peut avoir plusieurs genres littéraire et réciproquement.
    # Comme la classe d'objets Genre a été définit précédemment, nous pouvons manipuler l'objet.
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")

    language = models.ForeignKey("Language", on_delete=models.SET_NULL, null=True)

    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["title", "author"]

    def display_genre(self):
        """Cette fonction est utilisée pour afficher le genre dans l'admin de Django."""
        return ", ".join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = "Genre"

    def __str__(self):
        """Fonction requise par Django pour manipuler les objets Book dans la base de données."""
        return self.title

    def get_absolute_url(self):
        """Cette fonction est requise pas Django, lorsque vous souhaitez détailler le contenu d'un objet."""
        return reverse("book-detail", kwargs={"stub": self.slug})


from datetime import date

from django.conf import settings  # Required to assign User as a borrower


class BookInstance(models.Model):
    """Cet objet permet de modéliser les copies d'un ouvrage (i.e. qui peut être emprunté)."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular book across whole library",
    )
    book = models.ForeignKey("Book", on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)

    LOAN_STATUS = (
        ("m", "Maintenance"),
        ("o", "On loan"),
        ("a", "Available"),
        ("r", "Reserved"),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default="m",
        help_text="Book availability",
    )

    class Meta:
        ordering = ["due_back"]

        permissions = (("can_mark_returned", "Set book as returned"),)

    def get_absolute_url(self):
        """Cette fonction est requise pas Django, lorsque vous souhaitez détailler le contenu d'un objet."""
        return reverse("bookinstance-detail", args=[str(self.id)])

    def __str__(self):
        """Fonction requise par Django pour manipuler les objets BookInstance dans la base de données."""
        return f"{self.id} ({self.book.title})"


class Author(models.Model):
    """Model representing an author."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField("born", null=True, blank=True)
    date_of_death = models.DateField("died", null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse("author-detail", args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.last_name}, {self.first_name}"
