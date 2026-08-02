API_URL="http://127.0.0.1:1289"



function print(p) {
	console.log(p);
	document.getElementById("status-text").innerText = p;
}


function button_load() {
	fetch(API_URL + "/load")
		.then((response) => {
			if (!response.ok) {
				throw new Error("HTTP error: " + response.status);
			}
			return response.json();
		}).then((json) => ui_load(json))
			.catch((err) => console.error("Fetch problem: " + err.message));
	return 0;
}

function ui_load(json) {
	print(json["message"]);
	return 0;
}


function button_search() {
	search = document.getElementById("search-box").value;
	if (! search) {search = "all"};
	print("button_search(" + search + ")");
	fetch(API_URL + "/search/" + search)
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
	print(json);
	return 0;
}
