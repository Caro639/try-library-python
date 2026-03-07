import datetime
import uuid

from django.test import TestCase

from catalog.models import Author, Book, BookInstance, Genre, Language


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Author.objects.create(first_name="Big", last_name="Bob")

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field("first_name").verbose_name
        self.assertEqual(field_label, "first name")

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field("last_name").verbose_name
        self.assertEqual(field_label, "last name")

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field("date_of_death").verbose_name
        self.assertEqual(field_label, "died")

    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field("date_of_birth").verbose_name
        self.assertEqual(field_label, "born")

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field("first_name").max_length
        self.assertEqual(max_length, 100)

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field("last_name").max_length
        self.assertEqual(max_length, 100)

    def test_date_of_death_blank(self):
        author = Author.objects.get(id=1)
        blank = author._meta.get_field("date_of_death").blank
        self.assertTrue(blank)

    def test_date_of_birth_blank(self):
        author = Author.objects.get(id=1)
        blank = author._meta.get_field("date_of_birth").blank
        self.assertTrue(blank)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f"{author.last_name}, {author.first_name}"
        self.assertEqual(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(author.get_absolute_url(), "/catalog/author/1")


class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        author = Author.objects.create(first_name="Big", last_name="Bob")
        Book.objects.create(
            title="Book Title",
            author=author,
            summary="My book summary",
            isbn="ABCDEFGHIJKLM",
        )

    def test_title_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "title")

    def test_summary_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field("summary").verbose_name
        self.assertEqual(field_label, "summary")

    def test_isbn_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field("isbn").verbose_name
        self.assertEqual(field_label, "ISBN")

    def test_title_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field("title").max_length
        self.assertEqual(max_length, 200)

    def test_isbn_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field("isbn").max_length
        self.assertEqual(max_length, 13)

    def test_ordering(self):
        ordering = Book._meta.ordering
        self.assertEqual(ordering, ["title", "author"])

    def test_slug_is_generated_on_save(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.slug, "book-title")

    def test_slug_is_updated_on_title_change(self):
        book = Book.objects.get(id=1)
        book.title = "New Title"
        book.save()
        self.assertEqual(book.slug, "new-title")

    def test_get_absolute_url(self):
        book = Book.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(book.get_absolute_url(), f"/catalog/book/{book.slug}")


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name="Science Fiction")

    def test_name_max_length(self):
        genre = Genre.objects.get(id=1)
        max_length = genre._meta.get_field("name").max_length
        self.assertEqual(max_length, 200)

    def test_name_unique(self):
        unique = Genre._meta.get_field("name").unique
        self.assertTrue(unique)

    def test_object_name_is_name(self):
        genre = Genre.objects.get(id=1)
        self.assertEqual(str(genre), "Science Fiction")


class LanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Language.objects.create(name="English")

    def test_name_max_length(self):
        language = Language.objects.get(id=1)
        max_length = language._meta.get_field("name").max_length
        self.assertEqual(max_length, 200)

    def test_name_unique(self):
        unique = Language._meta.get_field("name").unique
        self.assertTrue(unique)

    def test_object_name_is_name(self):
        language = Language.objects.get(id=1)
        self.assertEqual(str(language), "English")


class BookInstanceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(first_name="Big", last_name="Bob")
        book = Book.objects.create(
            title="Book Title",
            author=author,
            summary="My book summary",
            isbn="ABCDEFGHIJKLM",
        )
        BookInstance.objects.create(
            id=uuid.UUID("4e6ce5a8-3b0a-4c5a-9b4c-1a2b3c4d5e6f"),
            book=book,
            imprint="Test Imprint",
        )

    def test_due_back_blank(self):
        instance = BookInstance.objects.get(id="4e6ce5a8-3b0a-4c5a-9b4c-1a2b3c4d5e6f")
        blank = instance._meta.get_field("due_back").blank
        self.assertTrue(blank)

    def test_status_default_is_maintenance(self):
        instance = BookInstance.objects.get(id="4e6ce5a8-3b0a-4c5a-9b4c-1a2b3c4d5e6f")
        self.assertEqual(instance.status, "m")

    def test_ordering(self):
        self.assertEqual(BookInstance._meta.ordering, ["due_back"])

    def test_object_name(self):
        instance = BookInstance.objects.get(id="4e6ce5a8-3b0a-4c5a-9b4c-1a2b3c4d5e6f")
        expected = f"{instance.id} ({instance.book.title})"
        self.assertEqual(str(instance), expected)

    def test_is_overdue_false_when_no_due_date(self):
        instance = BookInstance.objects.get(id="4e6ce5a8-3b0a-4c5a-9b4c-1a2b3c4d5e6f")
        self.assertFalse(instance.is_overdue)

    def test_is_overdue_false_when_due_in_future(self):
        instance = BookInstance.objects.get(id="4e6ce5a8-3b0a-4c5a-9b4c-1a2b3c4d5e6f")
        instance.due_back = datetime.date.today() + datetime.timedelta(days=1)
        self.assertFalse(instance.is_overdue)

    def test_is_overdue_true_when_due_in_past(self):
        instance = BookInstance.objects.get(id="4e6ce5a8-3b0a-4c5a-9b4c-1a2b3c4d5e6f")
        instance.due_back = datetime.date.today() - datetime.timedelta(days=1)
        self.assertTrue(instance.is_overdue)
