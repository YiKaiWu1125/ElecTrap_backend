
// FIXME refactor function
function changeImage(){
    element = document.getElementById('heart');
    if (element.src.match('heart')){
        element.src ="/static/images/broken-heart.png";
        const anime = document.querySelector('.lightning');
        anime.classList.add('animate__animated', 'animate__flash');
        const shake = document.querySelector('.finalshake');
        shake.classList.add('animate__animated', 'animate__shakeX')
        const music = new Audio('static/bgm/Thunder-crack.mp3');
        music.play();
    }
}

function changeImage1(){
    element = document.getElementById('heart1');
    if (element.src.match('heart')){
        element.src ="/static/images/broken-heart.png";
        const anime = document.querySelector('.crack1');
        anime.classList.add('animate__animated', 'animate__flash');
        const cam = document.querySelector('.cam');
        cam.classList.add('animate__animated', 'animate__shakeX')
        const music = new Audio('static/bgm/Thunder-crack.mp3');
        music.play();
    }
}

function changeImage2(){
    element = document.getElementById('heart2');
    if (element.src.match('heart')){
        element.src ="/static/images/broken-heart.png";
        const anime = document.querySelector('.crack2');
        anime.classList.add('animate__animated', 'animate__flash');
        const photo = document.querySelector('.photo');
        photo.classList.add('animate__animated', 'animate__shakeX')
        const music = new Audio('static/bgm/Thunder-crack.mp3');
        music.play();
    }
}

function changeImage3(){
    element = document.getElementById('heart3');
    const anime = document.querySelector('.crack3');
    if (element.src.match('heart')){
        element.src ="/static/images/broken-heart.png";
        anime.classList.add('animate__animated','animate__flash');
        const music = new Audio('static/bgm/Thunder-crack.mp3');
        music.play();
    }
}

function changeImage4(){
    element = document.getElementById('heart4');
    const anime = document.querySelector('.crack4');
    if (element.src.match('heart')){
        element.src ="/static/images/broken-heart.png";
        anime.classList.add('animate__animated', 'animate__flash');
        const music = new Audio('static/bgm/Thunder-crack.mp3');
        music.play();
    }
}
