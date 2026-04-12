function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


let selectedImageId = null;

function showImageMenu(imageId) {
    selectedImageId = imageId;
    document.getElementById('actions-navbar').style.display = 'flex';
}

function hideImageMenu() {
    document.getElementById('actions-navbar').style.display = 'none';
    selectedImageId = null;
}

// handle Delete click (make actual requests using fetch/AJAX for real app)
function deleteImage() {
    if (selectedImageId) {
        window.location.href = '/gallery/image/' + selectedImageId + '/delete/';
    }
}
function addToAlbum() {
    if (selectedImageId) {
        document.getElementById('create-album-modal').style.display = 'flex';
        document.getElementById('create-album-image-ids').value = selectedImageId;
    }
}
function archiveImage() {
    if (selectedImageId) {
        window.location.href = '/gallery/image/' + selectedImageId + '/archive/';
    }
}
function shareImage() {
    if (selectedImageId) {
        // You can show a share modal here!
        alert('Share functionality for image ' + selectedImageId);
    }
}

// Hide navbar on click outside or Escape
document.addEventListener('click', function (e) {
    const actionsBar = document.getElementById('actions-navbar');
    if (actionsBar && !actionsBar.contains(e.target) && !e.target.classList.contains('select-btn')) {
        hideImageMenu();
    }
});
document.addEventListener('keydown', function (e) {
    if (e.key === "Escape") hideImageMenu();
});



// dynamic search

const searchInput = document.getElementById('live-search-input');
const resultsDiv = document.getElementById('live-search-results');
let debounceTimer;

searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    const query = searchInput.value.trim();
    if (query.length < 2) {
        resultsDiv.innerHTML = '';  // Clear results if query too short
        resultsDiv.style.display = 'none';
        return;
    }
    debounceTimer = setTimeout(() => {
        fetch(`/gallery/api/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                showSearchResults(data.results);
            });
    }, 250); // wait 250ms after user stops typing
});

function showSearchResults(results) {
    if (results.length === 0) {
        resultsDiv.innerHTML = `
        <div class="no-results">
            <div class="no-results-icon">🔍</div>
            <div class="no-results-text">No results found</div>
            <div class="no-results-sub">Try a different search or generate one ✨</div>
        </div>
    `;
        resultsDiv.style.display = 'block';
        return;
    }

    let html = '<div class="search-dropdown">';

    results.forEach(item => {
        let url = item.type === 'generated'
            ? `/gallery/generated/${item.id}/`
            : `/gallery/image/${item.id}/`;

        html += `
        <div class="search-item" onclick="window.location.href='${url}'">
            
            <img src="${item.image_url}" class="search-thumb">
            
            <div class="search-text">
                <div class="search-title">${item.title || 'Untitled'}</div>
                <div class="search-type">${item.type === 'generated' ? 'AI Generated' : 'Your Photo'}</div>
            </div>

        </div>
    `;
    });

    html += '</div>';

    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}

// Hide results if clicked outside
document.addEventListener('click', function (event) {
    if (!resultsDiv.contains(event.target) && event.target !== searchInput) {
        resultsDiv.style.display = 'none';
    }
});




// album creation modal
let currentAlbumId = null;
let selectedImageIds = new Set();

function openAlbumModal(albumId) {
    currentAlbumId = albumId;
    selectedImageIds.clear();

    const modal = document.getElementById('album-modal');
    const imageListDiv = document.getElementById('album-image-list');

    imageListDiv.innerHTML = '<p>Loading images...</p>';
    modal.style.display = 'flex';

    fetch('/gallery/api/user_images/')  // API to list user images (create API next)
        .then(res => res.json())
        .then(data => {
            imageListDiv.innerHTML = '';
            data.images.forEach(img => {
                const div = document.createElement('div');
                div.classList.add('album-select-img');
                div.style.backgroundImage = `url(${img.image_url})`;
                div.dataset.id = img.id;
                div.onclick = () => toggleSelectImage(img.id, div);
                imageListDiv.appendChild(div);
            });
        });
}

function toggleSelectImage(id, element) {
    if (selectedImageIds.has(id)) {
        selectedImageIds.delete(id);
        element.classList.remove('selected');
    } else {
        selectedImageIds.add(id);
        element.classList.add('selected');
    }
}

function closeAlbumModal() {
    const modal = document.getElementById('album-modal');
    modal.style.display = 'none';
}

function saveAlbumImages() {
    if (!currentAlbumId) return alert('No album selected!');
    fetch(`/gallery/albums/${currentAlbumId}/update_images/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Make sure to add getCookie function or send token properly
        },
        body: JSON.stringify({ image_ids: Array.from(selectedImageIds) }),
    }).then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('Album updated!');
                closeAlbumModal();
                location.reload();
            } else {
                alert('Failed to update album.');
            }
        });
}



