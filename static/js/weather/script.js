function toggleUnits(unit) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('unit', unit);
    window.location.search = urlParams.toString();
}