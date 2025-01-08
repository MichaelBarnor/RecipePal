from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import Recipe, RecipeFile, CollaborationRequest
from .forms import RecipeForm, CollaboratorForm
from django.views import generic
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Message


class DetailView(generic.DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.object

        if self.request.user.groups.filter(name="PMA Administrators").exists():
            context['messages'] = recipe.messages.all()
            context['admin'] = True
        elif recipe.creator == self.request.user or recipe.accessible_users.filter(id=self.request.user.id).exists():
            context['messages'] = recipe.messages.all()
            context['public_view'] = False
        else:
            context['public_view'] = True

        pending_collaboration_requests = CollaborationRequest.objects.filter(recipe=recipe)
        collaboration_request = CollaborationRequest.objects.filter(recipe=recipe, user=self.request.user).exists()

        context['form'] = CollaboratorForm(recipe=recipe)
        context['pending_collaboration_requests'] = pending_collaboration_requests
        context['collaboration_request'] = collaboration_request

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if 'action' in request.POST:
            action = request.POST['action']
            if action == 'file':
                RecipeFile.objects.create(
                    recipe=self.object,
                    file=request.FILES.get('file_upload'),
                    file_title=request.POST.get('file_title'),
                    file_description=request.POST.get('file_description'),
                    keywords=request.POST.get('keywords'),
                    uploader=request.user,
                )
            elif action == 'message':
                if request.user == self.object.creator or self.object.accessible_users.filter(id=request.user.id).exists():
                    message = Message.objects.create(
                        recipe=self.object,
                        author=request.user,
                        content=request.POST['message']
                    )
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'success',
                            'message': {
                                'content': message.content,
                                'author': message.author.username,
                                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                            }
                        })
            return redirect('recipes:recipe_detail', pk=self.object.pk)

        else:
            form = CollaboratorForm(request.POST, recipe=self.object)
            if form.is_valid():
                user_ids = form.cleaned_data['accessible_users']
                for user in user_ids:
                    self.object.accessible_users.add(user)
                self.object.save()
                return redirect('recipes:recipe_detail', pk=self.object.pk)

        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        return Recipe.objects.all()

    def get(self, request, *args, **kwargs):
        # get the recipe object
        self.object = self.get_object()

        # check if the user is a PMA admin
        if self.request.user.groups.filter(name="PMA Administrators").exists():
            context = {
                'messages' : self.object.messages.all(),
                'recipe': self.object,
                'admin': True,
                'collaboration_request' : CollaborationRequest.objects.filter(recipe=self.object, user=self.request.user).exists()
            }
            return self.render_to_response(context)

        # check if the user is the creator or a collaborator
        elif self.object.creator != request.user and not self.object.accessible_users.filter(id=request.user.id).exists():
            context = {
                'messages' : self.object.messages.all(),
                'recipe': self.object,
                'public_view': True,
                'collaboration_request': CollaborationRequest.objects.filter(recipe=self.object,
                                                                             user=self.request.user).exists()
            }
            return self.render_to_response(context)

        # allow full access
        form = CollaboratorForm()
        form.fields['accessible_users'].queryset = User.objects.exclude(id=request.user.id)  # exclude the creator
        context = self.get_context_data(object=self.object, form=form)
        context['public_view'] = False
        return self.render_to_response(context)


def recipe_file_detail(request, file_id):
    recipe_file = get_object_or_404(RecipeFile, pk=file_id)
    context = {'recipe_file': recipe_file}
    return render(request, 'recipes/recipe_file_detail.html', context)


@login_required
def project_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # only owner should be able to delete project
    if recipe.creator != request.user and not request.user.groups.filter(name="PMA Administrators").exists():
        return HttpResponseForbidden("Permission Denied! You are not allowed to delete this project.")

    recipe_files = RecipeFile.objects.filter(recipe=recipe)

    for file_object in recipe_files:
        file_object.delete()

    recipe.delete()
    return redirect('recipes:all_recipes')


@login_required
def file_delete(request, file_id):
    recipe_file = get_object_or_404(RecipeFile, id=file_id)

    # Members and PMA admins should be allowed to delete the files they uploaded
    if recipe_file.uploader != request.user and not request.user.groups.filter(name="PMA Administrators").exists():
        return HttpResponseForbidden("Permission Denied! You are not allowed to delete this file.")

    recipe_file.delete()
    return redirect('recipes:recipe_detail', pk=recipe_file.recipe.id)


