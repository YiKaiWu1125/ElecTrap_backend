var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);
socket.on('connect', function () {
	console.log("Connected...!", socket.connected)
});

var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');
const video = document.querySelector("#videoElement");


var constraints = {
	audio: false,
	video: {
		width: 640,
		height: 480
	}
};


if (navigator.mediaDevices.getUserMedia) {
	navigator.mediaDevices.getUserMedia(constraints)
		.then(function (stream) {
			video.srcObject = stream;
			let { width, height } = stream.getTracks()[0].getSettings();
			canvas.width = width;
			canvas.height = height;
			video.hidden = true;
			video.style.display = "none";
			canvas.hidden = true;
			canvas.style.display = "none";
		})
		.catch(function (err0r) {

		});
}

const FPS = 120;
setInterval(() => {
	width = canvas.width;
	height = canvas.height;
	context.drawImage(video, 0, 0, width, height);
	var data = canvas.toDataURL('image/jpeg', 0.5);
	context.clearRect(0, 0, width, height);
	socket.emit('image', data);
}, 1000 / FPS);

socket.on('gameover', function (data) {
	$('#gameover').modal('show');
});

