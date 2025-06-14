const mainButton = document.getElementById('mainButton');
const circleMenu = document.querySelector('.circle-menu');

mainButton.addEventListener('click', () => {
    circleMenu.classList.toggle('open');
    if (mainButton.innerHTML == "+"){
        mainButton.innerHTML = "-";
    }
    else{
        mainButton.innerHTML = "+";
    }
});
