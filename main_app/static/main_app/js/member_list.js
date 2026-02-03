// Global variables for pagination and filtering
let allMembers = [];
let filteredMembers = [];
let currentPage = 1;
let itemsPerPage = 24;
let currentFilters = {
    search: '',
    branch: '',
    churchTitle: '',
    searchMode: 'general'  // 'general' or 'surname'
};

// Polyfill for CSS.escape in older browsers
if (typeof CSS === 'undefined' || typeof CSS.escape !== 'function') {
    window.CSS = window.CSS || {};
    CSS.escape = function(value) {
        return String(value).replace(/[^a-zA-Z0-9_\-]/g, function(ch) {
            const hex = ch.charCodeAt(0).toString(16);
            return "\\" + hex + " ";
        });
    };
}

document.addEventListener('DOMContentLoaded', function() {
    // Show loading overlay immediately
    document.getElementById('loadingOverlay').classList.remove('hidden'); 
    
    // Initial data loading and setup
    initializeMembers();
    populateBranchFilter();         // <-- NEW: Populate the branch options
    populateChurchTitleFilter();
    
    // Read and apply URL parameters
    const params = new URLSearchParams(window.location.search);
    const q = (params.get('q') || '').trim();
    const surnameParam = (params.get('surname') || '').trim();
    const cardParam = (params.get('card') || '').trim();
    
    // Handle search from URL params
    const searchInput = document.getElementById('table-search');
    if (surnameParam) {
        if (searchInput) { searchInput.value = surnameParam; }
        currentFilters.search = surnameParam.toLowerCase();
        currentFilters.searchMode = 'surname';
    } else if (q) {
        if (searchInput) { searchInput.value = q; }
        currentFilters.search = q.toLowerCase();
        currentFilters.searchMode = 'general';
    }
    
    initializeEventListeners();
    applyFilters(); // Apply initial filters based on URL params

    // If a specific card is requested, filter to it and open the modal
    if (cardParam) {
        // Since applyFilters() already ran, the member card should be visible/first
        setTimeout(() => {
            const cardEl = document.querySelector(`.member-card[data-card-number="${CSS.escape(cardParam)}"]`);
            if (cardEl) {
                const btn = cardEl.querySelector('.member-card-actions button');
                if (btn) { showMemberDetails(btn); }
            }
        }, 50);
    }

    // Hide loading overlay after content is ready
    document.getElementById('loadingOverlay').classList.add('hidden');
});

// --- CORE DATA FUNCTIONS ---

function initializeMembers() {
    // Extract data from the rendered HTML for all members
    const memberCards = document.querySelectorAll('.member-card');
    allMembers = Array.from(memberCards).map(card => ({
        element: card,
        cardNumber: (card.dataset.cardNumber || '').trim(),
        name: (card.dataset.name || '').trim(),
        surname: (card.dataset.surname || '').trim(),
        branch: (card.dataset.branch || '').trim(),
        churchTitle: (card.dataset.churchTitle || '').trim(),
        phone: (card.dataset.phone || '').trim(),
        address: (card.dataset.address || '').trim(),
        picture: card.dataset.picture || '',
        branchNumber: (card.dataset.branchNumber || '').trim()
    }));
    // Initially, all members are filtered members
    filteredMembers = [...allMembers];
}

// --- FILTER POPULATION FUNCTIONS ---

function populateBranchFilter() {
    const branchFilterContent = document.getElementById('branchFilterContent');
    if (!branchFilterContent) return;

    // Safety check: ensure allMembers is populated
    if (allMembers.length === 0) {
        console.warn('No members found when populating branch filter');
        return;
    }

    // 1. Get unique, trimmed, and sorted branch names
    const branches = [...new Set(allMembers.map(member => member.branch).filter(branch => branch))]
        .map(b => b.trim())
        .filter(b => b.length)
        .sort((a,b) => a.localeCompare(b));

    // 2. Clear existing content but preserve the 'All' option logic
    const allOption = document.createElement('div');
    allOption.className = 'filter-option';
    allOption.setAttribute('data-branch', '');
    allOption.textContent = 'All Branches';
    allOption.addEventListener('click', () => handleBranchFilter(''));

    branchFilterContent.innerHTML = '';
    branchFilterContent.appendChild(allOption);

    // 3. Create options for each unique branch and attach listener
    branches.forEach(branch => {
        const option = document.createElement('div');
        option.className = 'filter-option';
        option.dataset.branch = branch;
        option.textContent = branch;
        option.addEventListener('click', () => handleBranchFilter(branch));
        branchFilterContent.appendChild(option);
    });
}

