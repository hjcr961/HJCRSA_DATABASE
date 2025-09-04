// Global variables for pagination and filtering
let allMembers = [];
let filteredMembers = [];
let currentPage = 1;
let itemsPerPage = 24;
let currentFilters = {
    search: '',
    branch: '',
    churchTitle: ''
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeMembers();
    initializeEventListeners();
    populateBranchFilter();
    populateChurchTitleFilter();
    updateDisplay();
});

function initializeMembers() {
    const memberCards = document.querySelectorAll('.member-card');
    allMembers = Array.from(memberCards).map(card => ({
        element: card,
        cardNumber: (card.dataset.cardNumber || '').trim(),
        name: (card.dataset.name || '').trim(),
        branch: (card.dataset.branch || '').trim(),
        churchTitle: (card.dataset.churchTitle || '').trim(),
        phone: (card.dataset.phone || '').trim(),
        address: (card.dataset.address || '').trim(),
        picture: card.dataset.picture || '',
        branchNumber: (card.dataset.branchNumber || '').trim()
    }));
    filteredMembers = [...allMembers];
}

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
    if (branchFilterBtn) branchFilterBtn.addEventListener('click', toggleDropdown);
    if (churchTitleFilterBtn) churchTitleFilterBtn.addEventListener('click', toggleDropdown);
    if (clearFiltersBtn) clearFiltersBtn.addEventListener('click', clearAllFilters);

    document.addEventListener('click', function(event) {
        if (!event.target.closest('.filter-dropdown')) {
            closeAllDropdowns();
        }
    });

    document.querySelectorAll('#churchTitleFilterContent .filter-option').forEach(option => {
        option.addEventListener('click', function() {
            handleChurchTitleFilter(this.dataset.churchTitle);
        });
    });
}

function populateChurchTitleFilter() {
    const churchTitleFilterContent = document.getElementById('churchTitleFilterContent');
    if (!churchTitleFilterContent) return;

    const churchTitles = [...new Set(allMembers.map(member => member.churchTitle).filter(title => title))]
        .map(t => t.trim())
        .filter(t => t.length)
        .sort((a,b) => a.localeCompare(b));

    const existingAll = churchTitleFilterContent.querySelector('[data-church-title=""]');
    let allOptionClone;
    if (existingAll) {
        allOptionClone = existingAll.cloneNode(true); // clone to avoid losing ref/listeners on innerHTML wipe
    } else {
        allOptionClone = document.createElement('div');
        allOptionClone.className = 'filter-option';
        allOptionClone.setAttribute('data-church-title', '');
        allOptionClone.textContent = 'All Titles';
    }

    churchTitleFilterContent.innerHTML = '';
    churchTitleFilterContent.appendChild(allOptionClone);

    churchTitles.forEach(title => {
        const option = document.createElement('div');
        option.className = 'filter-option';
        option.dataset.churchTitle = title;
        option.textContent = title;
        option.addEventListener('click', () => handleChurchTitleFilter(title));
        churchTitleFilterContent.appendChild(option);
    });

    allOptionClone.addEventListener('click', () => handleChurchTitleFilter(''));
}

function handleChurchTitleFilter(churchTitle) {
    currentFilters.churchTitle = churchTitle;
    document.getElementById('churchTitleFilterText').textContent = churchTitle ? `: ${churchTitle}` : ': All';
    closeAllDropdowns();
    currentPage = 1;
    applyFilters();
}

function populateBranchFilter() {
    const branchFilterContent = document.getElementById('branchFilterContent');
    if (!branchFilterContent) return;

    const branches = [...new Set(allMembers.map(member => member.branch))]
        .map(b => (b || '').trim())
        .filter(b => b.length)
        .sort((a,b) => a.localeCompare(b));

    const existingAll = branchFilterContent.querySelector('[data-branch=""]');
    let allOptionClone;
    if (existingAll) {
        allOptionClone = existingAll.cloneNode(true);
    } else {
        allOptionClone = document.createElement('div');
        allOptionClone.className = 'filter-option';
        allOptionClone.setAttribute('data-branch', '');
        allOptionClone.textContent = 'All Branches';
    }

    branchFilterContent.innerHTML = '';
    branchFilterContent.appendChild(allOptionClone);

    branches.forEach(branch => {
        const option = document.createElement('div');
        option.className = 'filter-option';
        option.dataset.branch = branch;
        option.textContent = branch;
        option.addEventListener('click', () => handleBranchFilter(branch));
        branchFilterContent.appendChild(option);
    });

    allOptionClone.addEventListener('click', () => handleBranchFilter(''));
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase().trim();
    currentFilters.search = searchTerm;

    const clearBtn = document.getElementById('clearSearch');
    if (searchTerm) {
        clearBtn.classList.remove('hidden');
    } else {
        clearBtn.classList.add('hidden');
    }

    currentPage = 1;
    applyFilters();
}

function clearSearch() {
    document.getElementById('table-search').value = '';
    document.getElementById('clearSearch').classList.add('hidden');
    currentFilters.search = '';
    currentPage = 1;
    applyFilters();
}

