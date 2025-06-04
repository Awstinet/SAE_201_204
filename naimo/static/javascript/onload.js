document.addEventListener("DOMContentLoaded", () => {
    window.onload = function(){
        fetch("/pageLoaded", {method: "POST"})
    };
});








