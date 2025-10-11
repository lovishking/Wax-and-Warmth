// Mobile-friendly newsletter functionality for Vercel deployment
// Simple client-side email collection with localStorage

// Function to submit newsletter form
function submitNewsletter(event) {
    event.preventDefault(); // Prevent default form submission
    
    const emailInput = document.getElementById('emailInput');
    const submitBtn = document.getElementById('submitBtn');
    const responseMessage = document.getElementById('responseMessage');
    
    const email = emailInput.value.trim();
    
    // Validate email
    if (!isValidEmail(email)) {
        showMessage('Please enter a valid email address.', 'error', responseMessage);
        return;
    }
    
    // Check if email is already subscribed (using localStorage)
    const subscribers = getSubscribers();
    if (subscribers.includes(email.toLowerCase())) {
        showMessage('You are already subscribed to our newsletter!', 'info', responseMessage);
        return;
    }
    
    // Show loading state
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Subscribing...';
    submitBtn.disabled = true;
    
    // Simulate API call delay for better UX
    setTimeout(() => {
        try {
            // Add email to localStorage
            subscribers.push(email.toLowerCase());
            localStorage.setItem('newsletter_subscribers', JSON.stringify(subscribers));
            
            // Add subscription timestamp
            const subscription = {
                email: email.toLowerCase(),
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent
            };
            
            // Store detailed subscription info
            const subscriptionHistory = getSubscriptionHistory();
            subscriptionHistory.push(subscription);
            localStorage.setItem('newsletter_subscription_history', JSON.stringify(subscriptionHistory));
            
            // Clear form and show success message
            emailInput.value = '';
            showMessage('🎉 Thank you for subscribing! You\'ll receive updates about our latest candles and special offers.', 'success', responseMessage);
            
            // Optional: Send to external service (like Mailchimp, ConvertKit, etc.)
            sendToExternalService(email);
            
        } catch (error) {
            console.error('Newsletter subscription error:', error);
            showMessage('Sorry, something went wrong. Please try again later.', 'error', responseMessage);
        } finally {
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }, 800); // Small delay for better UX
}

// Function to validate email format
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Function to show messages with different styles
function showMessage(message, type, element) {
    element.innerHTML = message;
    element.style.display = 'block';
    
    // Set colors based on message type
    switch(type) {
        case 'success':
            element.style.color = '#28a745';
            element.style.backgroundColor = '#d4edda';
            element.style.border = '1px solid #c3e6cb';
            break;
        case 'error':
            element.style.color = '#dc3545';
            element.style.backgroundColor = '#f8d7da';
            element.style.border = '1px solid #f5c6cb';
            break;
        case 'info':
            element.style.color = '#0c5460';
            element.style.backgroundColor = '#d1ecf1';
            element.style.border = '1px solid #bee5eb';
            break;
        default:
            element.style.color = '#28a745';
            element.style.backgroundColor = '#d4edda';
            element.style.border = '1px solid #c3e6cb';
    }
    
    element.style.padding = '10px';
    element.style.borderRadius = '5px';
    element.style.marginTop = '10px';
    
    // Auto-hide message after 5 seconds
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

// Function to get existing subscribers from localStorage
function getSubscribers() {
    try {
        const subscribers = localStorage.getItem('newsletter_subscribers');
        return subscribers ? JSON.parse(subscribers) : [];
    } catch (error) {
        console.error('Error reading subscribers:', error);
        return [];
    }
}

// Function to get subscription history
function getSubscriptionHistory() {
    try {
        const history = localStorage.getItem('newsletter_subscription_history');
        return history ? JSON.parse(history) : [];
    } catch (error) {
        console.error('Error reading subscription history:', error);
        return [];
    }
}

// Function to send email to external newsletter service
function sendToExternalService(email) {
    console.log('Newsletter subscription:', email);
    
    // You can integrate with external services here
    // Example: EmailJS, Mailchimp API, webhooks, etc.
}

// Function to get all subscribers (for admin purposes)
function getAllSubscribers() {
    return getSubscribers();
}

// Function to get subscription count
function getSubscriberCount() {
    return getSubscribers().length;
}

// Function to export subscribers (for admin purposes)
function exportSubscribers() {
    const subscribers = getSubscribers();
    const history = getSubscriptionHistory();
    
    const exportData = {
        subscribers: subscribers,
        subscriptionHistory: history,
        exportDate: new Date().toISOString(),
        totalCount: subscribers.length
    };
    
    // Create downloadable file
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `newsletter-subscribers-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Initialize newsletter functionality when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Add mobile-friendly touch events
    if ('ontouchstart' in window) {
        const submitBtns = document.querySelectorAll('#submitBtn');
        submitBtns.forEach(btn => {
            btn.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.95)';
            });
            btn.addEventListener('touchend', function() {
                this.style.transform = 'scale(1)';
            });
        });
    }
    
    // Add form validation on input
    const emailInputs = document.querySelectorAll('#emailInput');
    emailInputs.forEach(input => {
        input.addEventListener('input', function() {
            const responseMessage = this.closest('form').nextElementSibling;
            if (responseMessage && responseMessage.id === 'responseMessage') {
                responseMessage.style.display = 'none';
            }
        });
        
        // Add mobile-friendly focus effects
        input.addEventListener('focus', function() {
            this.style.borderColor = '#007bff';
            this.style.boxShadow = '0 0 0 2px rgba(0,123,255,.25)';
        });
        
        input.addEventListener('blur', function() {
            this.style.borderColor = '#ced4da';
            this.style.boxShadow = 'none';
        });
    });
    
    console.log('Newsletter functionality initialized for mobile');
});

// Make functions available globally
window.submitNewsletter = submitNewsletter;
window.getAllSubscribers = getAllSubscribers;
window.getSubscriberCount = getSubscriberCount;
window.exportSubscribers = exportSubscribers;