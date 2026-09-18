document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname.split('/').pop();
  if (path) {
    document.querySelectorAll('.nav-links a').forEach((link) => {
      const href = link.getAttribute('href');
      if (href === path || (path === '' && href === 'index.html')) {
        link.classList.add('active');
      }
    });
  }
});