function handleItemsPerPageChange(event) {
    itemsPerPage = parseInt(event.target.value);
    currentPage = 1;
    updateDisplay();
}

function toggleDropdown(event) {
    const button = event.currentTarget;
    const dropdown = button.nextElementSibling;
    const isOpen = dropdown.classList.contains('show');

    closeAllDropdowns();

    if (!isOpen) {
        dropdown.classList.add('show');
    }
}

function closeAllDropdowns() {
    document.querySelectorAll('.filter-content').forEach(dropdown => {
        dropdown.classList.remove('show');
    });
}

function handleBranchFilter(branch) {
    currentFilters.branch = branch;
    document.getElementById('branchFilterText').textContent = branch ? `: ${branch}` : ': All';
    closeAllDropdowns();
    currentPage = 1;
    applyFilters();
}

function handleGenderFilter(gender) {
    currentFilters.gender = gender;
    document.getElementById('genderFilterText').textContent = gender ? `: ${gender}` : ': All';
    closeAllDropdowns();
    currentPage = 1;
    applyFilters();
}

function clearAllFilters() {
    currentFilters = { search: '', branch: '', churchTitle: '' };

    document.getElementById('table-search').value = '';
    document.getElementById('clearSearch').classList.add('hidden');
    document.getElementById('branchFilterText').textContent = ': All';
    document.getElementById('churchTitleFilterText').textContent = ': All';

    currentPage = 1;
    applyFilters();
}

function applyFilters() {
    filteredMembers = allMembers.filter(member => {
        if (currentFilters.search) {
            const searchMatch =
                member.cardNumber.toLowerCase().includes(currentFilters.search) ||
                member.name.toLowerCase().includes(currentFilters.search) ||
                member.branch.toLowerCase().includes(currentFilters.search);
            if (!searchMatch) return false;
        }

        if (currentFilters.branch && member.branch !== currentFilters.branch) {
            return false;
        }

        if (currentFilters.churchTitle && member.churchTitle !== currentFilters.churchTitle) {
            return false;
        }

        return true;
    });

    updateDisplay();
}

function updateDisplay() {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentPageMembers = filteredMembers.slice(startIndex, endIndex);

    allMembers.forEach(member => {
        member.element.style.display = 'none';
    });

    currentPageMembers.forEach(member => {
        member.element.style.display = '';
    });

    updateResultsInfo();
    updatePagination();

    const noResults = document.getElementById('noResults');
    const membersGrid = document.getElementById('membersGrid');

    if (filteredMembers.length === 0) {
        noResults.classList.remove('hidden');
        membersGrid.style.display = 'none';
    } else {
        noResults.classList.add('hidden');
        membersGrid.style.display = '';
    }
}

function updateResultsInfo() {
    const total = filteredMembers.length;
    const startIndex = (currentPage - 1) * itemsPerPage + 1;
    const endIndex = Math.min(currentPage * itemsPerPage, total);

    document.getElementById('showingCount').textContent = total;

    let infoText = '';
    if (total === 0) {
        infoText = 'No members found';
    } else if (total <= itemsPerPage) {
        infoText = `Showing all ${total} members`;
    } else {
        infoText = `Showing ${startIndex}-${endIndex} of ${total} members`;
    }

    document.getElementById('resultsInfo').textContent = infoText;
}

function updatePagination() {
    const totalPages = Math.ceil(filteredMembers.length / itemsPerPage);
    const container = document.getElementById('paginationContainer');

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let paginationHTML = '';

    paginationHTML += `
        <button class="pagination-btn ${currentPage === 1 ? 'disabled' : ''}"
                onclick="changePage(${currentPage - 1})"
                ${currentPage === 1 ? 'disabled' : ''}>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
        </button>
    `;

    const maxVisiblePages = 7;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    if (startPage > 1) {
        paginationHTML += `<button class="pagination-btn" onclick="changePage(1)">1</button>`;
        if (startPage > 2) {
            paginationHTML += `<span class="pagination-btn disabled">...</span>`;
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <button class="pagination-btn ${i === currentPage ? 'active' : ''}"
                    onclick="changePage(${i})">${i}</button>
        `;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += `<span class="pagination-btn disabled">...</span>`;
        }
        paginationHTML += `<button class="pagination-btn" onclick="changePage(${totalPages})">${totalPages}</button>`;
    }

    paginationHTML += `
        <button class="pagination-btn ${currentPage === totalPages ? 'disabled' : ''}"
                onclick="changePage(${currentPage + 1})"
                ${currentPage === totalPages ? 'disabled' : ''}>
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
        </button>
    `;

    container.innerHTML = paginationHTML;
}

function changePage(page) {
    const totalPages = Math.ceil(filteredMembers.length / itemsPerPage);
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        updateDisplay();

        document.getElementById('membersGrid').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showMemberDetails(button) {
    const card = button.closest('.member-card');
    const member = allMembers.find(m => m.element === card);

    if (!member) return;

    document.getElementById('modalMemberNameText').textContent = member.name;
    document.getElementById('modalBranchMemberNumber').textContent = member.branchNumber || '';
    document.getElementById('modalCardNumber').textContent = member.cardNumber;
    document.getElementById('modalName').textContent = member.name;
    document.getElementById('modalBranch').textContent = member.branch;
    document.getElementById('modalGender').textContent = member.gender;
    document.getElementById('modalPhone').textContent = member.phone;
    document.getElementById('modalAddress').textContent = member.address;
    document.getElementById('modalMemberPicture').src = member.picture || '/static/default-profile.jpg';
    document.getElementById('modalChurchTitle').textContent = member.churchTitle || '-';

    document.getElementById('memberDetailModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('memberDetailModal').classList.add('hidden');
}

function showPaymentHistory(cardNumber) {
    showLoading();
    fetch(`/api/member/${cardNumber}/payments/`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('paymentHistoryBody');
            tbody.innerHTML = '';

            if (data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                            No payment history found
                        </td>
                    </tr>
                `;
            } else {
                data.forEach(payment => {
                    tbody.innerHTML += `
                        <tr class="hover:bg-[#e8eaf6]">
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${payment.fund}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">R${payment.amount}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${payment.Fund_Date_Year}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${payment.Fund_Date_Month}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${payment.payment_date}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${payment.receipt_number}</td>
                        </tr>
                    `;
                });
            }

            document.getElementById('paymentHistoryModal').classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load payment history');
        })
        .finally(() => {
            hideLoading();
        });
}

