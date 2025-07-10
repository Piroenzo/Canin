// Animación de entrada para las secciones
window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('section').forEach((sec, i) => {
        sec.style.opacity = 0;
        setTimeout(() => {
            sec.style.transition = 'opacity 1s';
            sec.style.opacity = 1;
        }, 400 + i * 300);
    });

    // Cargar productos desde la API
    async function cargarProductos() {
        const res = await fetch('/api/productos');
        const productos = await res.json();
        renderProductos(productos);
    }

    function renderProductos(productos) {
        const lista = document.getElementById('productos-lista');
        if (!lista) return;
        lista.innerHTML = '';
        productos.forEach((prod, idx) => {
            const card = document.createElement('div');
            card.className = 'producto-card';
            if (window.innerWidth > 800) {
                card.classList.add(idx % 2 === 0 ? 'left' : 'right');
            }
            let huellita = '';
            if (idx % 2 === 0) {
                huellita = '<span class="huellita-deco">🐾</span>';
            }
            card.innerHTML = `
                ${huellita}
                <img src="${prod.img}" alt="Producto" class="img-producto">
                <h3>${prod.nombre}</h3>
                <p>${prod.desc}</p>
                <a href="https://wa.me/5492323656292?text=Hola!%20Quiero%20consultar%20por%20${encodeURIComponent(prod.nombre)}" class="btn-wpp-producto" target="_blank">
                    Consultar por WhatsApp
                </a>
            `;
            lista.appendChild(card);
        });
    }

    cargarProductos();

    // Animación de aparición al hacer scroll
    function animarSecciones() {
        const secciones = document.querySelectorAll('.seccion-animada');
        const trigger = window.innerHeight * 0.85;
        secciones.forEach(sec => {
            const top = sec.getBoundingClientRect().top;
            if (top < trigger) {
                sec.classList.add('visible');
            }
        });
    }
    window.addEventListener('scroll', animarSecciones);
    animarSecciones();

    // Validación avanzada del formulario de contacto
    const formContacto = document.querySelector('.form-contacto');
    if (formContacto) {
        formContacto.addEventListener('submit', function(e) {
            let errores = [];
            const nombre = formContacto.nombre.value.trim();
            const email = formContacto.email.value.trim();
            const mensaje = formContacto.mensaje.value.trim();
            // Validar nombre
            if (nombre.length < 2 || nombre.length > 40) {
                errores.push('El nombre debe tener entre 2 y 40 caracteres.');
            }
            // Validar email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                errores.push('El correo electrónico no es válido.');
            }
            // Validar mensaje
            if (mensaje.length < 10 || mensaje.length > 500) {
                errores.push('El mensaje debe tener entre 10 y 500 caracteres.');
            }
            // Mostrar errores
            let errorDiv = document.getElementById('contacto-errores');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.id = 'contacto-errores';
                errorDiv.style.color = '#e7743e';
                errorDiv.style.marginBottom = '10px';
                formContacto.insertBefore(errorDiv, formContacto.firstChild);
            }
            if (errores.length > 0) {
                e.preventDefault();
                errorDiv.innerHTML = errores.map(e => `<div>${e}</div>`).join('');
            } else {
                errorDiv.innerHTML = '';
            }
        });
    }
}); 