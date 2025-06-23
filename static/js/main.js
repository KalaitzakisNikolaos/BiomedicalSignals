// Main JavaScript File for Biomedical Signals Project

document.addEventListener('DOMContentLoaded', function() {
    // Toggle dataset case lists
    const datasetHeaders = document.querySelectorAll('.dataset-header');
    if (datasetHeaders) {
        datasetHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const caseList = this.nextElementSibling;
                // Toggle the active class on the case list
                caseList.classList.toggle('active');
                
                // Update the arrow indicator
                const arrow = this.querySelector('.arrow');
                if (arrow) {
                    if (caseList.classList.contains('active')) {
                        arrow.textContent = '▼';
                    } else {
                        arrow.textContent = '▶';
                    }
                }
                
                // Close other open lists
                const allCaseLists = document.querySelectorAll('.case-list');
                allCaseLists.forEach(list => {
                    if (list !== caseList && list.classList.contains('active')) {
                        list.classList.remove('active');
                        const otherHeader = list.previousElementSibling;
                        const otherArrow = otherHeader.querySelector('.arrow');
                        if (otherArrow) {
                            otherArrow.textContent = '▶';
                        }
                    }
                });
            });
        });
    }
      // ComBat visualization form submission
    const combatForm = document.getElementById('combat-form');
    if (combatForm) {
        combatForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const resultsContainer = document.getElementById('combat-results');
            const spinner = document.getElementById('combat-spinner');
            const generateBtn = document.getElementById('generate-combat-btn');
            const descContainer = document.getElementById('combat-description');
            
            // Show loading state
            spinner.classList.remove('d-none');
            generateBtn.disabled = true;
            descContainer.innerHTML = '<p>Generating ComBat visualization using real data, please wait...</p>';
            
            // Make API request to generate ComBat visualization
            fetch('/api/combat_visualization', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                // Hide spinner
                spinner.classList.add('d-none');
                generateBtn.disabled = false;
                
                if (data.success) {
                    // Add timestamp to image URL to prevent caching
                    const timestamp = new Date().getTime();
                    const imageUrl = `${data.image_path}?t=${timestamp}`;
                    
                    resultsContainer.innerHTML = `
                        <h3>ComBat Harmonization Results</h3>
                        <img src="${imageUrl}" alt="ComBat Harmonization Visualization" class="img-fluid combat-img">
                    `;
                    descContainer.innerHTML = `<p>${data.description}</p>`;
                } else {
                    resultsContainer.innerHTML = `<p class="alert alert-danger">Error: ${data.error}</p>`;
                    descContainer.innerHTML = '<p>Failed to generate visualization. Please try again.</p>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                spinner.classList.add('d-none');
                generateBtn.disabled = false;
                resultsContainer.innerHTML = '<p class="alert alert-danger">An error occurred while generating the visualization.</p>';
                descContainer.innerHTML = '<p>Failed to generate visualization. Please try again.</p>';
            });
        });
    }
    
    // Initialize any charts or plots if needed
    function initializeCharts() {
        // Code for initializing any interactive charts would go here
        // This could use Chart.js or other libraries if needed
    }
    
    // Toggle between raw and harmonized data views if present
    const dataToggle = document.getElementById('data-toggle');
    if (dataToggle) {
        dataToggle.addEventListener('change', function() {
            const rawData = document.querySelectorAll('.raw-data');
            const harmonizedData = document.querySelectorAll('.harmonized-data');
            
            if (this.checked) {
                // Show harmonized data
                rawData.forEach(el => el.style.display = 'none');
                harmonizedData.forEach(el => el.style.display = 'block');
            } else {
                // Show raw data
                rawData.forEach(el => el.style.display = 'block');
                harmonizedData.forEach(el => el.style.display = 'none');
            }
        });
    }
    
    // Function to highlight the currently selected case in sidebar
    function highlightCurrentCase() {
        const currentPath = window.location.pathname;
        const caseLinks = document.querySelectorAll('.case-list a');
        
        caseLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.parentElement.classList.add('active-case');
                // Expand the parent dataset list
                const parentList = link.closest('.case-list');
                parentList.classList.add('active');
                const datasetHeader = parentList.previousElementSibling;
                const arrow = datasetHeader.querySelector('.arrow');
                if (arrow) {
                    arrow.textContent = '▼';
                }
            }
        });
    }
    
    // Call initialization functions
    initializeCharts();
    highlightCurrentCase();
});
