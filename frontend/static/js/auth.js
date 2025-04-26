// Валидация формы регистрации
document.getElementById('register-form')?.addEventListener('submit', function(e) {
  const password = document.getElementById('password').value;
  const confirm = document.getElementById('confirm-password')?.value;

  if (password.length < 8) {
    e.preventDefault();
    showAlert('Пароль должен содержать минимум 8 символов', 'danger');
  }

  if (confirm && password !== confirm) {
    e.preventDefault();
    showAlert('Пароли не совпадают', 'danger');
  }
});

// Показать/скрыть пароль
document.querySelectorAll('.toggle-password').forEach(button => {
  button.addEventListener('click', function() {
    const input = this.previousElementSibling;
    const icon = this.querySelector('i');

    if (input.type === 'password') {
      input.type = 'text';
      icon.classList.replace('bi-eye-slash', 'bi-eye');
    } else {
      input.type = 'password';
      icon.classList.replace('bi-eye', 'bi-eye-slash');
    }
  });
});