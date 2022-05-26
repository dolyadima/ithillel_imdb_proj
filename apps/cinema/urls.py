from django.urls import path
from . import views

app_name = 'cinema'
urlpatterns = [
    path('', views.movies, name='movies'),
    path('persons/', views.persons, name='persons'),
    path('person_detail/<str:imdb_id>/', views.person_detail, name='person_detail'),
    path('<str:imdb_id>/', views.movie_detail, name='movie_detail'),
    path('<str:imdb_id>/edit_save=<int:edit_save>/', views.movie_detail, name='movie_detail'),
    path('<str:imdb_id>/edit_save=<int:edit_save>/b_page_number=<int:b_page_number>', views.movie_detail, name='movie_detail'),
]
