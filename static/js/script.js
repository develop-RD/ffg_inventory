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
        cell.addEventListener('click',function(event){
            // event.currentTarget - это элемент, на который кликнули
            const clickedCell = event.currentTarget;
            console.log('Clicked cell:', clickedCell);
            
            // Работаем только с этой ячейкой
            if (clickedCell.classList.contains('head-cell')) {
                handleCell(clickedCell);
            } else if (clickedCell.classList.contains('pants-cell')) {
                handleCell(clickedCell);
            }else if (clickedCell.classList.contains('torso-cell')) {
                handleCell(clickedCell);
            }else if (clickedCell.classList.contains('gloves-cell')) {
                handleCell(clickedCell);
            }else if (clickedCell.classList.contains('gorget-cell')) {
                handleCell(clickedCell);
            }else if (clickedCell.classList.contains('namasnik-cell')) {
                handleCell(clickedCell);
            }else if (clickedCell.classList.contains('naplech-cell')) {
                handleCell(clickedCell);
            }else if (clickedCell.classList.contains('sword1-cell')) {
                handleCell(clickedCell);
            }else if (clickedCell.classList.contains('ng-cell')) {
                handleCell(clickedCell);
            }else if (clickedCell.classList.contains('brass-cell')) {
                handleCell(clickedCell);
            }else if (clickedCell.classList.contains('bag-cell')) {
                handleCell(clickedCell);
            }else if (clickedCell.classList.contains('lokti-cell')) {
                handleCell(clickedCell);
            }else if (clickedCell.classList.contains('sword3-cell')) {
                handleCell(clickedCell);
            }










        });
        
    
    
    });

}

function handleCell(cell) {
    // Логика только для *-cell
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

       /* Вывод информации только для определённых объектов*/ 
        const description = img.getAttribute('data-description');
        const pros = img.getAttribute('data-pros');
        const cons = img.getAttribute('data-cons');
        const rating = img.getAttribute('data-rating');
        fillPros(description,pros,cons,rating);

}

function closeTooltip() {
    document.getElementById('tooltipContainer').style.display = 'none';
   
}


function fillPros(desc,Pros,cons,rating) {
    const prosList = [Pros.split('\n')];
    const consList = [cons.split('\n')];
    const detContainer = document.querySelector('.details');
    const prosContainer = document.querySelector('.pros');
    const consContainer = document.querySelector('.cons');
    const starsContainer = document.querySelector('.stars');
    /*Очищаем перед отправкой*/
    prosContainer.innerHTML = '<h3>Плюсы</h3>';
    consContainer.innerHTML = '<h3>Минусы</h3>';
    detContainer.innerHTML = `
      <section>
        <h3><strong>Описание</strong></h3>
        <div>${desc}</div>
      </section>
    `;
    let stars = '';
    for (let i = 0; i < 5; i++) {
        stars += i < rating ? '★' : '☆';
    }
    starsContainer.innerHTML = `
      <section>
        <h3><strong>Рейтинг</strong></h3>
        <div>${stars}</div>
      </section>
    `;

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
