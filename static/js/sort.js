document.getElementById("sort-by").addEventListener("change", function() {
    var selectedSort = this.value;
    var currentUrl = window.location.href;
    var baseUrl = currentUrl.split('?')[0];
    var queryString = currentUrl.split('?')[1];
    var params = new URLSearchParams(queryString);
    params.set('sort', selectedSort);
    window.location.href = baseUrl + '?' + params.toString();
 });
