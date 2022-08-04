var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);
socket.on('connect', function () {
	console.log("Connected...!", socket.connected)
});

var form = document.getElementById('scoreSelect');

function processForm(e) {
	if (e.preventDefault) e.preventDefault();
	const formData = new FormData(form);
	socket.emit('score', Object.fromEntries(formData));
	return false;
}

if (form.attachEvent) {
	form.attachEvent("submit", processForm);
} else {
	form.addEventListener("submit", processForm);
}


function updateTable(tableID, data) {
	var table = document.getElementById(tableID);
	while (table.rows.length > 1) {
		table.deleteRow(-1);
	}
	for (let [index, user] of data.entries()) {
		const row = document.createElement('tr');
		row.innerHTML = `<td>${index + 1}</td><td>${user.user_name}</td><td>${user.game_mode}</td><td>${user.game_body}</td><td>${user.game_level}</td><td>${user.score}</td>`;
		table.appendChild(row);
	}
}

socket.on('scoreUpdate', function (data) {
	updateTable('scoreTable', data['data']);
});
