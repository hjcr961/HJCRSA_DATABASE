class RealTimeUpdates {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.dataLoader = new DataLoader();
        this.initialize();
    }

    initialize() {
        this.setupWebSocket();
        this.startPeriodicUpdates();
        this.setupEventListeners();
    }

    setupWebSocket() {
        this.ws = new WebSocket(
            `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/updates/`
        );

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleUpdate(data);
        };
    }

    handleUpdate(data) {
        switch (data.type) {
            case 'member_update':
                this.updateMemberData(data.content);
                break;
            case 'treasury_update':
                this.updateTreasuryData(data.content);
                break;
            case 'dependent_update':
                this.updateDependentData(data.content);
                break;
        }
    }

    startPeriodicUpdates() {
        setInterval(() => {
            this.refreshData();
        }, this.updateInterval);
    }

    setupEventListeners() {
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.refreshData();
            }
        });
    }

    async refreshData() {
        const currentPage = document.body.dataset.page;
        if (currentPage) {
            await this.dataLoader.fetchData(`/api/${currentPage}/`);
        }
    }
}

// Initialize real-time updates
const realTimeUpdates = new RealTimeUpdates();
