document.addEventListener("DOMContentLoaded", function() {
    var paginationLinks = document.querySelectorAll('.pagination a');

    // Itera sobre os links e adiciona um ouvinte de evento ao clique
    paginationLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            // Remove a classe 'active' de todos os links
            paginationLinks.forEach(function(link) {
                link.classList.remove('active');
            });

            // Adiciona a classe 'active' apenas ao link clicado
            this.classList.add('active');
        });
    });
});