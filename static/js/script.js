
// script.js - Basic dropdown toggle for user profile

document.addEventListener('DOMContentLoaded', function () {
    const dropdownBtn = document.getElementById('profileDropdownBtn');
    const dropdownContent = document.getElementById('profileDropdownContent');

    if (dropdownBtn && dropdownContent) {
        dropdownBtn.addEventListener('click', function () {
            dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
        });

        window.addEventListener('click', function (event) {
            if (!dropdownBtn.contains(event.target)) {
                dropdownContent.style.display = 'none';
            }
        });
    }
});
