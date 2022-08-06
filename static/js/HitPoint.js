function heartBroken(element) {
    if (!element.classList.contains('broken')) {
        element.src = '/static/images/broken-heart.png';
        const lightning = document.querySelectorAll('.lightning');
        var randNum = Math.floor((Math.random() * lightning.length));
        const target = lightning[randNum];
        var newone = target.cloneNode(true);
        target.parentNode.replaceChild(newone, target);
        const music = new Audio('/static/bgm/Thunder-crack.mp3');
        music.play();
        element.classList.add('broken');
    }
}