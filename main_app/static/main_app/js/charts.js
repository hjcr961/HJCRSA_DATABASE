class DashboardCharts {
    constructor() {
        this.colors = {
            primary: '#3B82F6',
            secondary: '#10B981',
            accent: '#8B5CF6',
            background: '#F3F4F6'
        };
        this.initializeCharts();
    }

    initializeCharts() {
        this.createMembershipTrends();
        this.createTreasuryAnalytics();
        this.createGenderDistribution();
    }

    createMembershipTrends() {
        const ctx = document.getElementById('membershipTrends');
        if (ctx) {
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: this.getLastSixMonths(),
                    datasets: [{
                        label: 'New Members',
                        data: [30, 45, 60, 75, 85, 100],
                        borderColor: this.colors.primary,
                        tension: 0.4
                    }]
                },
                options: this.getChartOptions('Membership Growth Trends')
            });
        }
    }

    createTreasuryAnalytics() {
        const ctx = document.getElementById('treasuryAnalytics');
        if (ctx) {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Revenue',
                        data: [12000, 19000, 15000, 25000, 22000, 30000],
                        backgroundColor: this.colors.secondary
                    }]
                },
                options: this.getChartOptions('Treasury Analytics')
            });
        }
    }

    createGenderDistribution() {
        console.log('Starting gender distribution chart creation');
        const ctx = document.getElementById('genderDistribution');
        if (ctx) {
            console.log('Canvas element found');
            fetch('/api/gender-distribution/')
                .then(response => {
                    console.log('API Response:', response);
                    return response.json();
                })
                .then(data => {
                    console.log('Data received:', data);
                    new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: data.labels,
                            datasets: [{
                                data: data.counts,
                                backgroundColor: [
                                    '#10b981',  // Emerald green
                                    '#6366f1',  // Indigo
                                ],
                                borderWidth: 0
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: 'bottom'
                                },
                                title: {
                                    display: true,
                                    text: 'Member Gender Distribution'
                                },
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                            const value = context.parsed;
                                            const percentage = ((value / total) * 100).toFixed(1);
                                            return `${context.label}: ${value} (${percentage}%)`;
                                        }
                                    }
                                }
                            }
                        }
                    });
                    console.log('Chart created');
                })
                .catch(error => console.error('Error:', error));
        } else {
            console.log('Canvas element not found');
        }
    }

    getLastSixMonths() {
        const months = [];
        const date = new Date();
        for (let i = 5; i >= 0; i--) {
            const month = new Date(date.getFullYear(), date.getMonth() - i, 1);
            months.push(month.toLocaleString('default', { month: 'short' }));
        }
        return months;
    }

    getChartOptions(title) {
        return {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: title
                }
            }
        };
    }
}

// Initialize dashboard charts
document.addEventListener('DOMContentLoaded', () => {
    new DashboardCharts();
});
