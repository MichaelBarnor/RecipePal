from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage


class Recipe(models.Model):
    title_text = models.CharField(max_length=200)
    pub_date = models.DateField("date published", auto_now_add=True)
    description_text = models.CharField(max_length=200)
    calories_text = models.IntegerField(
        validators=[MinValueValidator(0)],
        blank=False,  # Make it required
        null=False
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        blank=False,  # Make it required
        null=False
    )
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    accessible_users = models.ManyToManyField(User, related_name='accessible_recipes', blank=True)

    def __str__(self):
        return self.title_text


class RecipeFile(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    file_title = models.CharField(max_length=100)
    file_description = models.TextField()
    submission_timestamp = models.DateTimeField(auto_now_add=True)
    keywords = models.CharField(max_length=200)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  

    def __str__(self):
        return self.file_title

    # delete file from s3
    def delete(self, *args, **kwargs):
        default_storage.delete(self.file.name)
        super().delete(*args, **kwargs)



class CollaborationRequest(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='collaboration_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collaboration_requests')

    class Meta:
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f'{self.user.username} requesting access to {self.recipe.title_text}'


class Message(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Message by {self.author.username} on {self.recipe.title_text}'