// Barcode Scanner functionality
class BarcodeScanner {
    constructor() {
        // DOM Elements
        this.startCameraBtn = document.getElementById('startCamera');
        this.stopCameraBtn = document.getElementById('stopCamera');
        this.scannerContainer = document.getElementById('scanner-container');
        this.barcodeInput = document.getElementById('barcodeInput');
        this.lookupBarcodeBtn = document.getElementById('lookupBarcode');
        this.tryAgainBtn = document.getElementById('tryAgain');
        this.scanAnotherBtn = document.getElementById('scanAnother');
        
        // States
        this.initialState = document.getElementById('initial-state');
        this.loadingState = document.getElementById('loading-state');
        this.errorState = document.getElementById('error-state');
        this.resultsState = document.getElementById('results-state');
        this.errorMessage = document.getElementById('error-message');
        
        // Result Elements
        this.memberName = document.getElementById('member-name');
        this.memberTitle = document.getElementById('member-title');
        this.memberStatus = document.getElementById('member-status');
        this.memberNumber = document.getElementById('member-number');
        this.memberBranch = document.getElementById('member-branch');
        this.memberIssueDate = document.getElementById('member-issue-date');
        this.memberExpiryDate = document.getElementById('member-expiry-date');
        this.viewDetailsLink = document.getElementById('view-details-link');
        
        // Scanner state
        this.scannerActive = false;
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        this.startCameraBtn.addEventListener('click', () => this.initScanner());
        this.stopCameraBtn.addEventListener('click', () => this.stopScanner());
        
        this.lookupBarcodeBtn.addEventListener('click', () => {
            const barcode = this.barcodeInput.value.trim();
            if (barcode) {
                this.lookupBarcode(barcode);
            } else {
                this.errorMessage.textContent = 'Please enter a barcode value.';
                this.showState(this.errorState);
            }
        });
        
        // Allow pressing Enter in the input field
        this.barcodeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const barcode = this.barcodeInput.value.trim();
                if (barcode) {
                    this.lookupBarcode(barcode);
                }
            }
        });
        
        this.tryAgainBtn.addEventListener('click', () => {
            this.showState(this.initialState);
        });
        
        this.scanAnotherBtn.addEventListener('click', () => {
            this.barcodeInput.value = '';
            this.showState(this.initialState);
        });
        
        // Clean up when leaving the page
        window.addEventListener('beforeunload', () => {
            if (this.scannerActive) {
                this.stopScanner();
            }
        });
    }
    
    // Show a specific state and hide others
    showState(state) {
        this.initialState.classList.add('hidden');
        this.loadingState.classList.add('hidden');
        this.errorState.classList.add('hidden');
        this.resultsState.classList.add('hidden');
        
        state.classList.remove('hidden');
    }
    
    // Initialize camera scanner with improved settings
    initScanner() {
        if (this.scannerActive) return;
        
        Quagga.init({
            inputStream: {
                name: "Live",
                type: "LiveStream",
                target: document.querySelector('#scanner'),
                constraints: {
                    width: 640,
                    height: 480,
                    facingMode: "environment" // Use back camera if available
                }
            },
            locator: {
                patchSize: "medium",
                halfSample: true
            },
            numOfWorkers: navigator.hardwareConcurrency || 4,
            decoder: {
                // Support multiple barcode formats
                readers: [
                    "code_128_reader",
                    "ean_reader",
                    "ean_8_reader",
                    "code_39_reader",
                    "code_39_vin_reader",
                    "codabar_reader",
                    "upc_reader",
                    "upc_e_reader",
                    "i2of5_reader"
                ]
            },
            locate: true
        }, (err) => {
            if (err) {
                console.error("Error initializing scanner:", err);
                this.errorMessage.textContent = "Could not access camera. Please check permissions and try again.";
                this.showState(this.errorState);
                return;
            }
            
            this.scannerActive = true;
            this.scannerContainer.classList.remove('hidden');
            Quagga.start();
        });
        
        // When a barcode is detected
        Quagga.onDetected((result) => {
            if (result && result.codeResult && result.codeResult.code) {
                const barcode = result.codeResult.code;
                this.barcodeInput.value = barcode;
                this.stopScanner();
                this.lookupBarcode(barcode);
            }
        });
    }
    
    // Stop the scanner
    stopScanner() {
        if (!this.scannerActive) return;
        
        Quagga.stop();
        this.scannerActive = false;
        this.scannerContainer.classList.add('hidden');
    }
    
    // Lookup a barcode
    lookupBarcode(barcode) {
        this.showState(this.loadingState);
        
        fetch(`/barcodes/lookup/?barcode=${encodeURIComponent(barcode)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    this.errorMessage.textContent = data.error;
                    this.showState(this.errorState);
                    return;
                }
                
                // Display member details
                const member = data.member;
                this.memberName.textContent = `${member.name} ${member.surname}`;
                this.memberTitle.textContent = member.title;
                this.memberNumber.textContent = member.branch_member_number;
                this.memberBranch.textContent = member.branch;
                this.memberIssueDate.textContent = member.issue_date;
                this.memberExpiryDate.textContent = member.expiry_date;
                this.viewDetailsLink.href = member.detail_url;
                
                // Set status badge
                if (member.status === 'active') {
                    this.memberStatus.className = 'px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800';
                    this.memberStatus.textContent = 'Active';
                } else {
                    this.memberStatus.className = 'px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800';
                    this.memberStatus.textContent = 'Inactive';
                }
                
                this.showState(this.resultsState);
            })
            .catch(error => {
                console.error('Error looking up barcode:', error);
                this.errorMessage.textContent = 'An error occurred while looking up the barcode.';
                this.showState(this.errorState);
            });
    }
}

// Initialize the scanner when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const scanner = new BarcodeScanner();
});