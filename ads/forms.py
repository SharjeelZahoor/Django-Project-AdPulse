from django import forms
from .models import Ad, Comment
from taggit.forms import TagField
from taggit.models import Tag
import logging

logger = logging.getLogger(__name__)

# Utility function to validate file size
def validate_file_size(file):
    if file.size > 2 * 1024 * 1024:  # 2MB limit
        raise forms.ValidationError("File size exceeds the limit of 2MB.")

class AdForm(forms.ModelForm):
    tags = TagField(help_text="Enter tags separated by commas.")  # TagField to manage tags input

    class Meta:
        model = Ad
        fields = ['title', 'text', 'price', 'picture', 'tags']

    def form_valid(self, form):
        try:
            form.instance.owner = self.request.user
            picture = form.cleaned_data.get('picture')

            if picture:
                validate_file_size(picture)

            logger.debug(f"Form data: {form.cleaned_data}")
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Error in form_valid: {e}")
            raise

    def clean_tags(self):
        tags_input = self.cleaned_data.get('tags', '')

        if isinstance(tags_input, list):
            tag_names = [name.strip() for name in tags_input if name.strip()]
        else:
            tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]

        return tag_names  # Return cleaned tag names as a list


    def clean_picture(self):
        """
        Validate the picture field for size limits.
        """
        picture = self.cleaned_data.get('picture')
        if picture:
            validate_file_size(picture)
        return picture

    def save(self, commit=True):
        """
        Custom save method to handle the saving of tags and other related data.
        """
        instance = super().save(commit=False)  # Save without committing to add extra processing
        if commit:
            instance.save()
            self.save_m2m()  # Save tags relation
        return instance


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']  # Only the 'comment' field is editable
