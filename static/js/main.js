// BorderWatch - Main JS (simplified)
document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 4s
    document.querySelectorAll('.alert').forEach(el => {
        setTimeout(() => {
            el.style.transition = 'opacity 0.3s';
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 300);
        }, 4000);
    });

    // File input preview
    const fileInput = document.getElementById('image');
    const previewContainer = document.getElementById('image-preview-container');
    const previewImg = document.getElementById('image-preview');

    if (fileInput && previewContainer && previewImg) {
        fileInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = e => {
                    previewImg.src = e.target.result;
                    previewContainer.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                previewContainer.style.display = 'none';
            }
        });
    }

    // Clickable table rows
    document.querySelectorAll('table tbody tr').forEach(row => {
        const link = row.querySelector('a');
        if (link) {
            row.style.cursor = 'pointer';
            row.addEventListener('click', () => link.click());
        }
    });

    // Login timestamp
    const tsEl = document.getElementById('current-time');
    if (tsEl) {
        tsEl.textContent = new Date().toLocaleString();
    }
});
