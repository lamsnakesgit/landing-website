document.addEventListener('DOMContentLoaded', () => {
    const slidesWrapper = document.getElementById('slidesWrapper');
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const dots = document.querySelectorAll('.dot');
    const progressBar = document.getElementById('progressBar');
    const container = document.querySelector('.presentation-container');
    
    let currentSlide = 0;
    const totalSlides = slides.length;
    
    // Переменные для свайпов
    let touchStartY = 0;
    let touchEndY = 0;
    const swipeThreshold = 50; // Минимальное расстояние для распознавания свайпа
    
    // Переменные для скролла колесиком
    let lastScrollTime = 0;
    const scrollCooldown = 800; // Таймаут между прокрутками (мс)

    // Функция обновления состояния презентации
    function updatePresentation() {
        // Прокрутка слайдов по вертикали
        slidesWrapper.style.transform = `translateY(-${currentSlide * 100}%)`;
        
        // Обновление активного класса на слайдах
        slides.forEach((slide, index) => {
            if (index === currentSlide) {
                slide.classList.add('active');
            } else {
                slide.classList.remove('active');
            }
        });
        
        // Обновление точек навигации
        dots.forEach((dot, index) => {
            if (index === currentSlide) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
        
        // Обновление прогресс-бара
        const progressPercentage = ((currentSlide + 1) / totalSlides) * 100;
        progressBar.style.width = `${progressPercentage}%`;
        
        // Изменение цвета темы навигации в зависимости от слайда
        const activeSlide = slides[currentSlide];
        if (activeSlide.classList.contains('theme-dark')) {
            progressBar.style.backgroundColor = '#EFECE5'; // Белый на темном
            prevBtn.style.color = '#EFECE5';
            prevBtn.style.background = 'rgba(255,255,255,0.1)';
            prevBtn.style.borderColor = 'rgba(255,255,255,0.15)';
            
            nextBtn.style.color = '#EFECE5';
            nextBtn.style.background = 'rgba(255,255,255,0.1)';
            nextBtn.style.borderColor = 'rgba(255,255,255,0.15)';
        } else {
            progressBar.style.backgroundColor = '#755B4C'; // Коричневый на светлом
            prevBtn.style.color = '#755B4C';
            prevBtn.style.background = 'rgba(255,255,255,0.6)';
            prevBtn.style.borderColor = 'rgba(255,255,255,0.4)';
            
            nextBtn.style.color = '#755B4C';
            nextBtn.style.background = 'rgba(255,255,255,0.6)';
            nextBtn.style.borderColor = 'rgba(255,255,255,0.4)';
        }
        
        // Видимость кнопок навигации (скрываем «назад» на 1-м слайде и «вперед» на последнем)
        if (currentSlide === 0) {
            prevBtn.style.opacity = '0';
            prevBtn.style.pointerEvents = 'none';
        } else {
            prevBtn.style.opacity = '0.8';
            prevBtn.style.pointerEvents = 'auto';
        }
        
        if (currentSlide === totalSlides - 1) {
            nextBtn.style.opacity = '0';
            nextBtn.style.pointerEvents = 'none';
        } else {
            nextBtn.style.opacity = '0.8';
            nextBtn.style.pointerEvents = 'auto';
        }
    }
    
    // Навигация к определенному слайду
    function goToSlide(index) {
        if (index >= 0 && index < totalSlides) {
            currentSlide = index;
            updatePresentation();
        }
    }
    
    // Обработчики для кнопок навигации
    prevBtn.addEventListener('click', () => {
        goToSlide(currentSlide - 1);
    });
    
    nextBtn.addEventListener('click', () => {
        goToSlide(currentSlide + 1);
    });
    
    // Клик по точкам навигации
    dots.forEach((dot) => {
        dot.addEventListener('click', (e) => {
            const slideIndex = parseInt(e.target.getAttribute('data-slide'), 10);
            goToSlide(slideIndex);
        });
    });
    
    // Управление клавиатурой
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === ' ') {
            e.preventDefault();
            goToSlide(currentSlide + 1);
        } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
            e.preventDefault();
            goToSlide(currentSlide - 1);
        }
    });
    
    // Обработка скролла (колесико / тачпад) с ограничением частоты
    container.addEventListener('wheel', (e) => {
        const currentTime = new Date().getTime();
        if (currentTime - lastScrollTime < scrollCooldown) {
            e.preventDefault();
            return;
        }
        
        if (Math.abs(e.deltaY) > 10) {
            if (e.deltaY > 0) {
                goToSlide(currentSlide + 1);
            } else {
                goToSlide(currentSlide - 1);
            }
            lastScrollTime = currentTime;
            e.preventDefault();
        }
    }, { passive: false });
    
    // Обработка свайпов (мобильные устройства)
    container.addEventListener('touchstart', (e) => {
        touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });
    
    container.addEventListener('touchend', (e) => {
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();
    }, { passive: true });
    
    function handleSwipe() {
        const distance = touchStartY - touchEndY;
        if (Math.abs(distance) > swipeThreshold) {
            if (distance > 0) {
                // Свайп вверх -> следующий слайд
                goToSlide(currentSlide + 1);
            } else {
                // Свайп вниз -> предыдущий слайд
                goToSlide(currentSlide - 1);
            }
        }
    }
    
    // Инициализация при загрузке
    updatePresentation();
});
