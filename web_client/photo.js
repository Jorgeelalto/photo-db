url_params = new URLSearchParams(window.location.search);
console.log(url_params.toString());

view = document.getElementById("pic-item").children[0].alt = url_params.get("alt");

function display(json) {
	
}
