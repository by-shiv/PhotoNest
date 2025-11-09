let selectedImageId = null;

function showImageMenu(imageId) {
    selectedImageId = imageId;
    document.getElementById('actions-navbar').style.display = 'flex';
}

function hideImageMenu() {
    document.getElementById('actions-navbar').style.display = 'none';
    selectedImageId = null;
}

// Example: handle Delete click (make actual requests using fetch/AJAX for real app)
function deleteImage() {
    if (selectedImageId) {
        window.location.href = '/gallery/image/' + selectedImageId + '/delete/';
    }
}
function addToAlbum() {
    if (selectedImageId) {
        window.location.href = '/gallery/image/' + selectedImageId + '/add-to-album/'; // implement this view
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
document.addEventListener('click', function(e) {
    const actionsBar = document.getElementById('actions-navbar');
    if (actionsBar && !actionsBar.contains(e.target) && !e.target.classList.contains('select-btn')) {
        hideImageMenu();
    }
});
document.addEventListener('keydown', function(e) {
    if (e.key === "Escape") hideImageMenu();
});
