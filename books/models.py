from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    # PROTECT: an author/category that still has books cannot be deleted.
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="books")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="books")
    isbn = models.CharField("ISBN", max_length=13, unique=True)
    description = models.TextField(blank=True)
    published_date = models.DateField()
    available_copies = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title
