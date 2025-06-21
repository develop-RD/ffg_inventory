/*document.addEventListener('DOMContentLoaded', function() {
function showTooltip() {
    console.log("opened");
    // Инициализация подсказок
    document.querySelectorAll('.inventory-cell').forEach(cell => {
    
        //document.getElementById('tooltipContainer').style.display = 'flex';
        const img = cell.querySelector('img');
        const tooltip = cell.querySelector('.item-tooltip');
        
        if (img && tooltip) {
            const description = img.getAttribute('data-description');
            const pros = img.getAttribute('data-pros');
            const cons = img.getAttribute('data-cons');
            const rating = img.getAttribute('data-rating');
            console.log(pros); 
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
    });
};
//});
//
*/

function showTooltip() {
    console.log("opened");
     document.getElementById('tooltipContainer').style.display = 'flex';
  // Инициализация подсказок
    document.querySelectorAll('.inventory-cell').forEach(cell =>{ 
        const img = cell.querySelector('img');
        const tooltip = cell.querySelector('.item-tooltip');
       /* Вывод информации только для определённых объектов*/ 
        // Head
        if (img && (img.getAttribute('alt') == "Голова") && tooltip){
            const pros = img.getAttribute('data-pros');
            fillPros(pros);
        }
    });
}

function closeTooltip() {
    document.getElementById('tooltipContainer').style.display = 'none';
}



function fillPros(Pros) {
    const prosList = [Pros];
    
    const prosContainer = document.querySelector('.pros ul');
    
    // Очищаем существующий список
    prosContainer.innerHTML = '';
    
    // Добавляем каждый пункт в список
    prosList.forEach(pro => {
        const li = document.createElement('li');
        li.textContent = pro;
        prosContainer.appendChild(li);
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Создаем ul элемент если его нет
    const prosDiv = document.querySelector('.pros');
    if (prosDiv && !prosDiv.querySelector('ul')) {
        const ul = document.createElement('ul');
        prosDiv.appendChild(ul);
    }
 });