# VIEWS FOR HANDLING ACCESS TO RECIPES
@login_required
def request_collaboration(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Ensure the user is not already a collaborator
    if recipe.creator == request.user:
        return HttpResponseForbidden("You are the creator of this recipe.")
    if recipe.accessible_users.filter(id=request.user.id).exists():
        return HttpResponseForbidden("You are already a collaborator on this recipe.")

    # Check if a request already exists
    existing_request = CollaborationRequest.objects.filter(recipe=recipe, user=request.user)
    if existing_request:
        messages.info(request, "Your request is pending.")
        return redirect('recipes:recipe_detail', pk=recipe.id)

    # Create a new collaboration request
    CollaborationRequest.objects.create(recipe=recipe, user=request.user)

    messages.success(request, "Your collaboration request has been sent to the creator.")
    return redirect('recipes:recipe_detail', pk=recipe.id)


@login_required
def manage_collaboration_request(request, request_id, action):
    collaboration_request = get_object_or_404(CollaborationRequest, id=request_id)

    if collaboration_request.recipe.creator != request.user:
        return HttpResponseForbidden("Only the creator can manage requests.")

    if action == 'approve':
        collaboration_request.recipe.accessible_users.add(collaboration_request.user)
        messages.success(request, f'You have approved {collaboration_request.user.username} as a collaborator.')
    elif action == 'deny':
        messages.success(request, f'You have denied {collaboration_request.user.username} access.')

    collaboration_request.delete()
    return redirect('recipes:recipe_detail', pk=collaboration_request.recipe.id)


@login_required
def remove_collaborator(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.user == recipe.creator:
        messages.error(request, "You are the creator of this recipe and cannot remove yourself.")
        return redirect('recipes:recipe_detail', pk=recipe.id)

    if not recipe.accessible_users.filter(id=request.user.id).exists():
        messages.error(request, "You are not a collaborator on this recipe.")
        return redirect('recipes:recipe_detail', pk=recipe.id)

    recipe.accessible_users.remove(request.user)
    messages.success(request, "You have successfully removed yourself as a collaborator.")

    return redirect('recipes:my_recipes')


def all_recipes(request):
    """View to display all recipes with collaboration status and search functionality."""
    search_query = request.GET.get('q', '')  # Get the search query from GET parameters

    if search_query:
        latest_recipe_list = Recipe.objects.filter(title_text__icontains=search_query).order_by('-pub_date')
    else:
        latest_recipe_list = Recipe.objects.all().order_by('-pub_date')

    for recipe in latest_recipe_list:
        recipe.is_owner = (recipe.creator == request.user)
        recipe.is_accessible = recipe.accessible_users.filter(id=request.user.id).exists()
        recipe.has_pending_collaboration_requests = CollaborationRequest.objects.filter(recipe=recipe).exists()

    context = {
        'latest_recipe_list': latest_recipe_list,
        'search_query': search_query  # Pass the search query back to the template
    }
    return render(request, 'recipes/all_recipes.html', context)


@login_required
def my_recipes(request):
    """View to display recipes created by or shared with the user."""
    my_recipe_list = Recipe.objects.filter(
        Q(creator=request.user) | Q(accessible_users=request.user)
    ).distinct().order_by('-pub_date')

    for recipe in my_recipe_list:
        recipe.is_owner = (recipe.creator == request.user)
        recipe.is_accessible = recipe.accessible_users.filter(id=request.user.id).exists()
        recipe.has_pending_collaboration_requests = CollaborationRequest.objects.filter(recipe=recipe).exists()

    context = {'my_recipe_list': my_recipe_list}
    return render(request, 'recipes/my_recipes.html', context)


@login_required
def add_recipe(request):
    """View to handle adding a new recipe."""
    if request.user.groups.filter(name="PMA Administrators").exists():
        context = {
            'admin': True
        }
        return render(request, 'recipes/add_recipe.html', context)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        file_uploads = request.FILES.getlist('file_upload')
        file_titles = request.POST.getlist('file_title')
        file_descriptions = request.POST.getlist('file_description')
        keywords_list = request.POST.getlist('keywords')

        # Initialize a flag to track file-related validation errors
        file_errors = False

        # Only validate file metadata if there are files uploaded
        if file_uploads:
            # Check if the number of file-related fields matches the number of file uploads
            if len(file_uploads) != len(file_titles) or len(file_uploads) != len(file_descriptions) or len(file_uploads) != len(keywords_list):
                messages.error(request, "Mismatch in the number of files and their associated metadata fields.")
                return render(request, 'recipes/add_recipe.html', {'form': form})

            # Validate that for each uploaded file, its related fields are provided
            for i in range(len(file_uploads)):
                file_title = file_titles[i].strip()
                file_description = file_descriptions[i].strip()
                keywords = keywords_list[i].strip()

                if not file_title or not file_description or not keywords:
                    file_errors = True
                    messages.error(request, f"All file fields (title, description, keywords) are required for each uploaded file.")
                    break

        # Process the form and files if the form is valid and no file errors are detected
        if form.is_valid() and not file_errors:
            # Create a new Recipe object without saving to the database yet
            recipe = form.save(commit=False)
            recipe.creator = request.user
            recipe.save()

            # Handle multiple file uploads
            for i in range(len(file_uploads)):
                RecipeFile.objects.create(
                    recipe=recipe,
                    file=file_uploads[i],
                    file_title=file_titles[i],
                    file_description=file_descriptions[i],
                    keywords=keywords_list[i],
                    uploader=request.user,
                )

            messages.success(request, "Recipe added successfully!")
            return redirect('recipes:recipe_detail', pk=recipe.pk)  # Using pk=recipe.pk
        else:
            # Form is not valid or there are file-related errors, display errors
            if not form.is_valid():
                messages.error(request, "Please correct the errors below.")
    else:
        form = RecipeForm()

    context = {'form': form}
    return render(request, 'recipes/add_recipe.html', context)


@login_required
def recipe_page(request):
    """Redirects to the 'all_recipes' view."""
    return redirect('recipes:all_recipes')  # Redirect to 'all_recipes' instead of 'recipe_page'
