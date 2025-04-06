    // Конфигурация пагинации
    const itemsPerPage = 20; // Количество товаров на странице
    let currentPage = 1;
    let totalProducts = 0;
    let totalPages = 1;

    // Проверка авторизации пользователя
    const isLoggedIn = false;

    // Функция для обновления кнопок авторизации
        function updateAuthButtons() {
            if (isLoggedIn) {
                $('#authButton').remove();
                $('#loginButton')
                    .text('Личный кабинет')
                    .removeClass('btn-outline-secondary')
                    .addClass('btn-outline-primary')
                    .click(function() {
                        window.location.href = '/account'; // Перенаправление в личный кабинет
                    });
            } else {
                $('#authButton').click(function() {
                    window.location.href = '/register'; // Перенаправление на регистрацию
                });
                $('#loginButton').click(function() {
                    window.location.href = '/login'; // Перенаправление на вход
                });
            }
        }

    // Функция для загрузки популярных товаров
    function loadPopularProducts(page = 1) {
        // В реальном проекте будет AJAX-запрос с параметрами пагинации
        // Пример: $.get(`/api/products/popular?page=${page}&limit=${itemsPerPage}`, ...)

        // Тестовые данные (в реальном проекте заменить на запрос к API)
        const allProducts = [];
        for (let i = 1; i <= 45; i++) { // Генерируем 45 тестовых товаров
            allProducts.push({
                id: i,
                name: `Товар ${i}`,
                description: `Описание товара ${i}`,
                price: Math.floor(Math.random() * 9000) + 1000,
                image: "https://via.placeholder.com/300"
            });
        }

        // Имитация пагинации на клиенте (в реальном проекте делается на сервере)
        totalProducts = allProducts.length;
        totalPages = Math.ceil(totalProducts / itemsPerPage);
        const startIdx = (page - 1) * itemsPerPage;
        const endIdx = startIdx + itemsPerPage;
        const products = allProducts.slice(startIdx, endIdx);

        // Отрисовка товаров
        $('#popularProducts').empty();
        products.forEach(product => {
            $('#popularProducts').append(`
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <img src="${product.image}" class="card-img-top" alt="${product.name}">
                        <div class="card-body">
                            <h5 class="card-title">${product.name}</h5>
                            <p class="card-text">${product.description}</p>
                            <p class="text-success">${product.price} руб.</p>
                            <a href="#" class="btn btn-primary">В корзину</a>
                        </div>
                    </div>
                </div>
            `);
        });

        // Обновление пагинации
        updatePagination(page);
    }

    // Функция для обновления пагинации
    function updatePagination(currentPage) {
        const pagination = $('#pagination');
        pagination.empty();

        // Кнопка "Назад"
        pagination.append(`
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage - 1}">Назад</a>
            </li>
        `);

        // Номера страниц
        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        if (startPage > 1) {
            pagination.append(`
                <li class="page-item">
                    <a class="page-link" href="#" data-page="1">1</a>
                </li>
                ${startPage > 2 ? '<li class="page-item disabled"><span class="page-link">...</span></li>' : ''}
            `);
        }

        for (let i = startPage; i <= endPage; i++) {
            pagination.append(`
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `);
        }

        if (endPage < totalPages) {
            pagination.append(`
                ${endPage < totalPages - 1 ? '<li class="page-item disabled"><span class="page-link">...</span></li>' : ''}
                <li class="page-item">
                    <a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a>
                </li>
            `);
        }

        // Кнопка "Вперед"
        pagination.append(`
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage + 1}">Вперед</a>
            </li>
        `);
    }

    // Обработчик кликов по пагинации
    $(document).on('click', '.page-link', function(e) {
        e.preventDefault();
        const page = $(this).data('page');
        if (page && page !== currentPage) {
            currentPage = parseInt(page);
            loadPopularProducts(currentPage);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    // Инициализация при загрузке страницы
    $(document).ready(function() {
        updateAuthButtons();
        loadPopularProducts(currentPage);
    });