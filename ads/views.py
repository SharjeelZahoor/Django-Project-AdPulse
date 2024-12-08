from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.generic import  DetailView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.exceptions import ValidationError
from .models import Ad, Comment, Favorite
from .forms import AdForm, CommentForm
from django.views import View
from django.db import models
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def naturaltime(value):
    now = timezone.now()
    diff = now - value

    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"

def custom_logout(request):
    logout(request)
    return redirect('/ads/')

# File size validator
def validate_file_size(value):
    limit = 2 * 1024 * 1024  # 2MB
    if value.size > limit:
        raise ValidationError("File size exceeds 2MB")




# Picture
def ad_picture(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if not ad.picture:
        return HttpResponse(status=404)
    return HttpResponse(ad.picture, content_type='image/jpeg')



import logging

logger = logging.getLogger(__name__)

# Helper function for natural time

# ListView for Ads with updated search functionality
from django.core.paginator import Paginator

class AdListView(View):
    template_name = 'ads/ad_list.html'

    def get_queryset(self, search_value):
    # Step 1: Build query using Q objects
        query = Q()
        if search_value:
            for term in search_value.split():
                query |= Q(title__icontains=term) | Q(text__icontains=term) | Q(tags__name__icontains=term)

    # Step 2: Filter ads based on the query
        filtered_ads = Ad.objects.filter(query).select_related("owner").prefetch_related("tags")

    # Step 3: Annotate distinct comments and ensure unique ads
        filtered_ads = (
            filtered_ads.annotate(num_comments=models.Count("ad_comments", distinct=True))
            .distinct()
            .order_by("-updated_at")
        )

        return filtered_ads


    def get(self, request):
        # Get the search term from the GET request
        strval = request.GET.get("search", "").strip()
        queryset = self.get_queryset(strval)

        # Paginate the queryset to limit results per page
        paginator = Paginator(queryset, 10)  # Show 10 ads per page
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        # Add natural time formatting for each ad
        for ad in page_obj:
            ad.natural_updated = naturaltime(ad.updated_at)

        # Prepare the context for rendering
        ctx = {
            "ad_list": page_obj,
            "search": strval,  # Include the search term for display
        }

        # Add user favorites if the user is authenticated
        if request.user.is_authenticated:
            ctx["favorites"] = list(request.user.favorite_ads.values_list("id", flat=True))
        else:
            ctx["favorites"] = []

        # Render the template with the context
        return render(request, self.template_name, ctx)



class AdDetailView(DetailView):
    model = Ad
    template_name = 'ads/ad_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = Comment.objects.filter(ad=self.object).order_by('-id')
        context.pop('owner', None)  # Ensure 'owner' is not part of the context data
        return context

    def post(self, request, *args, **kwargs):
        ad = self.get_object
        ad = self.get_object()
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ad = ad
            comment.owner = request.user
            comment.save()
            return redirect('ads:ad_detail', pk=ad.pk)

        context = self.get_context_data(**kwargs)
        context['comment_form'] = comment_form
        return self.render_to_response(context)

class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:ad_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user  # Assign owner
        return super().form_valid(form)

class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Ad
    form_class = AdForm
    template_name = 'ads/ad_form.html'
    success_url = reverse_lazy('ads:ad_list')

class AdDeleteView(LoginRequiredMixin, DeleteView):
    model = Ad
    template_name = 'ads/ad_confirm_delete.html'
    success_url = reverse_lazy('ads:ad_list')

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.ad = get_object_or_404(Ad, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ads:ad_detail', kwargs={'pk': self.object.ad.id})

class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'ads/ad_comment.html'

    def get_success_url(self):
        return reverse_lazy('ads:ad_detail', kwargs={'pk': self.object.ad.id})

def stream_file(request, pk):
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse(ad.picture, content_type=ad.picture.file.content_type)
    response['Content-Length'] = ad.picture.size
    return response


from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("Add PK", pk)
        t = get_object_or_404(Ad, id=pk)  # Fetch the Ad object
        fav = Favorite(user=request.user, ad=t)  # Use 'ad' field
        try:
            fav.save()  # Save the favorite entry
        except IntegrityError as e:
            print(f"IntegrityError: {e}")  # Log integrity errors
            return JsonResponse({'error': 'Duplicate favorite entry'}, status=400)
        except Exception as e:
            print(f"Unexpected error: {e}")  # Catch unexpected errors
            return JsonResponse({'error': 'Unexpected server error'}, status=500)

        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("Delete PK", pk)
        t = get_object_or_404(Ad, id=pk)  # Fetch the Ad object
        try:
            Favorite.objects.get(user=request.user, ad=t).delete()  # Use 'ad' field
        except Favorite.DoesNotExist:
            print("Favorite entry does not exist.")
            pass
        except Exception as e:
            print(f"Unexpected error: {e}")  # Log unexpected errors
            return JsonResponse({'error': 'Unexpected server error'}, status=500)

        return HttpResponse()



