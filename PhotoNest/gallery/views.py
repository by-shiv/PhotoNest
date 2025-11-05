from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import ImageUpload
from django.utils import timezone
from .forms import ImageUploadForm


@login_required
def gallery_home(request):
    images = ImageUpload.objects.filter(user=request.user, trashed=False).order_by('-upload_date')
    images_by_month = {}
    for img in images:
        month = img.upload_date.strftime("%B %Y")
        if month not in images_by_month:
            images_by_month[month] = []
        images_by_month[month].append(img)
    highlights = images[:4]  # Daily highlights: most recent
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

