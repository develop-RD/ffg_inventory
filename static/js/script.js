// Этот код уже встроен в profile.html, но если вы используете отдельный файл script.js, добавьте туда:

function loadWeaponClass(weaponClass) {
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('weapon_class', weaponClass);
    window.location.href = currentUrl.toString();
}

function saveWeaponClass() {
    const urlParams = new URLSearchParams(window.location.search);
    const weaponClass = urlParams.get('weapon_class');
    
    fetch("/set_weapon_class", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `weapon_class=${weaponClass}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            //alert('Класс оружия сохранен как основной');
        } else {
            alert('Ошибка при сохранении класса оружия');
        }
    });
}
