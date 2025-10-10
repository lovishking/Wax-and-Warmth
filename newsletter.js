/**
 * Newsletter subscription enhancement script
 * Provides better UX for newsletter subscription forms
 */

document.addEventListener('DOMContentLoaded', function() {
    const newsletterForms = document.querySelectorAll('#newsletterForm');
    
    newsletterForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('.sign');
            const emailInput = form.querySelector('input[type="email"]');
            const responseMessage = form.parentNode.querySelector('#responseMessage');
            
            // Disable submit button to prevent double submission
            submitButton.disabled = true;
            submitButton.textContent = 'Signing Up...';
            
            // Clear previous messages
            if (responseMessage) {
                responseMessage.textContent = '';
                responseMessage.style.color = 'green';
            }
            
            // Basic email validation
            const email = emailInput.value.trim();
            if (!email || !isValidEmail(email)) {
                e.preventDefault();
                showMessage(responseMessage, 'Please enter a valid email address.', 'error');
                resetButton(submitButton);
                return;
            }
            
            // For AJAX submission (optional enhancement)
            if (form.dataset.ajax === 'true') {
                e.preventDefault();
                submitNewsletterAjax(form, emailInput, submitButton, responseMessage);
            }
        });
    });
});

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showMessage(messageElement, text, type) {
    if (messageElement) {
        messageElement.textContent = text;
        messageElement.style.color = type === 'error' ? 'red' : 'green';
        messageElement.style.display = 'block';
    }
}

function resetButton(button) {
    button.disabled = false;
    button.textContent = 'Sign Up';
}

function submitNewsletterAjax(form, emailInput, submitButton, responseMessage) {
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage(responseMessage, data.message, 'success');
            emailInput.value = '';
        } else {
            showMessage(responseMessage, data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage(responseMessage, 'An error occurred. Please try again.', 'error');
    })
    .finally(() => {
        resetButton(submitButton);
    });
}

// Optional: Add loading animation for better UX
function addLoadingAnimation() {
    const style = document.createElement('style');
    style.textContent = `
        .sign:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        .sign:disabled:after {
            content: '';
            display: inline-block;
            width: 12px;
            height: 12px;
            margin-left: 5px;
            border: 2px solid #ffffff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        #responseMessage {
            margin-top: 10px;
            font-size: 0.9rem;
            font-weight: 500;
        }
    `;
    document.head.appendChild(style);
}

// Add loading animation styles
addLoadingAnimation();