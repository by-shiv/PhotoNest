from django.shortcuts import render, redirect, get_object_or_404
from .models import ImageUpload, Album, GeneratedImage
from .forms import ImageUploadForm, AlbumForm
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST
import json
from .models import UserProfile
from django import forms
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, FileResponse
from threading import Thread
from collections import defaultdict
from .services.image_processing import compress_image
from collections import OrderedDict
from .services.search import smart_search_filter, get_similar_images
from .services.blip_model import generate_caption
from .services.clip_model import get_image_embedding
from .services.tag_pipeline import generate_tags_from_caption, clean_caption
import random, os, time
from collections import Counter
from .services.generation import generate_image_from_prompt, build_advanced_prompt
from .services.search import get_related_images_for_generation
from django.conf import settings
from django.core.files.base import ContentFile
from .models import GeneratedImage, ImageUpload


def _split_tags(raw):
    if not raw:
        return []
    return [t.strip() for t in raw.split(",") if t.strip()]


def _normalized_tags(raw):
    if not raw:
        return []
    return [t.strip().lower() for t in raw.split(",") if t.strip()]

@login_required
def image_detail(request, image_id):
    image = get_object_or_404(
        ImageUpload,
        id=image_id,
        user=request.user
    )

    album_list = Album.objects.filter(
        user=request.user,
        images=image
    ).order_by("-created_date")

    all_images = ImageUpload.objects.filter(
    user=request.user,
    trashed=False
    )

    similar_images = get_similar_images(image, all_images, top_k=8)
    tags_list = _split_tags(image.tags)
    ai_tags_list = _split_tags(image.ai_tags)

    return render(request, "gallery/image_detail.html", {
        "image": image,
        "album_list": album_list,
        "similar_images": similar_images,
        "tags_list": tags_list,
        "ai_tags_list": ai_tags_list,
    })


def update_image(request, image_id):
    if request.method == "POST":
        data = json.loads(request.body)

        image = ImageUpload.objects.get(id=image_id)

        image.title = data.get("title", image.title)
        image.description = data.get("description", image.description)
        image.tags = data.get("tags", image.tags)

        image.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})

@login_required
def download_image(request, image_id):
    image = get_object_or_404(
        ImageUpload,
        id=image_id,
        user=request.user
    )

    if not image.image:
        return HttpResponseForbidden("No image file found.")

    filename = image.image.name.split("/")[-1]
    return FileResponse(
        image.image.open("rb"),
        as_attachment=True,
        filename=filename
    )


@login_required
def gallery_home(request):
    images = ImageUpload.objects.filter(
       user=request.user,
       trashed=False,
       archived=False
    ).only("id", "image", "upload_date", "title").order_by('-upload_date')

    temp = defaultdict(list)

    for img in images:
        month = img.upload_date.strftime("%Y-%m")
        temp[month].append(img)

    sorted_months = sorted(temp.keys(), reverse=True)
    images_by_month = OrderedDict()

    for month in sorted_months:
        readable = temp[month][0].upload_date.strftime("%B %Y")
        images_by_month[readable] = temp[month]

    highlights = get_highlights(images)

    return render(request, 'gallery/home.html', {
        'images_by_month': dict(images_by_month),
        'highlights': highlights,
    })


def get_highlights(images):
    tag_counter = Counter()

    for img in images:
        tags = (img.ai_tags or "").lower().split(", ")
        tag_counter.update(tags)

    scored = []

    for img in images:
        tags = (img.ai_tags or "").lower().split(", ")
        score = sum(1 / (tag_counter[t] + 1) for t in tags)
        scored.append((score, img))

    scored.sort(reverse=True, key=lambda x: x[0])

    top_candidates = [img for score, img in scored[:10]]

    highlights = random.sample(top_candidates, min(6, len(top_candidates)))

    return highlights


def run_ai_processing(obj):
    if not obj.image:
        return

    try:
        raw_caption = generate_caption(obj.image.path)
        caption = clean_caption(raw_caption)
        
        tags = generate_tags_from_caption(caption)
        embedding = get_image_embedding(obj.image.path)

        description = f"This moment captures {caption}"

        ImageUpload.objects.filter(id=obj.id).update(
            caption=caption,
            ai_tags=", ".join(tags),
            embedding=embedding.tolist(),
            description=description
        )

    except Exception as e:
        print(f"[AI ERROR] {e}")


