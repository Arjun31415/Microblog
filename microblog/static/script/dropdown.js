/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
// let profile_menu = document.querySelector('#myDropdown')
// console.log(profile_menu)

// profile_menu.addEventListener('mouseover', myFunction());


function myFunction() {
    document.getElementById("profile-dropdown").classList.toggle("show");
    console.log(document.getElementById("profile-dropdown"))
}

// Close the dropdown menu if the user clicks outside of it
window.onclick = function (event) {
    if (!event.target.matches('.dropbtn')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        var i;
        for (i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}