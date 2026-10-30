from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Author, Book, Category
from .permissions import IsAdminOrReadOnly
from .serializers import AuthorSerializer, BookSerializer, CategorySerializer


class BookViewSet(viewsets.ModelViewSet):
    """
    /api/books/  — list, create, retrieve, update (PUT/PATCH), delete.
    Search:  ?search=clean        (title)
    Filter:  ?author=1&category=2
    Page:    ?page=2              (5 books per page)
    """

    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["title"]
    ordering_fields = ["title", "published_date", "available_copies"]

    def get_queryset(self):
        queryset = Book.objects.select_related("author", "category").all()
        params = self.request.query_params
        for field in ("author", "category"):
            value = params.get(field)
            if value:
                if not value.isdigit():
                    return Book.objects.none()
                queryset = queryset.filter(**{f"{field}_id": int(value)})
        return queryset


class ProtectedDeleteMixin:
    """Return 400 instead of a server error when the record is still used by books."""

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "This record cannot be deleted because books still reference it."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AuthorViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]


class CategoryViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
