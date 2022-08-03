function playPause() {    
    var music = document.getElementById('music2');    
    var music_btn = document.getElementById('music_btn2');    
    if (music.paused){    
        music.play();    
        music_btn.src = 'static/images/music.png';    
    }    
    else{    
        music.pause();    
        music_btn.src = 'static/images/pause.png';     
    }    
}