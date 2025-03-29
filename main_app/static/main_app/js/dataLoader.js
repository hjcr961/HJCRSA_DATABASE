// Data Loading Management
class DataLoader {
    constructor() {
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.tableSkeleton = document.getElementById('table-skeleton');
    }

    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
    }

    async fetchData(url) {
        this.showLoading();
        try {
            const response = await fetch(url);
            const data = await response.json();
            return data;
        } finally {
            this.hideLoading();
        }
    }

    showTableSkeleton() {
        const tableContent = document.querySelector('.table-content');
        if (tableContent) {
            tableContent.classList.add('hidden');
            this.tableSkeleton.classList.remove('hidden');
        }
    }

    hideTableSkeleton() {
        const tableContent = document.querySelector('.table-content');
        if (tableContent) {
            this.tableSkeleton.classList.add('hidden');
            tableContent.classList.remove('hidden');
        }
    }
}

// Initialize the loader
const dataLoader = new DataLoader();
