// Admin Dashboard JavaScript
// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    loadProducts();
    setupImageDragDrop();
});

// Authentication check
function checkAuth() {
    const adminSession = localStorage.getItem('adminSession');
    const adminUsername = localStorage.getItem('adminUsername');
    
    if (!adminSession || adminSession !== 'active') {
        window.location.href = '/admin-login.html';
        return;
    }
    
    // Set username in header
    if (adminUsername) {
        document.getElementById('adminUsername').textContent = adminUsername;
    }
}

// Logout function
function logout() {
    // Clear all possible admin session keys
    localStorage.removeItem('adminSession');
    localStorage.removeItem('adminUsername');
    localStorage.removeItem('admin_session'); // Clean up old format if exists
    window.location.href = '/admin-login.html';
}

// Section navigation
function showSection(sectionName, element) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));
    
    // Remove active class from all nav cards
    const navCards = document.querySelectorAll('.nav-card');
    navCards.forEach(card => card.classList.remove('active'));
    
    // Show selected section
    document.getElementById(sectionName + '-section').classList.add('active');
    element.classList.add('active');
}

// Product management functions
let products = [];

function loadProducts() {
    const storedProducts = localStorage.getItem('waxProducts');
    if (storedProducts) {
        products = JSON.parse(storedProducts);
    }
    displayProducts();
}

function saveProducts() {
    localStorage.setItem('waxProducts', JSON.stringify(products));
    updateWebsiteProducts();
}

function addProduct(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const imageFile = document.getElementById('productImage').files[0];
    
    if (!imageFile) {
        showMessage('Please select an image for the product.', 'error');
        return;
    }
    
    // Convert image to base64
    const reader = new FileReader();
    reader.onload = function(e) {
        const product = {
            id: Date.now(),
            name: formData.get('productName'),
            price: parseInt(formData.get('productPrice')),
            description: formData.get('productDescription'),
            category: formData.get('productCategory'),
            stock: parseInt(formData.get('productStock')),
            image: e.target.result,
            dateAdded: new Date().toISOString()
        };
        
        products.push(product);
        saveProducts();
        displayProducts();
        clearForm();
        showMessage('Product added successfully!', 'success');
    };
    
    reader.readAsDataURL(imageFile);
}

function displayProducts() {
    const grid = document.getElementById('productsGrid');
    
    if (products.length === 0) {
        grid.innerHTML = '<p style="text-align: center; color: #666; grid-column: 1/-1;">No products added yet. Add your first product above!</p>';
        return;
    }
    
    grid.innerHTML = products.map(product => `
        <div class="product-card">
            <img src="${product.image}" alt="${product.name}">
            <h4>${product.name}</h4>
            <p><strong>₹${product.price}</strong></p>
            <p style="font-size: 0.9em; color: #666;">${product.description}</p>
            <p style="font-size: 0.8em; color: #888;">Stock: ${product.stock} | Category: ${product.category}</p>
            <div class="product-actions">
                <button class="btn btn-sm" onclick="editProduct(${product.id})" style="background: #17a2b8; color: white; padding: 8px 15px;">
                    ✏️ Edit
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})" style="padding: 8px 15px;">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `).join('');
}

function deleteProduct(productId) {
    if (confirm('Are you sure you want to delete this product?')) {
        products = products.filter(product => product.id !== productId);
        saveProducts();
        displayProducts();
        showMessage('Product deleted successfully!', 'success');
    }
}

function editProduct(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    // Fill form with product data
    document.getElementById('productName').value = product.name;
    document.getElementById('productPrice').value = product.price;
    document.getElementById('productDescription').value = product.description;
    document.getElementById('productCategory').value = product.category;
    document.getElementById('productStock').value = product.stock;
    
    // Show image preview
    const preview = document.getElementById('imagePreview');
    preview.src = product.image;
    preview.style.display = 'block';
    
    // Change form to edit mode
    const form = document.getElementById('productForm');
    form.setAttribute('data-edit-id', productId);
    form.onsubmit = function(e) {
        updateProduct(e, productId);
    };
    
    // Change button text
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.innerHTML = '💾 Update Product';
    
    // Scroll to form
    form.scrollIntoView({ behavior: 'smooth' });
}

