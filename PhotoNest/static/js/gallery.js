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
function moveToTrash() {
    if (selectedImageId) {
        window.location.href = '/gallery/image/' + selectedImageId + '/trash/';
    }
}

function openUploadModal() {
    const modal = document.getElementById('upload-modal');
    if (modal) modal.style.display = 'flex';
}

function closeUploadModal() {
    const modal = document.getElementById('upload-modal');
    if (modal) modal.style.display = 'none';
}

function restoreImage(imageId) {
    if (!confirm("Restore this image?")) return;

    fetch(`/gallery/image/${imageId}/restore/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    }).then(() => {
        location.reload();
    });
}

function deleteImagePermanently(imageId) {
    if (!confirm("Delete permanently? This cannot be undone.")) return;

    fetch(`/gallery/image/${imageId}/delete/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    }).then(() => {
        location.reload();
    });
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

if (searchInput && resultsDiv) {

    let debounceTimer;

    searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        const query = searchInput.value.trim();

        if (query.length < 2) {
            resultsDiv.innerHTML = '';
            resultsDiv.style.display = 'none';
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/gallery/api/search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    showSearchResults(data.results);
                });
        }, 250);
    });

}

document.addEventListener("DOMContentLoaded", () => {

    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('id_images');

    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');

        fileInput.files = e.dataTransfer.files;
        dropZone.querySelector('span').textContent =
            `${fileInput.files.length} file(s) selected`;
    });

    fileInput.addEventListener('change', () => {
        dropZone.querySelector('span').textContent =
            `${fileInput.files.length} file(s) selected`;
    });

});

document.addEventListener("DOMContentLoaded", () => {

    const uploadForm = document.getElementById('upload-form');

    if (!uploadForm) return;

    uploadForm.addEventListener('submit', function (e) {
        e.preventDefault();  // 🔥 stop normal submit

        const formData = new FormData(uploadForm);

        fetch('/gallery/upload/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(res => {
            if (res.redirected) {
                // reload page to show new images
                window.location.href = res.url;
            } else {
                location.reload();
            }
        })
        .catch(() => {
            alert("Upload failed");
        });
    });

});

function showSearchResults(results) {
    if (!searchInput || !resultsDiv) return;
    if (searchInput.value.trim() === "") {
        resultsDiv.innerHTML = "";
        resultsDiv.style.display = "none";
        return;
    }

    // 🔥 No results case
    if (results.length === 0) {
        resultsDiv.innerHTML = `
            <div class="no-results">
                <strong>🔍 No results found</strong>
                <span>Try a different search or generate one ✨</span>
            </div>
        `;
        resultsDiv.style.display = 'block';
        return;
    }

    // 🔥 Results exist
    let html = '';

    results.forEach(item => {
        let url = item.type === 'generated'
            ? `/gallery/generated/${item.id}/`
            : `/gallery/image/${item.id}/`;

        html += `
            <div class="live-search-item" onclick="window.location.href='${url}'">
                
                <img src="${item.image_url}" alt="img">
                
                <div class="search-text">
                    <div class="search-title">${item.title || 'Untitled'}</div>
                    <div class="search-type">
                        ${item.type === 'generated' ? 'AI Generated' : 'Your Photo'}
                    </div>
                </div>

            </div>
        `;
    });

    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}


// 🔥 Hide results if clicked outside
document.addEventListener('click', function (event) {
    if (resultsDiv && searchInput &&
        !resultsDiv.contains(event.target) &&
        !searchInput.contains(event.target)) {
        resultsDiv.innerHTML = "";
        resultsDiv.style.display = 'none';
    }
});



const settingsBtn = document.querySelector('.settings-btn');
const profileBtn = document.querySelector('.profile-btn');

const settingsMenu = document.querySelector('.settings-dropdown .dropdown-content');
const profileMenu = document.querySelector('.profile-dropdown .dropdown-content');

if (settingsBtn && profileBtn && settingsMenu && profileMenu) {

    settingsBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        profileMenu.classList.remove('show');
        settingsMenu.classList.toggle('show');
    });

    profileBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        settingsMenu.classList.remove('show');
        profileMenu.classList.toggle('show');
    });

    document.addEventListener('click', function () {
        settingsMenu.classList.remove('show');
        profileMenu.classList.remove('show');
    });
}


document.addEventListener("DOMContentLoaded", () => {

    const sidebar = document.querySelector(".detail-sidebar");
    const editBtn = document.querySelector(".edit-toggle");
    const cancelBtn = document.querySelector(".cancel-btn");
    const saveBtn = document.querySelector(".save-btn");

    if (editBtn) {
        editBtn.addEventListener("click", () => {
            sidebar.classList.add("editing");
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener("click", () => {
            sidebar.classList.remove("editing");
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener("click", () => {

            const url = sidebar.dataset.url;

            const title = document.querySelector(".edit-title").value;
            const description = document.querySelector(".edit-description").value;
            const tags = document.querySelector(".edit-tags").value;

            fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    title: title,
                    description: description,
                    tags: tags
                })
            })
                .then(res => res.json())
                .then(data => {

                    if (data.success) {

                        document.querySelector(".editable-field h1").innerText = title;

                        const descView = document.querySelector(".detail-block .view-mode");
                        descView.innerText = description || "No description added";

                        const tagContainer = document.querySelector(".user-tags");
                        tagContainer.innerHTML = "";

                        if (tags.trim() === "") {
                            tagContainer.innerHTML = "<span class='tag'>No tags</span>";
                        } else {
                            tags.split(",").forEach(tag => {
                                const span = document.createElement("span");
                                span.className = "tag";
                                span.innerText = tag.trim();
                                tagContainer.appendChild(span);
                            });
                        }

                        sidebar.classList.remove("editing");
                    }

                });
        });
    }

});

/* CSRF */
function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken"))
        ?.split("=")[1];
}


// album creation modal
let currentAlbumId = null;
let selectedImageIds = new Set();

function openAlbumModal(albumId) {
    currentAlbumId = albumId;
    selectedImageIds.clear();

    const modal = document.getElementById('album-modal');
    const imageListDiv = document.getElementById('album-image-list');
    if (!modal || !imageListDiv) return;
    console.log("GRID:", imageListDiv);

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

function openCreateAlbumModal() {
    document.getElementById('create-album-modal').style.display = 'flex';
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

function closeCreateAlbumModal() {
    document.getElementById('create-album-modal').style.display = 'none';
}

// Handle form submission
const createAlbumForm = document.getElementById('create-album-form');

if (createAlbumForm) {
    createAlbumForm.onsubmit = function (e) {
        e.preventDefault();

        const name = document.getElementById('new-album-name').value;
        const desc = document.getElementById('new-album-desc').value;
        const imgIds = document.getElementById('create-album-image-ids').value;

        fetch('/gallery/api/create_album_with_images/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: `name=${encodeURIComponent(name)}&description=${encodeURIComponent(desc)}&images[]=${imgIds}`
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    closeCreateAlbumModal();
                    window.location.href = '/gallery/albums/';
                } else {
                    alert(data.error || "Could not create album.");
                }
            });
    };
}


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

document.querySelector('input[type="file"]').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        document.getElementById('profile-preview').src = URL.createObjectURL(file);
    }
});