function populateChurchTitleFilter() {
    const churchTitleFilterContent = document.getElementById('churchTitleFilterContent');
    if (!churchTitleFilterContent) return;

    // Safety check: ensure allMembers is populated
    if (allMembers.length === 0) {
        console.warn('No members found when populating church title filter');
        return;
    }

    const churchTitles = [...new Set(allMembers.map(member => member.churchTitle).filter(title => title))]
        .map(t => t.trim())
        .filter(t => t.length)
        .sort((a,b) => a.localeCompare(b));

    // Clear existing content and create the 'All Titles' option
    const allOption = document.createElement('div');
    allOption.className = 'filter-option';
    allOption.setAttribute('data-church-title', '');
    allOption.textContent = 'All Titles';
    allOption.addEventListener('click', () => handleChurchTitleFilter(''));

    churchTitleFilterContent.innerHTML = '';
    churchTitleFilterContent.appendChild(allOption);

    // Create options for each unique title and attach listener
    churchTitles.forEach(title => {
        const option = document.createElement('div');
        option.className = 'filter-option';
        option.dataset.churchTitle = title;
        option.textContent = title;
        option.addEventListener('click', () => handleChurchTitleFilter(title));
        churchTitleFilterContent.appendChild(option);
    });
}


// --- EVENT HANDLERS ---

function initializeEventListeners() {
    const searchInput = document.getElementById('table-search');
    const clearSearchBtn = document.getElementById('clearSearch');
    const itemsPerPageEl = document.getElementById('itemsPerPage');
    const branchFilterBtn = document.getElementById('branchFilterBtn');
    const churchTitleFilterBtn = document.getElementById('churchTitleFilterBtn');
    const clearFiltersBtn = document.getElementById('clearFilters');

    if (searchInput) searchInput.addEventListener('input', debounce(handleSearch, 300));
    if (clearSearchBtn) clearSearchBtn.addEventListener('click', clearSearch);
    if (itemsPerPageEl) itemsPerPageEl.addEventListener('change', handleItemsPerPageChange);
    
    // DROPDOWN TOGGLERS
    if (branchFilterBtn) branchFilterBtn.addEventListener('click', toggleDropdown);
    if (churchTitleFilterBtn) churchTitleFilterBtn.addEventListener('click', toggleDropdown);

    if (clearFiltersBtn) clearFiltersBtn.addEventListener('click', clearAllFilters);

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.filter-dropdown')) {
            closeAllDropdowns();
        }
    });
    
    // Note: The click listeners for the options themselves are now correctly attached 
    // inside the populateBranchFilter() and populateChurchTitleFilter() functions.
}


// --- FILTER LOGIC FUNCTIONS ---

function applyFilters() {
    // 1. Filter the members list based on currentFilters
    filteredMembers = allMembers.filter(member => {
        const searchText = currentFilters.search.toLowerCase();
        
        // Branch Filter
        if (currentFilters.branch && member.branch !== currentFilters.branch) {
            return false;
        }

        // Church Title Filter
        if (currentFilters.churchTitle && member.churchTitle !== currentFilters.churchTitle) {
            return false;
        }

        // Search Filter
        if (searchText) {
            if (currentFilters.searchMode === 'surname') {
                return member.surname.toLowerCase() === searchText; // Exact match for surname
            } else {
                // General search (name, surname, card number, branch number)
                return member.name.toLowerCase().includes(searchText) ||
                       member.surname.toLowerCase().includes(searchText) ||
                       member.cardNumber.toLowerCase().includes(searchText) ||
                       member.branchNumber.toLowerCase().includes(searchText);
            }
        }
        
        return true;
    });

    // 2. Reset pagination and update display
    currentPage = 1;
    updateDisplay();
}

