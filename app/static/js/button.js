const sizeButtons = document.querySelectorAll('.btn-group.size .btn');

sizeButtons.forEach(button => {
  button.addEventListener('click', () => {
    sizeButtons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    
    const filters = {
      size: button.textContent.trim().toLowerCase()
    };
    
    window.location.search = new URLSearchParams(filters);
    event.preventDefault();
  });
});

