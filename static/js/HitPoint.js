var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);
var i=0;
const heartList=['heart0','heart1','heart2','heart3','heart4'];

function resetLife(){
    i=0;
    for(var x=0;x<5;x++){
        const bkheart =document.getElementById(heartList[x]);
        bkheart.src ='static/images/heart.png';
    }
}

socket.on('out_pipe', function () {
	console.log("out_pipe", socket.connected)
    if(i==5){
        resetLife();
    }
    heartBroken(heartList[i]);
    changeimg(heartList[i]);
});

function heartBroken(element) {
    element.src = '/static/images/broken-heart.png';
    const lightning = document.querySelectorAll('.lightning');
    var randNum = Math.floor((Math.random() * lightning.length));
    const target = lightning[randNum];
    var newone = target.cloneNode(true);
    target.parentNode.replaceChild(newone, target);
    const music = new Audio('/static/bgm/Thunder-crack.mp3');
    music.play();
}

function changeimg(item) {
    const heart = document.getElementById(item);
    heart.src = 'static/images/broken-heart.png';
    i++;
}