function handleSearch(event) {
    const searchText = event.target.value.trim();
    currentFilters.search = searchText.toLowerCase();
    currentFilters.searchMode = 'general'; // Reset to general search on input
    
    // Toggle clear button visibility
    document.getElementById('clearSearch').classList.toggle('hidden', !searchText);

    applyFilters();
}

function clearSearch() {
    const searchInput = document.getElementById('table-search');
    if (searchInput) searchInput.value = '';
    currentFilters.search = '';
    currentFilters.searchMode = 'general';
    document.getElementById('clearSearch').classList.add('hidden');
    applyFilters();
}

function handleBranchFilter(branch) {
    currentFilters.branch = branch;
    document.getElementById('branchFilterText').textContent = `: ${branch || 'All'}`;
    closeAllDropdowns();
    applyFilters();
}

function handleChurchTitleFilter(title) {
    currentFilters.churchTitle = title;
    document.getElementById('churchTitleFilterText').textContent = `: ${title || 'All'}`;
    closeAllDropdowns();
    applyFilters();
}

function clearAllFilters() {
    // Clear search
    clearSearch();

    // Clear branch filter
    currentFilters.branch = '';
    document.getElementById('branchFilterText').textContent = ': All';
    
    // Clear church title filter
    currentFilters.churchTitle = '';
    document.getElementById('churchTitleFilterText').textContent = ': All';
    
    // Clear items per page
    document.getElementById('itemsPerPage').value = '24';
    itemsPerPage = 24;

    applyFilters();
}


// --- UI/DISPLAY FUNCTIONS ---

function handleItemsPerPageChange(event) {
    itemsPerPage = parseInt(event.target.value);
    currentPage = 1; // Reset to first page
    updateDisplay();
}

function updateDisplay() {
    const grid = document.getElementById('membersGrid');
    const noResults = document.getElementById('noResults');
    const showingCount = document.getElementById('showingCount');
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const membersToShow = filteredMembers.slice(startIndex, endIndex);

    // 1. Show/Hide Cards
    allMembers.forEach(member => {
        member.element.classList.add('hidden');
    });
    membersToShow.forEach(member => {
        member.element.classList.remove('hidden');
    });

    // 2. Update Counts
    showingCount.textContent = filteredMembers.length;

    // 3. No Results Message
    if (filteredMembers.length === 0) {
        grid.classList.add('hidden');
        noResults.classList.remove('hidden');
    } else {
        grid.classList.remove('hidden');
        noResults.classList.add('hidden');
    }
    
    // 4. Update Results Info
    const totalCount = allMembers.length;
    const resultsInfoText = filteredMembers.length < totalCount
        ? `Showing ${filteredMembers.length} of ${totalCount} members`
        : `Showing all ${totalCount} members`;
    document.getElementById('resultsInfo').textContent = resultsInfoText;

    // 5. Update Pagination
    renderPagination();
}

function renderPagination() {
    const container = document.getElementById('paginationContainer');
    container.innerHTML = '';

    const totalPages = Math.ceil(filteredMembers.length / itemsPerPage);
    if (totalPages <= 1) {
        container.classList.add('hidden');
        return;
    }
    container.classList.remove('hidden');

    const paginationDiv = document.createElement('div');
    paginationDiv.className = 'flex items-center justify-center space-x-2 mt-6';

    // Previous button
    const prevBtn = createPaginationButton('Previous', currentPage > 1, () => goToPage(currentPage - 1));
    paginationDiv.appendChild(prevBtn);

    // Page buttons (simplified for space)
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    if (currentPage <= 3) {
        endPage = Math.min(totalPages, 5);
    } else if (currentPage > totalPages - 2) {
        startPage = Math.max(1, totalPages - 4);
    }

    if (startPage > 1) {
        paginationDiv.appendChild(createPaginationButton('1', true, () => goToPage(1)));
        if (startPage > 2) {
            paginationDiv.appendChild(createPaginationEllipsis());
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        const isActive = i === currentPage;
        const btn = createPaginationButton(i, true, () => goToPage(i), isActive);
        paginationDiv.appendChild(btn);
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationDiv.appendChild(createPaginationEllipsis());
        }
        paginationDiv.appendChild(createPaginationButton(totalPages, true, () => goToPage(totalPages)));
    }

    // Next button
    const nextBtn = createPaginationButton('Next', currentPage < totalPages, () => goToPage(currentPage + 1));
    paginationDiv.appendChild(nextBtn);

    container.appendChild(paginationDiv);
}

