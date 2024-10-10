
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


function flash_message(){
    var x = document.getElementById("message")
    x.style.display="none"
  }



function toggleDelete() {
    const editSquare = document.querySelector('.edit_square');
    const deleteSquare = document.querySelector('.delete_square');
    const x = document.querySelector('.add_square')
    
    if (deleteSquare.style.display === 'block') {
        deleteSquare.style.display = 'none';
        const x = document.querySelector('.add_square')
    } else {
        editSquare.style.display = 'none'; 
        deleteSquare.style.display = 'block';
        x.style.display = 'none';
    }
}

function toggleadd() {
    const editSquare = document.querySelector('.edit_square');
    const deleteSquare = document.querySelector('.delete_square');
    const x = document.querySelector('.add_square')
    
    if (x.style.display === 'block') {
        x.style.display = 'none';
    } else {
        x.style.display = 'block';
        editSquare.style.display = 'none'; 
        deleteSquare.style.display = 'none';
    }
}