@login_required
def generate_image_api(request):
    query = request.GET.get("q", "")

    base_images = ImageUpload.objects.filter(
        user=request.user,
        trashed=False
    )

    related_images = get_related_images_for_generation(query, base_images)

    prompt = build_advanced_prompt(query, related_images)

    start_time = time.time()
    image_bytes = generate_image_from_prompt(prompt)
    end_time = time.time()
    generation_time = round(end_time - start_time, 2)

    file_name = f"{query.replace(' ', '_')}.png"

    generated_obj = GeneratedImage.objects.create(
        user=request.user,
        title=query,
        prompt=prompt,
        generation_time=generation_time,
        caption=f"AI generated image for '{query}'",
        tags=", ".join([img.ai_tags for img in related_images if img.ai_tags][:3])
    )

    generated_obj.image.save(file_name, ContentFile(image_bytes))
    generated_obj.save()

    return JsonResponse({
        "generated": True,
        "redirect_url": "/gallery/generated/"
    })


@login_required
def upload_image(request):
    if request.method == 'POST':
        files = request.FILES.getlist('images')
        title = request.POST.get('title', '').strip()
        tags = request.POST.get('tags', '').strip()
        description = request.POST.get('description', '').strip()
        audio_note = request.FILES.get('audio_note')

        for f in files:
            obj = ImageUpload(
                user=request.user, 
                image=f, 
                title=title, 
                tags=tags, 
                description=description
            )
            if audio_note:
                obj.audio_note = audio_note
            obj.save()
            compress_image(obj.image.path)
            Thread(target=run_ai_processing, args=(obj,)).start()
        return redirect('gallery_home')
    return render(request, 'gallery/upload.html')


@login_required
def generated_gallery(request):
    images = GeneratedImage.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'gallery/generated.html', {'images': images})

@login_required
def generated_detail(request, image_id):
    image = get_object_or_404(GeneratedImage, id=image_id, user=request.user)

    tags_list = []
    if image.tags:
        tags_list = [tag.strip() for tag in image.tags.split(",")]

    return render(request, 'gallery/generated_detail.html', {
        'image': image,
        'tags_list': tags_list
    })

@login_required
def favorites(request):
    images = ImageUpload.objects.filter(
        user=request.user, 
        favorite=True, 
        trashed=False
    ).order_by('-upload_date')
    return render(request, 'gallery/favorites.html', {'images': images})

@login_required
def archives(request):
    images = ImageUpload.objects.filter(
        user=request.user, 
        archived=True, 
        trashed=False
    ).order_by('-upload_date')
    return render(request, 'gallery/archives.html', {'images': images})

@login_required
def trash(request):
    images = ImageUpload.objects.filter(
        user=request.user, 
        trashed=True
    ).order_by('-upload_date')
    return render(request, 'gallery/trash.html', {'images': images})

@login_required
def recently_added(request):
    last_week = timezone.now() - timedelta(days=7)
    images = ImageUpload.objects.filter(
        user=request.user,
        trashed=False,
        upload_date__gte=last_week
    ).order_by('-upload_date')
    return render(request, 'gallery/recently_added.html', {'images': images})

@login_required
def albums_list(request):
    albums = Album.objects.filter(user=request.user).order_by('-created_date')
    return render(request, 'gallery/albums.html', {'albums': albums})

@login_required
def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    images = album.images.all()
    return render(request, 'gallery/album_detail.html', {'album': album, 'images': images})

@login_required
def toggle_favorite(request, image_id):
    image = get_object_or_404(ImageUpload, id=image_id, user=request.user)
    image.favorite = not image.favorite
    image.save()
    return redirect(request.META.get('HTTP_REFERER', 'gallery_home'))

@login_required
def toggle_archive(request, image_id):
    image = get_object_or_404(ImageUpload, id=image_id, user=request.user)
    image.archived = not image.archived
    image.save()
    return redirect(request.META.get('HTTP_REFERER', 'gallery_home'))