function createPaginationButton(text, enabled, action, active = false) {
    const btn = document.createElement('button');
    btn.textContent = text;
    btn.className = `px-3 py-1.5 text-sm rounded-lg transition-colors ${
        active ? 'bg-[#1a237e] text-white font-semibold' : 
        enabled ? 'bg-gray-100 text-gray-700 hover:bg-gray-200' : 
        'bg-gray-50 text-gray-400 cursor-not-allowed'
    }`;
    btn.disabled = !enabled;
    if (enabled) {
        btn.addEventListener('click', action);
    }
    return btn;
}

function createPaginationEllipsis() {
    const span = document.createElement('span');
    span.textContent = '...';
    span.className = 'px-3 py-1.5 text-sm text-gray-500';
    return span;
}

function goToPage(page) {
    currentPage = page;
    updateDisplay();
    // Scroll to the top of the grid
    const grid = document.getElementById('membersGrid');
    if (grid) {
        grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// --- UTILITY/HELPER FUNCTIONS ---

function toggleDropdown(event) {
    event.stopPropagation();
    const dropdownBtn = event.currentTarget;
    const dropdown = dropdownBtn.closest('.filter-dropdown');
    const content = dropdown.querySelector('.filter-content');

    const isOpen = content.classList.contains('show');
    closeAllDropdowns(); // Close others first

    if (!isOpen) {
        content.classList.add('show');
    }
}

function closeAllDropdowns() {
    document.querySelectorAll('.filter-content').forEach(content => {
        content.classList.remove('show');
    });
}

function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}


// --- MODAL FUNCTIONS (Simplified for space, assuming APIs are correct) ---

// Placeholder for real modal functions - API calls are not shown here but assumed to work
function showMemberDetails(button) {
    const card = button.closest('.member-card');
    if (!card) return;

    // Extract all data from the card's dataset
    const data = card.dataset;

    // Assuming you have a way to fetch the full gender detail if not on the card
    // For this example, we only use what's available
    
    // Populate Modal
    document.getElementById('modalMemberNameText').textContent = `${data.name} ${data.surname}`;
    document.getElementById('modalBranchMemberNumber').textContent = `(${data.branchMemberNumber})`;
    document.getElementById('modalMemberPicture').src = data.picture || '{% static "path/to/default/image.png" %}'; // Update default path as needed
    document.getElementById('modalCardNumber').textContent = data.cardNumber;
    document.getElementById('modalName').textContent = data.name + ' ' + data.surname;
    document.getElementById('modalBranch').textContent = data.branch;
    document.getElementById('modalChurchTitle').textContent = data.churchTitle || '-';
    // document.getElementById('modalGender').textContent = '...'; // Needs backend API for full detail
    document.getElementById('modalPhone').textContent = data.phone;
    document.getElementById('modalAddress').textContent = data.address;
    
    document.getElementById('memberDetailModal').classList.remove('hidden');
    // For Tailwind/CSS use 'block' or 'flex' instead of 'hidden' removal if needed
}

function closeModal() {
    document.getElementById('memberDetailModal').classList.add('hidden');
}

function showPaymentHistory(cardNumber) {
    const tbody = document.getElementById('paymentHistoryBody');
    tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center">Loading payments...</td></tr>';
    
    document.getElementById('paymentHistoryModal').classList.remove('hidden');

    // Replace 'member_payments' with your actual Django URL name or path
    fetch(`/api/member/${cardNumber}/payments/`) 
        .then(response => response.json())
        .then(data => {
            tbody.innerHTML = ''; // Clear loading message
            if (data.payments.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center">No payments found.</td></tr>';
                return;
            }
            data.payments.forEach(payment => {
                tbody.innerHTML += `
                    <tr class="hover:bg-gray-50">
                        <td class="px-6 py-4 text-sm">${payment.fund}</td>
                        <td class="px-6 py-4 text-sm font-medium">R${payment.amount}</td>
                        <td class="px-6 py-4 text-sm">${payment.year}</td>
                        <td class="px-6 py-4 text-sm">${payment.month}</td>
                        <td class="px-6 py-4 text-sm">${payment.date}</td>
                        <td class="px-6 py-4 text-sm">
                            <span class="text-gray-600">${payment.receipt_number || 'N/A'}</span>
                        </td>
                    </tr>`;
            });
        })
        .catch(err => {
            tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-red-500">Error loading payment data.</td></tr>';
            console.error('Error loading member payments:', err);
        });
}

function closePaymentModal() {
    document.getElementById('paymentHistoryModal').classList.add('hidden');
}

function showDependents(cardNumber, memberName) {
    const tbody = document.getElementById('dependentsBody');
    tbody.innerHTML = '<tr><td colspan="3" class="px-6 py-4 text-center">Loading...</td></tr>';
    
    document.getElementById('dependentsModalTitle').textContent = `Dependents of ${memberName}`;
    document.getElementById('dependentsModal').classList.remove('hidden');

    fetch(`/api/member/${cardNumber}/dependents/`) 
        .then(response => response.json())
        .then(data => {
            tbody.innerHTML = '';
            
            if (data.dependents && data.dependents.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" class="px-6 py-4 text-center">No dependents found.</td></tr>';
                return;
            }
            
            data.dependents.forEach(dep => {
                tbody.innerHTML += `
                    <tr class="hover:bg-gray-50">
                        <td class="px-6 py-4 text-sm">${dep.name}</td>
                        <td class="px-6 py-4 text-sm">${dep.surname}</td>
                        <td class="px-6 py-4 text-right">
                            <button onclick="showDependentPayments('${dep.id}')" class="text-purple-600 hover:text-purple-900 text-xs font-medium">
                                View Payments
                            </button>
                        </td>
                    </tr>`;
            });
                })
        .catch(err => {
            tbody.innerHTML = '<tr><td colspan="3" class="px-6 py-4 text-center text-red-500">Error loading dependents.</td></tr>';
            console.error('Error loading dependents:', err);
        });
}

function closeDependentsModal() {
    document.getElementById('dependentsModal').classList.add('hidden');
}

function showDependentPayments(dependentId) {
    const tbody = document.getElementById('dependentPaymentHistoryBody');
    const modalTitle = document.getElementById('dependentPaymentModalTitle');
    
    tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center">Loading payments...</td></tr>';
    document.getElementById('dependentPaymentHistoryModal').classList.remove('hidden');

    fetch(`/api/dependent/${dependentId}/payments/`)
        .then(response => response.json())
        .then(data => {
            tbody.innerHTML = '';
            
            // Handle both array and object responses for consistency
            const payments = data.payments || data;
            
            if (payments.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center">No payments found.</td></tr>';
                return;
            }
            
            payments.forEach(payment => {
                tbody.innerHTML += `
                    <tr class="hover:bg-gray-50">
                        <td class="px-6 py-4 text-sm">${payment.fund}</td>
                        <td class="px-6 py-4 text-sm font-medium">R${payment.amount}</td>
                        <td class="px-6 py-4 text-sm">${payment.year || payment.Fund_Date_Year}</td>
                        <td class="px-6 py-4 text-sm">${payment.month || payment.Fund_Date_Month}</td>
                        <td class="px-6 py-4 text-sm">${payment.date || payment.payment_date}</td>
                        <td class="px-6 py-4 text-sm">
                            <span class="text-gray-600">${payment.receipt_number || payment.reciept_number || 'N/A'}</span>
                        </td>
                    </tr>`;
            });
        })
        .catch(err => {
            tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-red-500">Error loading payment data.</td></tr>';
            console.error('Error loading dependent payments:', err);
        });
}

function closeDependentPaymentModal() {
    document.getElementById('dependentPaymentHistoryModal').classList.add('hidden');
}
