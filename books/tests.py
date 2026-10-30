from datetime import date

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Author, Book, Category


class BookAPITests(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Robert C. Martin")
        self.other_author = Author.objects.create(name="Cal Newport")
        self.category = Category.objects.create(name="Programming")
        self.book = Book.objects.create(
            title="Clean Code", author=self.author, category=self.category,
            isbn="9780132350884", published_date=date(2008, 8, 1), available_copies=5,
        )
        for i in range(6):  # extra books to test pagination
            Book.objects.create(title=f"Book {i}", author=self.other_author, category=self.category,
                                isbn=f"978000000000{i}", published_date=date(2020, 1, 1))
        self.admin = User.objects.create_user("admin1", password="StrongPass!234", is_staff=True)
        self.user = User.objects.create_user("student1", password="StrongPass!234")
        self.payload = {
            "title": "Deep Work", "author": self.other_author.id, "category": self.category.id,
            "isbn": "9781455586691", "description": "Focus.", "published_date": "2016-01-05",
            "available_copies": 2,
        }

    # --- Guests -----------------------------------------------------------
    def test_guest_can_list_books(self):
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 7)

    def test_guest_cannot_create_book(self):
        response = self.client.post("/api/books/", self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Permissions -------------------------------------------------------
    def test_regular_user_cannot_delete_book(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"/api/books/{self.book.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_update_delete(self):
        self.client.force_authenticate(self.admin)
        created = self.client.post("/api/books/", self.payload, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        book_id = created.data["id"]
        patched = self.client.patch(f"/api/books/{book_id}/", {"available_copies": 9}, format="json")
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(patched.data["available_copies"], 9)
        deleted = self.client.delete(f"/api/books/{book_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)

    # --- Validation --------------------------------------------------------
    def test_duplicate_isbn_rejected(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/books/", {**self.payload, "isbn": "9780132350884"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("isbn", response.data)

    def test_negative_copies_rejected(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post("/api/books/", {**self.payload, "available_copies": -1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("available_copies", response.data)

    def test_nonexistent_book_returns_404(self):
        self.assertEqual(self.client.get("/api/books/9999/").status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_author_with_books(self):
        self.client.force_authenticate(self.admin)
        response = self.client.delete(f"/api/authors/{self.author.id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Search, filter, pagination ----------------------------------------
    def test_search_by_title(self):
        response = self.client.get("/api/books/?search=clean")
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_author(self):
        response = self.client.get(f"/api/books/?author={self.other_author.id}")
        self.assertEqual(response.data["count"], 6)

    def test_pagination(self):
        response = self.client.get("/api/books/")
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])
