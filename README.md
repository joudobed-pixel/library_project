# Library Management System API

A RESTful API built with **Django** and **Django REST Framework** for a library.
Anyone can browse and search books; only administrators can add, update and
delete records. Users register and log in with **JWT** tokens.

Concepts covered: **Models · Admin · Serializers · Views · Authentication**.

## Features

- Three related models: `Author`, `Category`, `Book` (each book has one author and one category)
- Unique ISBN and non-negative available copies (validated in the serializer)
- Customised Django admin: list display, search (title, ISBN), filters (author, category, publication date)
- Admin theme with **django-admin-interface**
- Full CRUD with `ModelViewSet` + router
- Search by title, filter by author/category, pagination (5 per page)
- Registration with hashed passwords, JWT login/refresh, profile endpoint
- Role-based permissions (guest / user / admin) with correct 401 and 403 responses
- Automated tests (`APITestCase`) and a ready Postman collection

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_library     # optional sample data
python manage.py createsuperuser  # admin account
python manage.py runserver
```

- API root: http://127.0.0.1:8000/api/
- Admin panel: http://127.0.0.1:8000/admin/

## Admin theme (django-admin-interface)

The theme is already configured in `settings.py` (`admin_interface` and
`colorfield` are added before `django.contrib.admin`, plus
`X_FRAME_OPTIONS = "SAMEORIGIN"`). After `pip install -r requirements.txt` and
`python manage.py migrate`, open **/admin/ → Admin Interface → Themes** to change
the title, logo, colours and dark mode.

## Endpoints

| Method | Endpoint | Action | Access |
|---|---|---|---|
| GET | `/api/books/` | List books (`?search=`, `?author=`, `?category=`, `?page=`) | Everyone |
| GET | `/api/books/{id}/` | Book details | Everyone |
| POST | `/api/books/` | Create book | Admin |
| PUT / PATCH | `/api/books/{id}/` | Replace / partially update book | Admin |
| DELETE | `/api/books/{id}/` | Delete book | Admin |
| GET / POST | `/api/authors/` | List / create authors | Read: everyone · Write: admin |
| GET / PUT / DELETE | `/api/authors/{id}/` | Author details / update / delete | Read: everyone · Write: admin |
| GET / POST | `/api/categories/` | List / create categories | Read: everyone · Write: admin |
| GET / PUT / DELETE | `/api/categories/{id}/` | Category details / update / delete | Read: everyone · Write: admin |
| POST | `/api/register/` | Register user | Everyone |
| POST | `/api/login/` | Get JWT access + refresh tokens | Everyone |
| POST | `/api/token/refresh/` | Refresh access token | Everyone |
| GET | `/api/profile/` | Current user profile | Logged-in users |

Send the token in the header: `Authorization: Bearer <access_token>`.

## Permissions

| Operation | Guest | User | Admin |
|---|---|---|---|
| View / search books | ✅ | ✅ | ✅ |
| View authors / categories | ✅ | ✅ | ✅ |
| Create / update / delete books | ❌ 401 | ❌ 403 | ✅ |
| Manage authors / categories | ❌ 401 | ❌ 403 | ✅ |
| View own profile | ❌ 401 | ✅ | ✅ |

## Status codes

`200` OK · `201` Created · `204` Deleted · `400` Invalid data (duplicate ISBN, negative copies,
deleting an author/category still used by books) · `401` Missing/invalid token ·
`403` Logged in without permission · `404` Not found

## Example

`POST /api/books/` (admin)

```json
{
  "title": "Clean Code",
  "author": 1,
  "category": 2,
  "isbn": "9780132350884",
  "description": "A book about writing clean and maintainable code.",
  "published_date": "2008-08-01",
  "available_copies": 5
}
```

Response `201 Created` – the same fields plus `id`, `author_detail`, `category_detail`,
`created_at` and `updated_at`.

## Testing

Automated tests:

```bash
python manage.py test
```

Postman: import `Library_API.postman_collection.json`, set your admin password in
**Login admin (JWT)**, then run the requests from top to bottom. Login requests save
the tokens automatically into the collection variables.

## Project structure

```
library_project/
  manage.py
  requirements.txt
  Library_API.postman_collection.json
  library_project/   settings.py, urls.py, asgi.py, wsgi.py
  books/             models.py, admin.py, serializers.py, views.py, urls.py,
                     permissions.py, tests.py, management/commands/seed_library.py
  accounts/          serializers.py, views.py, urls.py, tests.py
```
