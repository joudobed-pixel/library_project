from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Library Management System"
admin.site.site_title = "Library Admin"
admin.site.index_title = "Library administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("books.urls")),
    path("api/", include("accounts.urls")),
]
