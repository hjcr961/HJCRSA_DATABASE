// Main initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    initializeDropdowns();
    initializeTooltips();
    initializeDataTables();
    initializeFormValidation();
    initializeNotifications();
});

// Search functionality
function initializeSearch() {
    const searchInput = document.getElementById('table-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('tbody tr');
            
            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const display = text.includes(searchTerm) ? '' : 'none';
                row.style.display = display;
                
                // Animate rows when showing
                if (display === '') {
                    row.classList.add('animate__animated', 'animate__fadeIn');
                }
            });
        });
    }
}

// Dropdown animations
function initializeDropdowns() {
    const dropdownButtons = document.querySelectorAll('[data-collapse-toggle]');
    dropdownButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('aria-controls');
            const dropdownContent = document.getElementById(targetId);
            const arrow = this.querySelector('svg:last-child');
            
            if (dropdownContent.classList.contains('hidden')) {
                dropdownContent.classList.remove('hidden');
                dropdownContent.classList.add('animate__animated', 'animate__fadeIn');
                arrow.style.transform = 'rotate(180deg)';
            } else {
                dropdownContent.classList.add('hidden');
                arrow.style.transform = 'rotate(0deg)';
            }
        });
    });
}

// Table sorting functionality
function sortTable(column, tableId) {
    const table = document.getElementById(tableId);
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const isNumeric = column => !isNaN(column);
    let sortDirection = table.getAttribute('data-sort-direction') === 'asc' ? -1 : 1;
    
    rows.sort((a, b) => {
        const aCol = a.children[column].textContent.trim();
        const bCol = b.children[column].textContent.trim();
        
        return sortDirection * (isNumeric(aCol) ? aCol - bCol : aCol.localeCompare(bCol));
    });
    
    rows.forEach(row => table.querySelector('tbody').appendChild(row));
    table.setAttribute('data-sort-direction', sortDirection === 1 ? 'asc' : 'desc');
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(form)) {
                event.preventDefault();
                showNotification('Please fill in all required fields correctly', 'error');
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            highlightInvalidField(input);
        } else {
            removeInvalidHighlight(input);
        }
    });
    
    return isValid;
}

function highlightInvalidField(field) {
    field.classList.add('border-red-500', 'animate__animated', 'animate__shakeX');
    field.addEventListener('animationend', () => {
        field.classList.remove('animate__animated', 'animate__shakeX');
    });
}

function removeInvalidHighlight(field) {
    field.classList.remove('border-red-500');
}

// Notifications system
function initializeNotifications() {
    createNotificationContainer();
}

function createNotificationContainer() {
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed top-4 right-4 z-50 space-y-4';
        document.body.appendChild(container);
    }
}

function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500',
        warning: 'bg-yellow-500'
    };
    
    notification.className = `${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg animate__animated animate__fadeInRight`;
    notification.textContent = message;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.replace('animate__fadeInRight', 'animate__fadeOutRight');
        notification.addEventListener('animationend', () => notification.remove());
    }, 3000);
}

// Initialize tooltips
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', e => {
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute bg-gray-800 text-white px-2 py-1 rounded text-sm z-50';
            tooltip.textContent = element.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
            
            const rect = element.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
            tooltip.style.left = `${rect.left + (element.offsetWidth - tooltip.offsetWidth) / 2}px`;
        });
        
        element.addEventListener('mouseleave', () => {
            const tooltips = document.querySelectorAll('.tooltip');
            tooltips.forEach(t => t.remove());
        });
    });
}

// Initialize DataTables
function initializeDataTables() {
    const tables = document.querySelectorAll('.datatable');
    tables.forEach(table => {
        new DataTable(table, {
            pageLength: 10,
            responsive: true,
            dom: 'Bfrtip',
            buttons: ['copy', 'csv', 'excel', 'pdf', 'print']
        });
    });
}
