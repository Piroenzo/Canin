window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-producto');
    const lista = document.getElementById('admin-productos-lista');
    const imgInput = document.getElementById('imgfile');
    const previewImg = document.getElementById('preview-img');

    // Previsualización de imagen
    imgInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = e => {
                previewImg.src = e.target.result;
                previewImg.style.display = 'block';
            };
            reader.readAsDataURL(this.files[0]);
        } else {
            previewImg.style.display = 'none';
        }
    });

    // Cargar productos desde el backend
    async function cargarProductos() {
        const res = await fetch('/api/productos');
        const productos = await res.json();
        renderProductos(productos);
    }

    // Validación avanzada del formulario de productos
    form.addEventListener('submit', async e => {
        e.preventDefault();
        let errores = [];
        const nombre = form.nombre.value.trim();
        const desc = form.desc.value.trim();
        const file = imgInput.files[0];
        if (nombre.length < 2 || nombre.length > 40) {
            errores.push('El nombre debe tener entre 2 y 40 caracteres.');
        }
        if (desc.length < 10 || desc.length > 300) {
            errores.push('La descripción debe tener entre 10 y 300 caracteres.');
        }
        if (!file) {
            errores.push('Debes seleccionar una imagen.');
        }
        let errorDiv = document.getElementById('admin-errores');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'admin-errores';
            errorDiv.style.color = '#e7743e';
            errorDiv.style.marginBottom = '10px';
            form.insertBefore(errorDiv, form.firstChild);
        }
        if (errores.length > 0) {
            errorDiv.innerHTML = errores.map(e => `<div>${e}</div>`).join('');
            return;
        } else {
            errorDiv.innerHTML = '';
        }
        // Subir imagen
        const data = new FormData();
        data.append('file', file);
        const resImg = await fetch('/api/upload_img', { method: 'POST', body: data });
        const resImgJson = await resImg.json();
        if (!resImgJson.url) {
            alert('Error al subir la imagen');
            return;
        }
        // Crear producto
        await fetch('/api/productos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, img: resImgJson.url, desc })
        });
        form.reset();
        previewImg.style.display = 'none';
        form.nombre.focus();
        cargarProductos();
    });

    function renderProductos(productos) {
        lista.innerHTML = '';
        productos.forEach(prod => {
            const card = document.createElement('div');
            card.className = 'producto-card';
            card.innerHTML = `
                <img src="${prod.img}" alt="Producto" class="img-producto">
                <h3>${prod.nombre}</h3>
                <p>${prod.desc}</p>
                <div class="admin-acciones">
                    <button class="btn-editar" data-nombre="${prod.nombre}">Editar</button>
                    <button class="btn-eliminar" data-nombre="${prod.nombre}">Eliminar</button>
                </div>
            `;
            lista.appendChild(card);
        });
        // Acciones eliminar
        document.querySelectorAll('.btn-eliminar').forEach(btn => {
            btn.onclick = async () => {
                if (confirm('¿Seguro que deseas eliminar este producto?')) {
                    await fetch('/api/productos', {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ nombre: btn.dataset.nombre })
                    });
                    cargarProductos();
                }
            };
        });
        // Acciones editar
        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.onclick = () => {
                const prod = productos.find(p => p.nombre === btn.dataset.nombre);
                if (prod) abrirModalEditar(prod);
            };
        });
    }

    cargarProductos();

    // Edición de productos
    const modalEditar = document.getElementById('modal-editar');
    const formEditar = document.getElementById('form-editar');
    const editNombre = document.getElementById('edit-nombre');
    const editDesc = document.getElementById('edit-desc');
    const editImgInput = document.getElementById('edit-imgfile');
    const editPreviewImg = document.getElementById('edit-preview-img');
    const cancelarEdicion = document.getElementById('cancelar-edicion');
    let productoEditando = null;

    function abrirModalEditar(prod) {
        productoEditando = prod;
        editNombre.value = prod.nombre;
        editDesc.value = prod.desc;
        editPreviewImg.src = prod.img;
        editPreviewImg.style.display = 'block';
        editImgInput.value = '';
        modalEditar.style.display = 'flex';
    }
    cancelarEdicion.onclick = () => {
        modalEditar.style.display = 'none';
        productoEditando = null;
    };
    editImgInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = e => {
                editPreviewImg.src = e.target.result;
                editPreviewImg.style.display = 'block';
            };
            reader.readAsDataURL(this.files[0]);
        } else {
            editPreviewImg.src = productoEditando ? productoEditando.img : '';
        }
    });
    formEditar.onsubmit = async e => {
        e.preventDefault();
        if (!productoEditando) return;
        const nuevoNombre = editNombre.value.trim();
        const nuevoDesc = editDesc.value.trim();
        let nuevaImg = productoEditando.img;
        const file = editImgInput.files[0];
        if (file) {
            const data = new FormData();
            data.append('file', file);
            const resImg = await fetch('/api/upload_img', { method: 'POST', body: data });
            const resImgJson = await resImg.json();
            if (resImgJson.url) nuevaImg = resImgJson.url;
        }
        await fetch('/api/productos', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nombre: productoEditando.nombre,
                nuevo: { nombre: nuevoNombre, desc: nuevoDesc, img: nuevaImg }
            })
        });
        modalEditar.style.display = 'none';
        productoEditando = null;
        cargarProductos();
    };
}); 