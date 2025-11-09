from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import ImageUpload, Album
from .forms import ImageUploadForm, AlbumForm
from django.utils import timezone
from datetime import timedelta


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
