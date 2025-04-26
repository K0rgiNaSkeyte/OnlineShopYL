document.addEventListener('DOMContentLoaded', function() {
  // Инициализация корзины
  if (typeof localStorage.cart === 'undefined') {
    localStorage.setItem('cart', JSON.stringify([]));
  }

  // Загрузка товаров
  loadProducts();
});

async function loadProducts(page = 1) {
  try {
    const response = await fetch(`/api/products?page=${page}`);
    const data = await response.json();

    renderProducts(data.products);
    renderPagination(data.totalPages, page);
  } catch (error) {
    console.error('Ошибка загрузки товаров:', error);
  }
}

function renderProducts(products) {
  const container = document.getElementById('products-container');
  container.innerHTML = products.map(product => `
    <div class="col-md-4 mb-4">
      <div class="card product-card h-100">
        <img src="/static/images/products/${product.id}.jpg"
             class="card-img-top product-img"
             alt="${product.name}">
        <div class="card-body">
          <h5 class="card-title">${product.name}</h5>
          <p class="card-text">${product.description}</p>
          <p class="text-success fw-bold">${product.price} руб.</p>
          <button class="btn btn-primary add-to-cart"
                  data-id="${product.id}">
            В корзину
          </button>
        </div>
      </div>
    </div>
  `).join('');
}