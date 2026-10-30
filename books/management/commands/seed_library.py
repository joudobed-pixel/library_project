"""Create sample authors, categories and books:  python manage.py seed_library"""

from datetime import date

from django.core.management.base import BaseCommand

from books.models import Author, Book, Category

AUTHORS = [
    ("Robert C. Martin", "Software engineer and author of books on clean code.", date(1952, 12, 5)),
    ("Andrew Hunt", "Co-author of The Pragmatic Programmer.", date(1964, 1, 1)),
    ("Wes McKinney", "Creator of the pandas library.", date(1985, 3, 1)),
    ("Cal Newport", "Computer science professor and writer.", date(1982, 6, 23)),
]
CATEGORIES = [
    ("Programming", "Software development and coding practices."),
    ("Data Science", "Data analysis, statistics and machine learning."),
    ("Productivity", "Focus, habits and work performance."),
]
BOOKS = [
    ("Clean Code", 0, 0, "9780132350884", date(2008, 8, 1), 5),
    ("The Clean Coder", 0, 0, "9780137081073", date(2011, 5, 13), 3),
    ("Clean Architecture", 0, 0, "9780134494166", date(2017, 9, 10), 4),
    ("The Pragmatic Programmer", 1, 0, "9780135957059", date(2019, 9, 13), 6),
    ("Python for Data Analysis", 2, 1, "9781098104030", date(2022, 8, 30), 7),
    ("Deep Work", 3, 2, "9781455586691", date(2016, 1, 5), 2),
    ("Digital Minimalism", 3, 2, "9780525536512", date(2019, 2, 5), 0),
]


class Command(BaseCommand):
    help = "Create sample library data (safe to run more than once)."

    def handle(self, *args, **options):
        authors = [Author.objects.get_or_create(name=n, defaults={"biography": b, "birth_date": d})[0]
                   for n, b, d in AUTHORS]
        categories = [Category.objects.get_or_create(name=n, defaults={"description": d})[0]
                      for n, d in CATEGORIES]
        for title, a, c, isbn, published, copies in BOOKS:
            Book.objects.get_or_create(isbn=isbn, defaults={
                "title": title, "author": authors[a], "category": categories[c],
                "description": f"Sample description of {title}.",
                "published_date": published, "available_copies": copies,
            })
        self.stdout.write(self.style.SUCCESS(
            f"{Author.objects.count()} authors, {Category.objects.count()} categories, {Book.objects.count()} books."
        ))
