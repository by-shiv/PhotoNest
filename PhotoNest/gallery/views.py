from django.shortcuts import render, redirect, get_object_or_404
from .models import ImageUpload, Album
from .forms import ImageUploadForm, AlbumForm
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json


@login_required
def gallery_home(request):
    images = ImageUpload.objects.filter(
        user=request.user, 
        trashed=False, 
        archived=False
    ).order_by('-upload_date')
    
    images_by_month = {}
    for img in images:
        month = img.upload_date.strftime("%B %Y")
        if month not in images_by_month:
            images_by_month[month] = []
        images_by_month[month].append(img)
    
    highlights = images[:4]
    return render(request, 'gallery/home.html', {
        'images_by_month': images_by_month,
        'highlights': highlights,
    })


@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('gallery_home')
    else:
        form = ImageUploadForm()
    return render(request, 'gallery/upload.html', {'form': form})


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
    image.image.delete()  # Delete file from storage
    if image.audio_note:
        image.audio_note.delete()
    image.delete()  # Delete from database
    return redirect('trash')


@login_required
@require_GET
def live_search_api(request):
    query = request.GET.get('q', '').strip()
    if query == '':
        return JsonResponse({'results': []})
    
    images = ImageUpload.objects.filter(
        user=request.user,
        trashed=False
    ).filter(
        Q(title__icontains=query) | Q(tags__icontains=query) | Q(description__icontains=query)
    ).order_by('-upload_date')[:20]

    results = []
    for img in images:
        results.append({
            'id': img.id,
            'title': img.title,
            'image_url': img.image.url,
            'favorite': img.favorite,
            'uploaded_on': img.upload_date.strftime('%Y-%m-%d'),
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
@csrf_exempt 
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
