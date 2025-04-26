class Cart {
  constructor() {
    this.items = JSON.parse(localStorage.getItem('cart')) || [];
  }

  addItem(productId, quantity = 1) {
    const existing = this.items.find(item => item.id === productId);

    if (existing) {
      existing.quantity += quantity;
    } else {
      this.items.push({ id: productId, quantity });
    }

    this.save();
  }

  removeItem(productId) {
    this.items = this.items.filter(item => item.id !== productId);
    this.save();
  }

  save() {
    localStorage.setItem('cart', JSON.stringify(this.items));
    this.updateBadge();
  }

  updateBadge() {
    const total = this.items.reduce((sum, item) => sum + item.quantity, 0);
    document.querySelectorAll('.cart-badge').forEach(badge => {
      badge.textContent = total;
      badge.style.display = total > 0 ? 'inline-block' : 'none';
    });
  }
}

// Инициализация корзины
const cart = new Cart();
cart.updateBadge();

// Обработчики для кнопок "В корзину"
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('add-to-cart')) {
    const productId = e.target.dataset.id;
    cart.addItem(productId);
    showAlert('Товар добавлен в корзину', 'success');
  }
});