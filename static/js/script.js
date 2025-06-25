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
    /*Создаём поля*/
    
    const prosDiv = document.querySelector('.pros');
    const consDiv = document.querySelector('.cons');
    if (prosDiv && !prosDiv.querySelector('ul')) {
        const ul = document.createElement('ul');
        prosDiv.appendChild(ul);
    }
    if (consDiv && !consDiv.querySelector('ul')) {
        const li = document.createElement('ul');
        consDiv.appendChild(li);
    }

        const img = cell.querySelector('img');
        const tooltip = cell.querySelector('.item-tooltip');
       /* Вывод информации только для определённых объектов*/ 
        // Head
        if (img && (img.getAttribute('alt') == "Голова") && tooltip){
            const description = img.getAttribute('data-description');
            const pros = img.getAttribute('data-pros');
            const cons = img.getAttribute('data-cons');
            const rating = img.getAttribute('data-rating');

            fillPros(description,pros,cons,rating);
        }
    });

}

function closeTooltip() {
    document.getElementById('tooltipContainer').style.display = 'none';
     /*Очищаем поля*/    
    
    const prosContainer = document.querySelector('.pros');
    const consContainer = document.querySelector('.cons');
    prosContainer.innerHTML = '';
    consContainer.innerHTML = '';
   
}


function fillPros(desc,Pros,cons,rating) {
    const prosList = [Pros.split('\n')];
    const consList = [cons.split('\n')];
    const prosContainer = document.querySelector('.pros');
    const consContainer = document.querySelector('.cons');
    /*Добавляем каждый пункт при выводе*/    
    for (const elem of prosList[0]){
        const li = document.createElement('li');
        li.textContent = elem;
        prosContainer.appendChild(li);
    }

    for (const elem of consList[0]){
        const li = document.createElement('li');
        li.textContent = elem;
        consContainer.appendChild(li);
    }

    
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Создаем ul элемент если его нет
    const prosDiv = document.querySelector('.pros');
    const consDiv = document.querySelector('.cons');

   
 });
