// Галерея изображений товара
document.addEventListener('DOMContentLoaded', function() {
    const mainImage = document.querySelector('.col-md-6 img.img-fluid');
    const thumbnails = document.querySelectorAll('.img-thumbnail');
    
    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                // Обновляем основное изображение
                mainImage.src = this.src;
                mainImage.alt = this.alt;
                
                // Убираем активный класс у всех миниатюр
                thumbnails.forEach(t => t.classList.remove('active'));
                // Добавляем активный класс к текущей миниатюре
                this.classList.add('active');
            });
        });
        
        // Добавляем стиль для активной миниатюры
        const style = document.createElement('style');
        style.textContent = `
            .img-thumbnail.active {
                border-color: #0d6efd;
                box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
            }
        `;
        document.head.appendChild(style);
    }
});