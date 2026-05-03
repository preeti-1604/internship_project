# Enhanced Dashboard Template
# This will be integrated into dashboard.py

ENHANCED_DASHBOARD_ADDITIONS = """
<!-- Add DataTables CSS and JS -->
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
<link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css">
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/pdfmake.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/vfs_fonts.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.print.min.js"></script>

<style>
/* DataTables Custom Styling */
.dataTables_wrapper {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
}

.dataTables_filter input {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    padding: 8px 12px;
    margin-left: 8px;
}

.dataTables_length select {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    padding: 6px 10px;
    margin: 0 8px;
}

.dataTables_info {
    color: var(--muted);
    font-size: 0.85rem;
    padding-top: 12px;
}

.dataTables_paginate {
    padding-top: 12px;
}

.paginate_button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 6px !important;
    padding: 6px 12px !important;
    margin: 0 2px !important;
}

.paginate_button:hover {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: white !important;
}

.paginate_button.current {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: white !important;
}

.dt-buttons {
    margin-bottom: 12px;
}

.dt-button {
    background: var(--accent) !important;
    border: none !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    margin-right: 8px !important;
    font-size: 0.85rem !important;
    cursor: pointer !important;
}

.dt-button:hover {
    background: #2563eb !important;
}

/* Enhanced Table Styling */
#sitesTable {
    width: 100% !important;
    border-collapse: collapse;
}

#sitesTable thead th {
    background: var(--surface);
    color: var(--muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 12px 16px;
    border-bottom: 2px solid var(--border);
    cursor: pointer;
}

#sitesTable thead th:hover {
    background: var(--card);
    color: var(--text);
}

#sitesTable tbody tr {
    border-bottom: 1px solid var(--border);
    transition: background 0.15s;
}

#sitesTable tbody tr:hover {
    background: rgba(59,130,246,0.08);
}

#sitesTable tbody td {
    padding: 12px 16px;
    font-size: 0.88rem;
    color: var(--text);
}

/* Score Badges */
.score-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
}

.score-high { background: rgba(16,185,129,0.15); color: #10b981; }
.score-medium { background: rgba(245,158,11,0.15); color: #f59e0b; }
.score-low { background: rgba(239,68,68,0.15); color: #ef4444; }

/* Rank Badge */
.rank-badge-new {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 0.85rem;
}

.rank-top3 { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; }
.rank-top10 { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; }
.rank-other { background: var(--surface); color: var(--muted); }

/* Competition Indicator */
.competition-indicator {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.82rem;
}

.competition-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.comp-low { background: #10b981; }
.comp-medium { background: #f59e0b; }
.comp-high { background: #ef4444; }

/* Address Lookup */
.address-cell {
    font-size: 0.8rem;
    color: var(--muted);
    font-style: italic;
}

.address-loading {
    color: var(--accent);
}

/* Filter Panel */
.filter-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}

.filter-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
}

.filter-item label {
    display: block;
    font-size: 0.8rem;
    color: var(--muted);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.filter-item input,
.filter-item select {
    width: 100%;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    padding: 8px 12px;
    font-size: 0.9rem;
}

.filter-actions {
    display: flex;
    gap: 12px;
    margin-top: 16px;
}

.filter-btn {
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.filter-btn-primary {
    background: var(--accent);
    color: white;
}

.filter-btn-primary:hover {
    background: #2563eb;
}

.filter-btn-secondary {
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
}

.filter-btn-secondary:hover {
    background: var(--card);
}

/* Site Comparison */
.comparison-panel {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
    display: none;
}

.comparison-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
    margin-top: 16px;
}

.comparison-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
}

.comparison-card h4 {
    color: var(--accent);
    font-size: 1.1rem;
    margin-bottom: 12px;
}

.comparison-metric {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.85rem;
}

.comparison-metric:last-child {
    border-bottom: none;
}

.comparison-metric .label {
    color: var(--muted);
}

.comparison-metric .value {
    color: var(--text);
    font-weight: 600;
}
</style>

<script>
// Sites data will be injected here
const SITES_DATA = {sites_json};

// Initialize DataTable
let sitesTable;

function initializeDataTable() {
    sitesTable = $('#sitesTable').DataTable({
        data: SITES_DATA,
        columns: [
            {
                data: 'final_rank',
                title: 'Rank',
                render: function(data) {
                    let badgeClass = data <= 3 ? 'rank-top3' : data <= 10 ? 'rank-top10' : 'rank-other';
                    return `<span class="rank-badge-new ${badgeClass}">#${data}</span>`;
                }
            },
            {
                data: 'site_id',
                title: 'Site ID',
                render: function(data) {
                    return `<span class="site-id">${data}</span>`;
                }
            },
            {
                data: 'final_score',
                title: 'Final Score',
                render: function(data) {
                    let badgeClass = data >= 0.7 ? 'score-high' : data >= 0.5 ? 'score-medium' : 'score-low';
                    return `<span class="score-badge ${badgeClass}">${data.toFixed(4)}</span>`;
                }
            },
            {
                data: 'ahp_score',
                title: 'AHP Score',
                render: function(data) {
                    return data.toFixed(4);
                }
            },
            {
                data: 'predicted_demand',
                title: 'Demand',
                render: function(data) {
                    return data.toFixed(4);
                }
            },
            {
                data: 'competition_score',
                title: 'Competition',
                render: function(data, type, row) {
                    if (data === undefined) return 'N/A';
                    let dotClass = data >= 0.7 ? 'comp-low' : data >= 0.4 ? 'comp-medium' : 'comp-high';
                    let distance = row.nearest_competitor_km || 'N/A';
                    return `<div class="competition-indicator">
                        <span class="competition-dot ${dotClass}"></span>
                        ${data.toFixed(3)} (${distance} km)
                    </div>`;
                }
            },
            {
                data: 'latitude',
                title: 'Location',
                render: function(data, type, row) {
                    if (data === undefined) return 'N/A';
                    return `<div>
                        <div style="font-size:0.8rem;font-family:monospace;">${data.toFixed(4)}, ${row.longitude.toFixed(4)}</div>
                        <div class="address-cell address-loading" id="addr-${row.site_id}">Loading address...</div>
                    </div>`;
                }
            },
            {
                data: null,
                title: 'Actions',
                orderable: false,
                render: function(data, type, row) {
                    return `
                        <button onclick="viewSiteDetails('${row.site_id}')" class="action-btn" title="View Details">
                            📊
                        </button>
                        <button onclick="addToComparison('${row.site_id}')" class="action-btn" title="Compare">
                            ⚖️
                        </button>
                        <button onclick="showOnMap(${row.latitude}, ${row.longitude})" class="action-btn" title="Show on Map">
                            🗺️
                        </button>
                    `;
                }
            }
        ],
        order: [[0, 'asc']],
        pageLength: 25,
        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'csv',
                text: '📥 Export CSV',
                title: 'EV_Charging_Sites_' + new Date().toISOString().split('T')[0]
            },
            {
                extend: 'excel',
                text: '📊 Export Excel',
                title: 'EV_Charging_Sites_' + new Date().toISOString().split('T')[0]
            },
            {
                extend: 'pdf',
                text: '📄 Export PDF',
                title: 'EV Charging Sites Report',
                orientation: 'landscape'
            },
            {
                text: '🔄 Refresh Data',
                action: function() {
                    refreshAllData();
                }
            }
        ],
        drawCallback: function() {
            // Load addresses for visible rows
            loadAddressesForVisibleRows();
        }
    });
}

// Load addresses using PositionStack API
async function loadAddressesForVisibleRows() {
    const visibleRows = sitesTable.rows({page: 'current'}).data();
    
    for (let i = 0; i < visibleRows.length; i++) {
        const row = visibleRows[i];
        if (row.latitude && row.longitude) {
            loadAddress(row.site_id, row.latitude, row.longitude);
        }
    }
}

async function loadAddress(siteId, lat, lon) {
    const addressCell = document.getElementById(`addr-${siteId}`);
    if (!addressCell) return;
    
    try {
        // Use PositionStack API for reverse geocoding
        const response = await fetch(
            `http://api.positionstack.com/v1/reverse?access_key=25568ac20b49c89857f39f3505b6f7f5&query=${lat},${lon}&limit=1`
        );
        const data = await response.json();
        
        if (data.data && data.data.length > 0) {
            const location = data.data[0];
            const address = `${location.locality || ''}, ${location.region || ''}`.trim();
            addressCell.textContent = address || 'Address not found';
            addressCell.classList.remove('address-loading');
        } else {
            addressCell.textContent = 'Address not available';
            addressCell.classList.remove('address-loading');
        }
    } catch (error) {
        addressCell.textContent = 'Error loading address';
        addressCell.classList.remove('address-loading');
    }
}

// Site comparison
let comparisonSites = [];

function addToComparison(siteId) {
    const site = SITES_DATA.find(s => s.site_id === siteId);
    if (!site) return;
    
    if (comparisonSites.length >= 3) {
        alert('Maximum 3 sites can be compared at once');
        return;
    }
    
    if (comparisonSites.find(s => s.site_id === siteId)) {
        alert('Site already added to comparison');
        return;
    }
    
    comparisonSites.push(site);
    updateComparisonPanel();
}

function updateComparisonPanel() {
    const panel = document.getElementById('comparisonPanel');
    const grid = document.getElementById('comparisonGrid');
    
    if (comparisonSites.length === 0) {
        panel.style.display = 'none';
        return;
    }
    
    panel.style.display = 'block';
    grid.innerHTML = '';
    
    comparisonSites.forEach(site => {
        const card = document.createElement('div');
        card.className = 'comparison-card';
        card.innerHTML = `
            <h4>${site.site_id} <button onclick="removeFromComparison('${site.site_id}')" style="float:right;background:none;border:none;color:var(--red);cursor:pointer;">✕</button></h4>
            <div class="comparison-metric">
                <span class="label">Rank:</span>
                <span class="value">#${site.final_rank}</span>
            </div>
            <div class="comparison-metric">
                <span class="label">Final Score:</span>
                <span class="value">${site.final_score.toFixed(4)}</span>
            </div>
            <div class="comparison-metric">
                <span class="label">AHP Score:</span>
                <span class="value">${site.ahp_score.toFixed(4)}</span>
            </div>
            <div class="comparison-metric">
                <span class="label">Demand:</span>
                <span class="value">${site.predicted_demand.toFixed(4)}</span>
            </div>
            ${site.competition_score !== undefined ? `
            <div class="comparison-metric">
                <span class="label">Competition:</span>
                <span class="value">${site.competition_score.toFixed(4)}</span>
            </div>
            <div class="comparison-metric">
                <span class="label">Nearest Competitor:</span>
                <span class="value">${site.nearest_competitor_km.toFixed(2)} km</span>
            </div>
            ` : ''}
        `;
        grid.appendChild(card);
    });
}

function removeFromComparison(siteId) {
    comparisonSites = comparisonSites.filter(s => s.site_id !== siteId);
    updateComparisonPanel();
}

function clearComparison() {
    comparisonSites = [];
    updateComparisonPanel();
}

// View site details
function viewSiteDetails(siteId) {
    const site = SITES_DATA.find(s => s.site_id === siteId);
    if (!site) return;
    
    alert(`Site Details: ${siteId}\\n\\n` +
          `Rank: #${site.final_rank}\\n` +
          `Final Score: ${site.final_score.toFixed(4)}\\n` +
          `AHP Score: ${site.ahp_score.toFixed(4)}\\n` +
          `Predicted Demand: ${site.predicted_demand.toFixed(4)}\\n` +
          (site.competition_score !== undefined ? 
           `Competition Score: ${site.competition_score.toFixed(4)}\\n` +
           `Nearest Competitor: ${site.nearest_competitor_km.toFixed(2)} km\\n` +
           `Competitor: ${site.competitor_name}\\n` : '') +
          (site.latitude ? `Location: ${site.latitude.toFixed(6)}, ${site.longitude.toFixed(6)}` : '')
    );
}

// Show on map
function showOnMap(lat, lon) {
    // Switch to map tab
    showTab('map');
    // Note: You would need to add map interaction here
    alert(`Showing location: ${lat.toFixed(6)}, ${lon.toFixed(6)}\\n\\nSwitch to Map tab to view.`);
}

// Refresh data
function refreshAllData() {
    alert('Data refresh functionality would connect to backend API to fetch latest data.\\n\\nFor now, reload the page to see updated data.');
}

// Initialize on page load
$(document).ready(function() {
    initializeDataTable();
});
</script>
"""
