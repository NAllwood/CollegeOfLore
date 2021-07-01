var slideIndex = 0;
var slides = document.getElementsByClassName("slides");

initSlides();

function initSlides(n) {
    for (let i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slides[slideIndex].style.display = "flex";
}

// Next/previous controls
function plusSlides(n) {
    slides[slideIndex].style.display = "none";
    slideIndex = mod((slideIndex + n), slides.length);
    slides[slideIndex].style.display = "flex";
}

function enlargeImage(image) {
    image.classList.add("fullscreen");
    image.onclick = function() {reduceImage(image); };
}

function reduceImage(image) {
    image.classList.remove("fullscreen");
    image.onclick = function () { enlargeImage(image); };
}

function mod(n, m) {
    return ((n % m) + m) % m;
}