function addToAlbum() {
    if (selectedImageId) {
        // Open the create album modal, passing the image ID
        document.getElementById('create-album-modal').style.display = 'flex';
        document.getElementById('create-album-image-ids').value = selectedImageId;
    }
}

function closeCreateAlbumModal() {
    document.getElementById('create-album-modal').style.display = 'none';
}

// Handle form submission
document.getElementById('create-album-form').onsubmit = function (e) {
    e.preventDefault();
    const name = document.getElementById('new-album-name').value;
    const desc = document.getElementById('new-album-desc').value;
    const imgIds = document.getElementById('create-album-image-ids').value;

    fetch('/gallery/api/create_album_with_images/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCookie('csrftoken') },
        body: `name=${encodeURIComponent(name)}&description=${encodeURIComponent(desc)}&images[]=${imgIds}`
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                closeCreateAlbumModal();
                window.location.href = '/gallery/albums/';  // reload albums page
            } else {
                alert(data.error || "Could not create album.");
            }
        });
};



// unarchive 

function unarchiveImage(imageId) {
    if (!confirm('Unarchive this image?')) return;
    fetch(`/gallery/image/${imageId}/archive/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
    }).then(() => {
        alert('Image unarchived!');
        location.reload();
    });
}


// Remove from album

function removeFromAlbum(albumId, imageId, btn) {
    if (!confirm("Remove this image from album?")) return;
    fetch(`/gallery/albums/${albumId}/remove_image/${imageId}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Remove the card from DOM for instant feedback
                btn.closest('.image-card').remove();
            } else {
                alert("Failed to remove image from album!");
            }
        });
}


//dropdown

document.querySelectorAll('.dropbtn').forEach(btn => {
    btn.addEventListener('click', () => {
        const dropdown = btn.nextElementSibling;
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    });
});
window.addEventListener('click', function (event) {
    if (!event.target.matches('.dropbtn')) {
        document.querySelectorAll('.dropdown-content').forEach(dc => {
            dc.style.display = 'none';
        });
    }
});

function generateImage(query) {
    const resultsDiv = document.getElementById('live-search-results');

    resultsDiv.innerHTML = `
        <p style="padding:12px;">Generating image... ⏳</p>
    `;

    fetch(`/gallery/generate-image/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
            if (data.generated) {
                window.location.href = data.redirect_url;
            } else {
                resultsDiv.innerHTML = `<p style="padding:12px;">Generation failed ❌</p>`;
            }
        })
        .catch(() => {
            resultsDiv.innerHTML = `<p style="padding:12px;">Error generating image</p>`;
        });
}

function regenerateImage(query) {
    window.location.href = `/gallery/generate-image/?q=${encodeURIComponent(query)}`;
}

function triggerSearch() {
    const query = document.getElementById('live-search-input').value.trim();
    if (!query) return;

    fetch(`/gallery/api/search/?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => showSearchResults(data.results));
}

function generateFromInput() {
    const query = document.getElementById('live-search-input').value.trim();
    if (!query) return;

    generateImage(query);
}