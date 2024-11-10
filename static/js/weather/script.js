function toggleUnits(unit) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('unit', unit);
    
    // Show loading spinner
    document.getElementById('loading-indicator').style.display = 'block';
    
    // Set the new unit in URL and reload
    window.location.search = urlParams.toString();
}

document.addEventListener("DOMContentLoaded", function() {
    // Hide loading indicator once content is fully loaded
    document.getElementById('loading-indicator').style.display = 'none';
});

window.addEventListener("error", function() {
    alert("An error occurred while fetching data. Please try again later.");
});
