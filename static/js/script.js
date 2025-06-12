document.addEventListener('DOMContentLoaded', function() {
    // Обработка всплывающих подсказок
    const inventoryCells = document.querySelectorAll('.inventory-cell');
    
    inventoryCells.forEach(cell => {
        const img = cell.querySelector('img');
        const tooltip = cell.querySelector('.item-tooltip');
        
        if (img && tooltip) {
            const description = img.getAttribute('data-description');
            const pros = img.getAttribute('data-pros');
            const cons = img.getAttribute('data-cons');
            const rating = img.getAttribute('data-rating');
            
            let stars = '';
            for (let i = 0; i < 5; i++) {
                stars += i < rating ? '★' : '☆';
            }
            
            tooltip.innerHTML = `
                <p><strong>Описание:</strong> ${description}</p>
                <p><strong>Плюсы:</strong> ${pros}</p>
                <p><strong>Минусы:</strong> ${cons}</p>
                <p><strong>Рейтинг:</strong> ${stars}</p>
            `;
        }

        cell.addEventListener('mouseenter', function() {
        const controls = this.querySelector('.item-controls');
        if (controls) {
            controls.style.opacity = '1';
        }
        });
    
        cell.addEventListener('mouseleave', function() {
        const controls = this.querySelector('.item-controls');
        if (controls) {
            controls.style.opacity = '0.7';
        }
        });
    });
});
