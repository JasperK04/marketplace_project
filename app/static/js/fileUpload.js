var getFileName = function(event) {
    var output = document.getElementById('image-upload');
    output.innerHTML = event.target.files[0].name;
}