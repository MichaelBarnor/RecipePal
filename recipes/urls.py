from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    # New URL patterns
    path('all/', views.all_recipes, name='all_recipes'),
    path('my/', views.my_recipes, name='my_recipes'),
    path('add/', views.add_recipe, name='add_recipe'),

    # Existing URL patterns
    path('<int:pk>/', views.DetailView.as_view(), name='recipe_detail'),
    path('file/<int:file_id>/', views.recipe_file_detail, name='recipe_file_detail'),
    path('<int:recipe_id>/delete/', views.project_delete, name='project_delete'),
    path('file/<int:file_id>/delete/', views.file_delete, name='file_delete'),
    path('recipe/<int:recipe_id>/request_collaboration/', views.request_collaboration, name='request_collaboration'),
    path('file/<int:request_id>/<str:action>', views.manage_collaboration_request, name='manage_collaboration_request'),
    path('recipe/<int:recipe_id>/remove_collaborator/', views.remove_collaborator, name='remove_collaborator'),
    
    # Optional: Redirect the base URL to 'all_recipes'
    # This ensures that accessing the base URL shows all recipes
    path('', views.all_recipes, name='recipe_page'),
]
