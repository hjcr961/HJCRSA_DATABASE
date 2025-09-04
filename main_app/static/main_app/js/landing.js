// Landing page search handler: redirect to members with query param and preserve UX
(function(){
  document.addEventListener('DOMContentLoaded', function(){
    const form = document.getElementById('landing-search-form');
    const input = document.getElementById('landing-search');
    const msg = document.getElementById('landing-search-msg');
    if (!form || !input) return;
    form.addEventListener('submit', function(e){
      e.preventDefault();
      const q = (input.value || '').trim();
      if (!q) {
        if (msg) { msg.textContent = 'Please enter a search query'; msg.classList.remove('hidden'); }
        return;
      }
      if (msg) { msg.textContent = ''; msg.classList.add('hidden'); }

      // Add timeout to avoid infinite spinner on intermittent network or server delays
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000); // 8s timeout

      fetch(`/api/member/search/?q=${encodeURIComponent(q)}`, { signal: controller.signal })
        .then(r => r.json().then(data => ({ ok: r.ok, data })))
        .then(({ ok, data }) => {
          clearTimeout(timeoutId);
          if (ok && data.found) {
            if (data.mode === 'card' && data.card_number) {
              window.location.href = `/members/?card=${encodeURIComponent(data.card_number)}`;
            } else if (data.mode === 'surname' && data.surname) {
              // Redirect to members list filtered by exact surname
              window.location.href = `/members/?surname=${encodeURIComponent(data.surname)}`;
            } else {
              if (msg) { msg.textContent = 'Unexpected response format'; msg.classList.remove('hidden'); }
            }
          } else {
            if (msg) { msg.textContent = data && data.error ? `Member not found: ${data.error}` : 'Member not found'; msg.classList.remove('hidden'); }
          }
        })
        .catch((err) => {
          clearTimeout(timeoutId);
          if (msg) { msg.textContent = err && err.name === 'AbortError' ? 'Search timed out. Please try again.' : 'Search failed. Please try again.'; msg.classList.remove('hidden'); }
        });
    });
  });
})();