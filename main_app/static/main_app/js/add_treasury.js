// Scoped JS for Add Treasury page. Keep IDs/classes consistent.

(function(){
  const qs = (sel, ctx=document) => ctx.querySelector(sel);
  const qsa = (sel, ctx=document) => Array.from(ctx.querySelectorAll(sel));

  document.addEventListener('DOMContentLoaded', function() {
    // Date picker
    if (window.flatpickr) {
      flatpickr('#payment_date', { dateFormat: 'Y-m-d', defaultDate: 'today' });
    }

    const cardInput = qs('#id_idmain_member');
    const form = qs('#treasury-form');
    const addBtn = qs('#add-fund');

    if (cardInput) cardInput.addEventListener('blur', validateCardNumber);
    if (form) form.addEventListener('submit', handleFormSubmit);
    if (addBtn) addBtn.addEventListener('click', addNewFund);

    initializeRemoveButtons();
    updateSummary();

    document.addEventListener('input', function(e) {
      if (e.target.classList.contains('fund-amount')) {
        updateSummary();
      }
    });
  });

  function validateCardNumber() {
    const cardNumber = this.value.trim();
    const indicator = qs('#validating-indicator');
    if (!cardNumber) return;

    indicator && indicator.classList.remove('hidden');
    fetch(`/validate-card-number/?card_number=${encodeURIComponent(cardNumber)}`)
      .then(r => r.json())
      .then(data => {
        indicator && indicator.classList.add('hidden');
        if (!data.exists) {
          alert('Invalid card number. Please enter a valid member card number.');
          this.value = '';
          this.focus();
        }
      })
      .catch(err => {
        indicator && indicator.classList.add('hidden');
        console.error('Validation error:', err);
      });
  }

  function handleFormSubmit(e) {
    e.preventDefault();
    const savingIndicator = qs('#saving-indicator');
    savingIndicator && savingIndicator.classList.remove('hidden');

    const form = e.currentTarget;
    const formData = new FormData(form);
    const fundEntries = qsa('.fund-entry');

    // Clear existing arrays (server expects arrays)
    ['fund[]','fund_date_year[]','fund_date_month[]','amount[]','receipt_number[]'].forEach(name => formData.delete(name));

    fundEntries.forEach(entry => {
      formData.append('fund[]', qs('.fund-type', entry).value);
      const selectedYears = qsa('.fund-years option:checked', entry).map(opt => opt.value);
      formData.append('fund_date_year[]', JSON.stringify(selectedYears));
      formData.append('fund_date_month[]', qs('.fund-month', entry).value);
      formData.append('amount[]', qs('.fund-amount', entry).value);
      formData.append('receipt_number[]', qs('.fund-receipt', entry).value);
    });

    fetch(form.action, {
      method: 'POST',
      headers: { 'X-CSRFToken': qs('[name=csrfmiddlewaretoken]').value },
      body: formData
    })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        window.location.href = data.redirect_url;
      } else {
        throw new Error(data.error || 'Failed to save record');
      }
    })
    .catch(err => {
      console.error('Submission error:', err);
      alert('Error saving record: ' + err.message);
    })
    .finally(() => {
      savingIndicator && savingIndicator.classList.add('hidden');
    });
  }

  function addNewFund() {
    const container = qs('#funds-container');
    const template = container.querySelector('.fund-entry').cloneNode(true);

    qsa('input, select', template).forEach(el => {
      el.value = '';
      if (el.multiple) qsa('option', el).forEach(opt => opt.selected = false);
    });

    qs('.remove-fund', template).addEventListener('click', function() {
      if (container.children.length > 1) {
        this.closest('.fund-entry').remove();
        updateSummary();
      }
    });

    container.appendChild(template);
    updateSummary();
  }

  function initializeRemoveButtons() {
    qsa('.remove-fund').forEach(btn => {
      btn.addEventListener('click', function() {
        const container = qs('#funds-container');
        if (container.children.length > 1) {
          this.closest('.fund-entry').remove();
          updateSummary();
        }
      });
    });
  }

  function updateSummary() {
    const entries = qsa('.fund-entry');
    const total = entries.reduce((sum, entry) => sum + (parseFloat(qs('.fund-amount', entry).value) || 0), 0);
    const totalFundsEl = qs('#total-funds');
    const totalAmountEl = qs('#total-amount');
    if (totalFundsEl) totalFundsEl.textContent = entries.length;
    if (totalAmountEl) totalAmountEl.textContent = `${total.toFixed(2)}`;
  }
})();