function updateProduct(event, productId) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const imageFile = document.getElementById('productImage').files[0];
    
    const productIndex = products.findIndex(p => p.id === productId);
    if (productIndex === -1) return;
    
    const updateProductData = () => {
        products[productIndex] = {
            ...products[productIndex],
            name: formData.get('productName'),
            price: parseInt(formData.get('productPrice')),
            description: formData.get('productDescription'),
            category: formData.get('productCategory'),
            stock: parseInt(formData.get('productStock')),
            lastModified: new Date().toISOString()
        };
        
        saveProducts();
        displayProducts();
        resetForm();
        showMessage('Product updated successfully!', 'success');
    };
    
    if (imageFile) {
        const reader = new FileReader();
        reader.onload = function(e) {
            products[productIndex].image = e.target.result;
            updateProductData();
        };
        reader.readAsDataURL(imageFile);
    } else {
        updateProductData();
    }
}

function clearForm() {
    const form = document.getElementById('productForm');
    form.reset();
    document.getElementById('imagePreview').style.display = 'none';
    resetForm();
}

function resetForm() {
    const form = document.getElementById('productForm');
    form.removeAttribute('data-edit-id');
    form.onsubmit = addProduct;
    
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.innerHTML = '➕ Add Product';
}

// Image preview function
function previewImage(input) {
    const preview = document.getElementById('imagePreview');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Drag and drop functionality
function setupImageDragDrop() {
    const uploadArea = document.querySelector('.image-upload');
    const fileInput = document.getElementById('productImage');
    
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            fileInput.files = files;
            previewImage(fileInput);
        }
    });
}

// Message display function
function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

// Update website products (inject into home and shop pages)
function updateWebsiteProducts() {
    // This function will be called whenever products are updated
    // It updates the localStorage that the main website uses
    localStorage.setItem('websiteProducts', JSON.stringify(products));
    
    // Trigger a custom event that the main website can listen to
    window.dispatchEvent(new CustomEvent('productsUpdated', { detail: products }));
}

// Settings management
function saveSettings() {
    const settings = {
        siteName: document.getElementById('siteName').value,
        siteDescription: document.getElementById('siteDescription').value,
        contactEmail: document.getElementById('contactEmail').value,
        contactPhone: document.getElementById('contactPhone').value,
        lastUpdated: new Date().toISOString()
    };
    
    localStorage.setItem('websiteSettings', JSON.stringify(settings));
    showMessage('Settings saved successfully!', 'success');
}

// Load settings on page load
function loadSettings() {
    const settings = localStorage.getItem('websiteSettings');
    if (settings) {
        const settingsData = JSON.parse(settings);
        document.getElementById('siteName').value = settingsData.siteName || 'Wax and Warmth';
        document.getElementById('siteDescription').value = settingsData.siteDescription || '';
        document.getElementById('contactEmail').value = settingsData.contactEmail || 'realwaxandwarmth@gmail.com';
        document.getElementById('contactPhone').value = settingsData.contactPhone || '+91 6200835077';
    }
}

// Export products function (for backup)
function exportProducts() {
    const dataStr = JSON.stringify(products, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = 'wax-products-backup.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

// Import products function (for restore)
function importProducts(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const importedProducts = JSON.parse(e.target.result);
            if (confirm('This will replace all current products. Are you sure?')) {
                products = importedProducts;
                saveProducts();
                displayProducts();
                showMessage('Products imported successfully!', 'success');
            }
        } catch (error) {
            showMessage('Error importing products. Please check the file format.', 'error');
        }
    };
    reader.readAsText(file);
}

// Initialize settings when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadSettings();
});