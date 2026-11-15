API_URL="http://127.0.0.1:1289"


function print(p) {
	console.log(p);
	document.getElementById("status-text").innerText = p;
}


function button_scan() {
	fetch(API_URL + "/scan")
		.then((response) => {
			if (!response.ok) {
				throw new Error("HTTP error: " + response.status);
			}
			return response.json();
		}).then((json) => ui_scan(json))
			.catch((err) => console.error("Fetch problem: " + err.message));
	return 0;
}

function ui_scan(json) {
	print(json["message"]);
	return 0;
}


function button_extract() {
	fetch(API_URL + "/extract_metadata")
		.then((response) => {
			if (!response.ok) {
				throw new Error("HTTP error: " + response.status);
			}
			return response.json();
		}).then((json) => ui_extract(json))
			.catch((err) => console.error("Fetch problem: " + err.message));
	return 0;
}

function ui_extract(json) {
	print(json["message"]);
	return 0;
}


function button_analyze() {
	fetch(API_URL + "/analyze")
		.then((response) => {
			if (!response.ok) {
				throw new Error("HTTP error: " + response.status);
			}
			return response.json();
		}).then((json) => ui_analyze(json))
			.catch((err) => console.error("Fetch problem: " + err.message));
	return 0;
}

function ui_analyze(json) {
	print(json["message"]);
	return 0;
}


function button_search() {
	search = document.getElementById("search-box").value;
	if (! search) {search = "all"};
	print("button_search(" + search + ")");
	fetch(API_URL + "/photos/" + search)
		.then((response) => {
			if (!response.ok) {
				throw new Error("HTTP error: " + response.status);
			}
			return response.json();
		}).then((json) => ui_search(json))
			.catch((err) => console.error("Fetch problem: " + err.message));
	return 0;
}

var sbox = document.getElementById("search-box");
sbox.addEventListener("keydown", function (e) {
    if (e.code === "Enter") {
        button_search(e);
    }
});

function ui_search(json) {
	console.log(json)
	photo_list = json["payload"];
	template = document.getElementById("pic-item").cloneNode("deep");
	div = document.getElementById("pic-container");
	div.innerHTML = "";
	photo_list.forEach(element => {
    	console.log(element);
    	new_item = template.cloneNode("deep");
		new_item.children[0].src = API_URL + "/image/" + element;
		new_item.children[0].alt = element;
		div.appendChild(new_item);
	});
	return 0;
}

function click_on_photo(element) {
	pid = element.children[0].alt;
	window.open("photo.html?pid=" + pid, "_blank").focus();
}


button_search()