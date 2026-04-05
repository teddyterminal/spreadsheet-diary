// Collapsible nav
document.getElementById('nav-toggle').addEventListener('click', () => {
    document.getElementById('nav').classList.toggle('collapsed');
});

// Active link
document.querySelectorAll('nav a').forEach(a => {
    if (a.getAttribute('href') === window.location.pathname) {
        a.classList.add('active');
    }
});