from rest_framework import serializers

from .models import Author, Book, Category


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name", "biography", "birth_date"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class BookSerializer(serializers.ModelSerializer):
    # Write: send author/category IDs.  Read: IDs + nested details.
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    author_detail = AuthorSerializer(source="author", read_only=True)
    category_detail = CategorySerializer(source="category", read_only=True)

    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "author_detail", "category", "category_detail",
            "isbn", "description", "published_date", "available_copies",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        # Uniqueness is checked in validate_isbn() with a clearer message.
        extra_kwargs = {"isbn": {"validators": []}}

    def validate_isbn(self, value):
        value = value.replace("-", "").strip()
        if not value.isdigit() or len(value) not in (10, 13):
            raise serializers.ValidationError("ISBN must contain 10 or 13 digits.")
        duplicates = Book.objects.filter(isbn=value)
        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError("A book with this ISBN already exists.")
        return value

    def validate_available_copies(self, value):
        if value < 0:
            raise serializers.ValidationError("Available copies cannot be negative.")
        return value
