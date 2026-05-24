function print(p) {
	console.log(p)
	document.getElementById("status-text").innerText = p
}

function ui_load() {
	print("ui_load()")
	return 0
}

function ui_scan() {
	print("ui_scan()")
	return 0
}

function ui_analyze() {
	print("ui_analyze()")
	return 0
}

function ui_search() {
	print("ui_search()")
	return 0
}


var wage = document.getElementById("search-box");
wage.addEventListener("keydown", function (e) {
    if (e.code === "Enter") {
        ui_search(e);
    }
});
