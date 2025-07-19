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
            cardNumber: card.dataset.cardNumber || '',
            name: card.dataset.name || '',
            branch: card.dataset.branch || '',
            churchTitle: card.dataset.churchTitle || '',
            phone: card.dataset.phone || '',
            address: card.dataset.address || '',
            picture: card.dataset.picture || '',
            branchNumber: card.dataset.branchNumber || ''
        }));
        filteredMembers = [...allMembers];
    }

// Initialize event listeners for view buttons
function initializeEventListeners() {
    const searchInput = document.getElementById('table-search');
    const clearSearchBtn = document.getElementById('clearSearch');
    const gridViewBtn = document.getElementById('gridViewBtn');
    const listViewBtn = document.getElementById('listViewBtn');

    searchInput.addEventListener('input', debounce(handleSearch, 300));
    clearSearchBtn.addEventListener('click', clearSearch);
    document.getElementById('itemsPerPage').addEventListener('change', handleItemsPerPageChange);
    document.getElementById('branchFilterBtn').addEventListener('click', toggleDropdown);
    document.getElementById('churchTitleFilterBtn').addEventListener('click', toggleDropdown);
    document.getElementById('clearFilters').addEventListener('click', clearAllFilters);
    
    // Add view toggle button listeners
    gridViewBtn.addEventListener('click', activateGridView);
    listViewBtn.addEventListener('click', activateListView);

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
        const churchTitles = [...new Set(allMembers.map(member => member.churchTitle).filter(title => title))].sort();
        const churchTitleFilterContent = document.getElementById('churchTitleFilterContent');
        const allOption = churchTitleFilterContent.querySelector('[data-church-title=""]');
        churchTitleFilterContent.innerHTML = '';
        churchTitleFilterContent.appendChild(allOption);

        churchTitles.forEach(title => {
            if (title) {
                const option = document.createElement('div');
                option.className = 'filter-option';
                option.dataset.churchTitle = title;
                option.textContent = title;
                option.addEventListener('click', () => handleChurchTitleFilter(title));
                churchTitleFilterContent.appendChild(option);
            }
        });

        allOption.addEventListener('click', () => handleChurchTitleFilter(''));
    }

    function handleChurchTitleFilter(churchTitle) {
        currentFilters.churchTitle = churchTitle;
        document.getElementById('churchTitleFilterText').textContent = churchTitle ? `: ${churchTitle}` : ': All';
        closeAllDropdowns();
        currentPage = 1;
        applyFilters();
    }



    function populateBranchFilter() {
        const branches = [...new Set(allMembers.map(member => member.branch))].sort();
        const branchFilterContent = document.getElementById('branchFilterContent');
        const allOption = branchFilterContent.querySelector('[data-branch=""]');
        branchFilterContent.innerHTML = '';
        branchFilterContent.appendChild(allOption);

        branches.forEach(branch => {
            if (branch) {
                const option = document.createElement('div');
                option.className = 'filter-option';
                option.dataset.branch = branch;
                option.textContent = branch;
                option.addEventListener('click', () => handleBranchFilter(branch));
                branchFilterContent.appendChild(option);
            }
        });

        allOption.addEventListener('click', () => handleBranchFilter(''));
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


// Update the updateDisplay function to also update the list view
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

    // Update list view if it's active
    if (viewMode === 'list') {
        renderListView();
    }

    updateResultsInfo();
    updatePagination();

    const noResults = document.getElementById('noResults');
    const membersGrid = document.getElementById('membersGrid');
    const membersListView = document.getElementById('membersListView');

    if (filteredMembers.length === 0) {
        noResults.classList.remove('hidden');
        membersGrid.style.display = 'none';
        membersListView.classList.add('hidden');
    } else {
        noResults.classList.add('hidden');
        
        // Only show the current active view
        if (viewMode === 'grid') {
            membersGrid.style.display = '';
            membersListView.classList.add('hidden');
        } else {
            membersGrid.style.display = 'none';
            membersListView.classList.remove('hidden');
        }
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

    // View mode management
let viewMode = localStorage.getItem('memberViewMode') || 'grid';
const gridViewBtn = document.getElementById('gridViewBtn');
const listViewBtn = document.getElementById('listViewBtn');
const membersGrid = document.getElementById('membersGrid');
const membersListView = document.getElementById('membersListView');
const membersListBody = document.getElementById('membersListBody');

// Initialize view based on saved preference
function initializeViewMode() {
    if (viewMode === 'list') {
        activateListView();
    } else {
        activateGridView();
    }
}

// Switch to grid view
function activateGridView() {
    gridViewBtn.classList.remove('bg-gray-100', 'text-gray-700');
    gridViewBtn.classList.add('bg-[#1a237e]', 'text-white');
    listViewBtn.classList.remove('bg-[#1a237e]', 'text-white');
    listViewBtn.classList.add('bg-gray-100', 'text-gray-700');

    membersGrid.classList.remove('hidden');
    membersListView.classList.add('hidden');
    viewMode = 'grid';
    localStorage.setItem('memberViewMode', 'grid');
}

// Switch to list view
function activateListView() {
    listViewBtn.classList.remove('bg-gray-100', 'text-gray-700');
    listViewBtn.classList.add('bg-[#1a237e]', 'text-white');
    gridViewBtn.classList.remove('bg-[#1a237e]', 'text-white');
    gridViewBtn.classList.add('bg-gray-100', 'text-gray-700');

    membersGrid.classList.add('hidden');
    membersListView.classList.remove('hidden');
    viewMode = 'list';
    localStorage.setItem('memberViewMode', 'list');

    // Generate the list view content
    renderListView();
}

// Render the list view with the current filtered members
function renderListView() {
    const membersToShow = getVisibleMembers();
    membersListBody.innerHTML = '';

    membersToShow.forEach(member => {
        // Skip members with no card number to avoid URL errors
        if (!member.cardNumber) return;

        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50';

        // Generate edit link only if we have a valid card number
        const editLink = member.cardNumber ?
            `<a href="/member/${member.cardNumber}/edit/" class="text-yellow-600 hover:text-yellow-800">Edit</a>` :
            '';

        row.innerHTML = `
            <td class="px-4 py-3 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="h-10 w-10 flex-shrink-0">
                        <img class="h-10 w-10 rounded-full object-cover" src="${member.picture}" alt="">
                    </div>
                    <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">${member.name}</div>
                    </div>
                </div>
            </td>
            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">${member.cardNumber}</td>
            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">${member.branch}</td>
            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">${member.churchTitle || '-'}</td>
            <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">${member.dependentCount}</td>
            <td class="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                    <button onclick="showMemberDetails(this)" 
                            data-card-number="${member.cardNumber}"
                            data-name="${member.name}"
                            data-branch="${member.branch}"
                            data-church-title="${member.churchTitle || ''}"
                            data-phone="${member.phone}"
                            data-address="${member.address}"
                            data-picture="${member.picture}"
                            data-branch-number="${member.branchNumber}"
                            class="text-[#1a237e] hover:text-[#283593]">
                        View
                    </button>
                    <button onclick="showPaymentHistory('${member.cardNumber}')" class="text-green-600 hover:text-green-800">
                        Payments
                    </button>
                    <button onclick="showDependents('${member.cardNumber}', '${member.name}')" class="text-blue-600 hover:text-blue-800">
                        Dependents
                    </button>
                    ${editLink}
                </div>
            </td>
        `;

        membersListBody.appendChild(row);
    });
}

// Fix the getVisibleMembers function to use filteredMembers instead
function getVisibleMembers() {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentPageMembers = filteredMembers.slice(startIndex, endIndex);
    
    // Return the current page's members with formatted data
    return currentPageMembers.map(member => {
        return {
            cardNumber: member.cardNumber || '',
            name: member.name || '',
            branch: member.branch || '',
            churchTitle: member.churchTitle || '',
            phone: member.phone || '',
            address: member.address || '',
            picture: member.picture || '/static/default-profile.jpg',
            branchNumber: member.branchNumber || '',
            dependentCount: member.dependentCount || '0'
        };
    });
}

// Remove the reference to displayMembers which doesn't exist
// and directly call renderListView in activateListView
function activateListView() {
    listViewBtn.classList.remove('bg-gray-100', 'text-gray-700');
    listViewBtn.classList.add('bg-[#1a237e]', 'text-white');
    gridViewBtn.classList.remove('bg-[#1a237e]', 'text-white');
    gridViewBtn.classList.add('bg-gray-100', 'text-gray-700');

    membersGrid.classList.add('hidden');
    membersListView.classList.remove('hidden');
    viewMode = 'list';
    localStorage.setItem('memberViewMode', 'list');

    // Generate the list view content
    renderListView();
}

// Add event listeners for view toggle buttons
gridViewBtn.addEventListener('click', activateGridView);
listViewBtn.addEventListener('click', activateListView);

// Modify the displayMembers function to update list view when needed
const originalDisplayMembers = displayMembers;
displayMembers = function(page) {
    originalDisplayMembers(page);
    if (viewMode === 'list') {
        renderListView();
    }
};

// Initialize the view mode on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the view mode
    initializeViewMode();
});