@login_required
def move_to_trash(request, image_id):
    image = get_object_or_404(ImageUpload, id=image_id, user=request.user)
    image.trashed = True
    image.save()
    return redirect(request.META.get('HTTP_REFERER', 'gallery_home'))

@login_required
def restore_from_trash(request, image_id):
    image = get_object_or_404(ImageUpload, id=image_id, user=request.user)
    image.trashed = False
    image.save()
    return redirect('trash')

@login_required
def delete_permanently(request, image_id):
    image = get_object_or_404(ImageUpload, id=image_id, user=request.user)
    image.image.delete() 
    if image.audio_note:
        image.audio_note.delete()
    image.delete()  
    return redirect('trash')


@login_required
@require_GET
def live_search_api(request):
    query = request.GET.get('q', '').strip()
    if query == '':
        return JsonResponse({'results': []})
    
    uploaded_images = ImageUpload.objects.filter(
       user=request.user,
       trashed=False
    )

    generated_images = GeneratedImage.objects.filter(
       user=request.user
    )

    ai_results = smart_search_filter(query, uploaded_images)
    generated_results = generated_images.filter(
       title__icontains=query
    )

    images = list(ai_results) + list(generated_results)
    images = images[:20]

    results = []

    for img in images:
        is_generated = hasattr(img, 'prompt')

        results.append({
           'id': img.id,
           'title': img.title,
           'image_url': img.image.url,
           'favorite': getattr(img, 'favorite', False),
           'type': 'generated' if is_generated else 'uploaded'
        })
    return JsonResponse({'results': results})


@login_required
def album_create(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.save()
            messages.success(request, 'Album created successfully.')
            return redirect('albums_list')
    else:
        form = AlbumForm()
    return render(request, 'gallery/album_create.html', {'form': form})

@login_required
def album_edit(request, album_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    if request.method == 'POST':
        form = AlbumForm(request.POST, instance=album)
        if form.is_valid():
            form.save()
            messages.success(request, 'Album updated successfully.')
            return redirect('album_detail', album_id=album.id)
    else:
        form = AlbumForm(instance=album)
    return render(request, 'gallery/album_edit.html', {'form': form, 'album': album})


@login_required
@require_POST
def update_album_images(request, album_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    try:
        data = json.loads(request.body)
        image_ids = data.get('image_ids', [])
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    for image in ImageUpload.objects.filter(id__in=image_ids, user=request.user):
        if not album.images.filter(id=image.id).exists():
           album.images.add(image)
    return JsonResponse({'success': True})


@login_required
def user_images_api(request):
    images = ImageUpload.objects.filter(user=request.user, trashed=False)
    data = {
        'images': [
            {'id': img.id, 'image_url': img.image.url, 'title': img.title or ''}
            for img in images
        ]
    }
    return JsonResponse(data)


@login_required
@require_POST
def create_album_with_images(request):
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    image_ids = request.POST.getlist('images[]')

    if not name or not image_ids:
        return JsonResponse({'success': False, 'error': 'Missing album name or image.'}, status=400)

    album = Album.objects.create(user=request.user, name=name, description=description)
    images = ImageUpload.objects.filter(id__in=image_ids, user=request.user)
    album.images.add(*images)
    return JsonResponse({'success': True, 'album_id': album.id})



@login_required
@require_POST
def remove_from_album(request, album_id, image_id):
    album = get_object_or_404(Album, id=album_id, user=request.user)
    image = get_object_or_404(ImageUpload, id=image_id, user=request.user)
    album.images.remove(image)
    return JsonResponse({'success': True})


'''profile option and settings'''

@login_required
def profile_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    favorites = ImageUpload.objects.filter(user=request.user, favorite=True)
    albums = Album.objects.filter(user=request.user)
    return render(request, 'gallery/profile.html', {
        'profile': profile,
        'favorites': favorites,
        'albums': albums,
    })


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_pic']



@login_required
def profile_edit(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        user_form = ProfileEditForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = ProfileEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    return render(request, 'gallery/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
