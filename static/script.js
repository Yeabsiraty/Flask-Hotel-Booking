window.addEventListener('scroll',reveal);
function reveal(){
var reveals = document.querySelectorAll('.reveal2')
for (var i=0; i<reveals.length; i++){
var windowheight = window.innerHeight;
var revealtop = reveals[i].getBoundingClientRect().left;
var revealpoint = 150;
if(revealtop<windowheight - revealpoint){
  reveals[i].classList.add('active');
}
else{
  reveals[i].classList.remove('active');
}
}
}


function bardisplay(){
  const b = document.getElementById("bar_phone")
  const a = document.getElementById("burger-bar")
  const c= document.getElementById("burger-close")
  if (b.style.display === "none"){
    b.style.display = "block";
    a.style.display = "none";
    c.style.display = "block"
  }
  else{
    c.style.display = "none"
    b.style.display = "none";
    a.style.display = "block";
  }

}


function flash_message(){
  var x = document.getElementById("message")
  x.style.display="none"
}


window.addEventListener('scroll',reveal);
function reveal(){
var reveals = document.querySelectorAll('.reveals')
for (var i=0; i<reveals.length; i++){
var windowheight = window.innerHeight;
var revealtop = reveals[i].getBoundingClientRect().top;
var revealpoint = 150;
if(revealtop<windowheight - revealpoint){
  reveals[i].classList.add('active');
}
else{
  reveals[i].classList.remove('active');
}
}
}



function toggleMode() {
    const body = document.body;

    // Toggle the dark-mode class
    if (body.classList.contains('dark-mode')) {
        body.classList.remove('dark-mode');
        localStorage.setItem('dark-mode', 'disabled');
    } else {
        body.classList.add('dark-mode');
        localStorage.setItem('dark-mode', 'enabled');
    }
}
// Apply the saved mode preference on page load
document.addEventListener('DOMContentLoaded', function() {
  if (localStorage.getItem('dark-mode') === 'enabled') {
      document.body.classList.add('dark-mode');
  }
});




let slider = document.querySelector('.slider .list');
let items = document.querySelectorAll('.slider .list .item');
let next = document.getElementById('next');
let prev = document.getElementById('prev');
let dots = document.querySelectorAll('.slider .dots li');

let lengthItems = items.length - 1;
let active = 0;
next.onclick = function(){
    active = active + 1 <= lengthItems ? active + 1 : 0;
    reloadSlider();
}
prev.onclick = function(){
    active = active - 1 >= 0 ? active - 1 : lengthItems;
    reloadSlider();
}
let refreshInterval = setInterval(()=> {next.click()}, 2000);
function reloadSlider(){
    slider.style.left = -items[active].offsetLeft + 'px';
    // 
    let last_active_dot = document.querySelector('.slider .dots li.active');
    last_active_dot.classList.remove('active');
    dots[active].classList.add('active');

    clearInterval(refreshInterval);
    refreshInterval = setInterval(()=> {next.click()}, 2000);

    
}

dots.forEach((li, key) => {
    li.addEventListener('click', ()=>{
         active = key;
         reloadSlider();
    })
})
window.onresize = function(event) {
    reloadSlider();
};



const openModalButtons = document.querySelectorAll('[data-modal-target]')
const closeModalButtons = document.querySelectorAll('[data-close-button]')
const overlay = document.getElementById('overlay')

openModalButtons.forEach(button => {
  button.addEventListener('click', () => {
    const modal = document.querySelector(button.dataset.modalTarget)
    openModal(modal)
  })
})

overlay.addEventListener('click', () => {
  const modals = document.querySelectorAll('.modal.active')
  modals.forEach(modal => {
    closeModal(modal)
  })
})

closeModalButtons.forEach(button => {
  button.addEventListener('click', () => {
    const modal = button.closest('.modal')
    closeModal(modal)
  })
})

function openModal(modal) {
  if (modal == null) return
  modal.classList.add('active')
  overlay.classList.add('active')
}

function closeModal(modal) {
  if (modal == null) return
  modal.classList.remove('active')
  overlay.classList.remove('active')
}




let nextBtn = document.querySelector("#nexts");
let prevBtn = document.querySelector("#prevs");
let slides = document.querySelectorAll(".slide");
let changeSlide = 0;
// console.log(changeSlide);
nextBtn.addEventListener("click", function() {
  
    slides.forEach(function (slide, index) {
    if (slide.classList.contains("show") === true) {
      changeSlide = index + 1;
      slide.classList.remove("show");
    }
    
  });
//   console.log(changeSlide);
  if (changeSlide < slides.length) {
    slides[changeSlide].classList.add("show");
    }
  else {
      changeSlide = 0;
      slides[changeSlide].classList.add("show");
    }
});
// console.log(changeSlide);
prevBtn.addEventListener('click', function () {
   
    slides.forEach(function (slide, index) {
        if (slide.classList.contains("show") === true) {
            changeSlide = index - 1;
            slide.classList.remove("show");
        }
       
        
    });
    // console.log(changeSlide);

    if (changeSlide < slides.length && changeSlide > -1) {
        slides[changeSlide].classList.add("show");
    }
    else {
        // console.log(slides.length);
        
        changeSlide = slides.length - 1;
        slides[changeSlide].classList.add("show");
    }
});