function closePaymentModal() {
    document.getElementById('paymentHistoryModal').classList.add('hidden');
}

function showDependents(cardNumber, memberName) {
    showLoading();
    fetch(`/api/member/${cardNumber}/dependents/`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('dependentsBody');
            document.getElementById('dependentsModalTitle').textContent = `Dependents - ${memberName}`;
            tbody.innerHTML = '';

            if (data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="3" class="px-6 py-8 text-center text-gray-500">
                            No dependents found
                        </td>
                    </tr>
                `;
            } else {
                data.forEach(dependent => {
                    tbody.innerHTML += `
                        <tr class="hover:bg-[#e8eaf6]">
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${dependent.name}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${dependent.surname}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-right">
                                <button onclick="showDependentPaymentHistory(event, '${dependent.idDependents}', '${dependent.name} ${dependent.surname}')"
                                    class="inline-flex items-center px-2 py-1 text-[10px] bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors duration-200">
                                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                    Payments
                                </button>
                            </td>
                        </tr>
                    `;
                });
            }

            document.getElementById('dependentsModal').classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load dependents');
        })
        .finally(() => {
            hideLoading();
        });
}

function closeDependentsModal() {
    document.getElementById('dependentsModal').classList.add('hidden');
}

function showDependentPaymentHistory(event, dependentId, dependentName) {
    event.stopPropagation();
    showLoading();

    fetch(`/api/dependent/${dependentId}/payments/`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('dependentPaymentHistoryBody');
            document.getElementById('dependentPaymentModalTitle').textContent = `Payment History - ${dependentName}`;
            tbody.innerHTML = '';

            if (data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                            No payment history found
                        </td>
                    </tr>
                `;
            } else {
                data.forEach(payment => {
                    tbody.innerHTML += `
                        <tr class="hover:bg-[#e8eaf6]">
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${payment.fund}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">R${payment.amount}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${payment.Fund_Date_Year}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${payment.Fund_Date_Month}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${payment.payment_date}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">${payment.reciept_number}</td>
                        </tr>
                    `;
                });
            }

            document.getElementById('dependentPaymentHistoryModal').classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to load dependent payment history');
        })
        .finally(() => {
            hideLoading();
        });
}

function closeDependentPaymentModal() {
    document.getElementById('dependentPaymentHistoryModal').classList.add('hidden');
}

// Close modals when clicking outside
window.onclick = function(event) {
    const memberModal = document.getElementById('memberDetailModal');
    const paymentModal = document.getElementById('paymentHistoryModal');
    const dependentsModal = document.getElementById('dependentsModal');
    const dependentPaymentModal = document.getElementById('dependentPaymentHistoryModal');

    if (event.target === memberModal) {
        memberModal.classList.add('hidden');
    }
    if (event.target === paymentModal) {
        paymentModal.classList.add('hidden');
    }
    if (event.target === dependentsModal) {
        dependentsModal.classList.add('hidden');
    }
    if (event.target === dependentPaymentModal) {
        dependentPaymentModal.classList.add('hidden');
    }
}

// Keyboard navigation for pagination
document.addEventListener('keydown', function(event) {
    if (event.target.tagName === 'INPUT') return;

    const totalPages = Math.ceil(filteredMembers.length / itemsPerPage);

    if (event.key === 'ArrowLeft' && currentPage > 1) {
        changePage(currentPage - 1);
    } else if (event.key === 'ArrowRight' && currentPage < totalPages) {
        changePage(currentPage + 1);
    }
});