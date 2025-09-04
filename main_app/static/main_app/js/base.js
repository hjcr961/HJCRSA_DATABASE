// Base interactions extracted from base.html

// Enhanced Sidebar Toggle for Mobile
document.addEventListener('DOMContentLoaded', function() {
  const toggleSidebar = document.getElementById('toggleSidebar');
  const sidebar = document.querySelector('aside');
  const mainContent = document.getElementById('main-content');
  const sidebarOverlay = document.getElementById('sidebar-overlay');

  if (toggleSidebar) {
    toggleSidebar.addEventListener('click', () => {
      sidebar.classList.toggle('-translate-x-full');
      sidebarOverlay.classList.toggle('hidden');
      mainContent.classList.toggle('ml-0');
      mainContent.classList.toggle('ml-64');
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', () => {
      sidebar.classList.add('-translate-x-full');
      sidebarOverlay.classList.add('hidden');
      mainContent.classList.remove('ml-64');
      mainContent.classList.add('ml-0');
    });
  }

  function handleResize() {
    if (window.innerWidth < 1024) {
      sidebar.classList.add('-translate-x-full');
      mainContent.classList.remove('ml-64');
      mainContent.classList.add('ml-0');
      sidebarOverlay.classList.add('hidden');
    } else {
      sidebar.classList.remove('-translate-x-full');
      mainContent.classList.add('ml-64');
      mainContent.classList.remove('ml-0');
      sidebarOverlay.classList.add('hidden');
    }
  }

  window.addEventListener('resize', handleResize);
  handleResize();

  // Loading indicator helpers
  function showLoading() {
    const el = document.getElementById('loading-indicator');
    if (el) el.classList.remove('hidden');
  }
  function hideLoading() {
    const el = document.getElementById('loading-indicator');
    if (el) el.classList.add('hidden');
  }

  // Real-time clock and date
  function updateDateTime() {
    const now = new Date();
    const timeElement = document.getElementById('current-time');
    const dateElement = document.getElementById('current-date');

    if (timeElement) {
      timeElement.textContent = now.toLocaleTimeString('en-US', { hour12: true, hour: '2-digit', minute: '2-digit' });
    }
    if (dateElement) {
      dateElement.textContent = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    }
  }

  updateDateTime();
  setInterval(updateDateTime, 60000);

  // Show loading when submitting forms or clicking content links
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function() { showLoading(); });
  });

  const contentLinks = document.querySelectorAll('#content-wrapper a[href]:not([href^="#"]):not([href^="javascript:"]):not([target]):not([download])');
  contentLinks.forEach(link => {
    link.addEventListener('click', function() { showLoading(); });
  });
});
