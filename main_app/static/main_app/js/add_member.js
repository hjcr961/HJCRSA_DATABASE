// Scoped JS for Add Member page
(function(){
  const qs = (sel, ctx=document) => ctx.querySelector(sel);
  const qsa = (sel, ctx=document) => Array.from(ctx.querySelectorAll(sel));

  document.addEventListener('DOMContentLoaded', function() {
    const form = qs('#memberForm');
    const validateBtn = qs('#validateCardBtn');
    const addDepBtn = qs('#addDependentBtn');

    if (form) form.addEventListener('submit', onSubmit);
    if (validateBtn) validateBtn.addEventListener('click', validateCardNumber);
    if (addDepBtn) addDepBtn.addEventListener('click', addDependentSection);

    // Delegate toggle for dependents
    document.addEventListener('click', function(e){
      if (e.target.closest('.toggle-dependent')) {
        toggleDependent(e.target.closest('.toggle-dependent'));
      }
    });
  });

  function showSaving(){ const el = qs('#saving-indicator'); if (el) el.classList.remove('hidden'); }
  function hideSaving(){ const el = qs('#saving-indicator'); if (el) el.classList.add('hidden'); }

  function onSubmit(e){
    e.preventDefault();
    showSaving();
    const form = e.currentTarget;
    const formData = new FormData(form);
    fetch(form.action, {
      method: 'POST',
      body: formData,
      headers: { 'X-CSRFToken': qs('[name=csrfmiddlewaretoken]').value }
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        window.location.href = '/members/';
      } else {
        hideSaving();
        if (data.errors) alert('Form validation errors: ' + JSON.stringify(data.errors));
        else if (data.error) alert('Error: ' + data.error);
        else alert('An unknown error occurred');
      }
    })
    .catch(err => { console.error('Error:', err); hideSaving(); alert('An error occurred: ' + err); });
  }

  function validateCardNumber(){
    const input = qs('#id_card_number');
    if (!input) return;
    const indicator = qs('#validating-indicator');
    indicator && indicator.classList.remove('hidden');
    fetch(`/validate-card-number-add/?card_number=${encodeURIComponent(input.value)}`)
      .then(r => r.json())
      .then(data => {
        indicator && indicator.classList.add('hidden');
        if (!data.exists) {
          alert('This card number is already in use. Please enter a different card number.');
          input.value=''; input.focus();
        } else {
          alert('Card number is valid and available!');
        }
      })
      .catch(err => { console.error('Error:', err); indicator && indicator.classList.add('hidden'); });
  }

  let dependentCount = 1;
  function addDependentSection(){
    dependentCount++;
    const container = qs('#dependents-container');
    const template = container.querySelector('.dependent-section').cloneNode(true);
    template.querySelector('h3').textContent = `Dependent #${dependentCount}`;
    qsa('input', template).forEach(i => i.value='');
    container.appendChild(template);
  }

  function toggleDependent(button){
    const fields = button.closest('.dependent-section').querySelector('.dependent-fields');
    fields.classList.toggle('hidden');
    const path = button.querySelector('path');
    if (fields.classList.contains('hidden')) path.setAttribute('d','M9 5l7 7-7 7');
    else path.setAttribute('d','M19 9l-7 7-7-7');
  }
})();