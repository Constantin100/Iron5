// Анимация чисел в статистике
function animateNumbers() {
    const stats = document.querySelectorAll('.stat-number');
    
    stats.forEach(stat => {
        const target = parseInt(stat.getAttribute('data-count'));
        const duration = 2000; // 2 секунды на анимацию
        const step = target / duration * 10;
        let current = 0;
        
        const updateNumber = () => {
            if (current < target) {
                current += step;
                if (current > target) current = target;
                stat.textContent = Math.floor(current);
                requestAnimationFrame(updateNumber);
            }
        };
        
        updateNumber();
    });
}

// Запуск анимации при появлении элемента в viewport
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateNumbers();
            observer.unobserve(entry.target);
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const statistics = document.querySelector('.statistics');
    if (statistics) {
        observer.observe(statistics);
    }

    // Обработка бургер-меню
    const menuToggle = document.querySelector('.menu-toggle');
    const navContainer = document.querySelector('.nav-container');
    
    menuToggle?.addEventListener('click', () => {
        menuToggle.classList.toggle('active');
        navContainer.classList.toggle('active');
    });
}); 