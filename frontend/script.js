/* ========================================
   Developer Portfolio - Main Script
   ======================================== */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const contactForm = document.getElementById('contactForm');
const submitBtn = document.getElementById('submitBtn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');
const formMessage = document.getElementById('formMessage');
const successModal = document.getElementById('successModal');
const modalClose = document.getElementById('modalClose');
const modalBtn = document.getElementById('modalBtn');
const charCount = document.getElementById('charCount');
const commentField = document.getElementById('comment');

// Form fields
const fields = {
    name: document.getElementById('name'),
    email: document.getElementById('email'),
    phone: document.getElementById('phone'),
    comment: document.getElementById('comment')
};

// Error elements
const errors = {
    name: document.getElementById('nameError'),
    email: document.getElementById('emailError'),
    phone: document.getElementById('phoneError'),
    comment: document.getElementById('commentError')
};

/* ========================================
   Character Counter
   ======================================== */
if (commentField && charCount) {
    commentField.addEventListener('input', () => {
        const count = commentField.value.length;
        charCount.textContent = count;
        
        if (count > 900) {
            charCount.style.color = 'var(--error)';
        } else if (count > 700) {
            charCount.style.color = 'var(--warning)';
        } else {
            charCount.style.color = 'var(--text-muted)';
        }
    });
}

/* ========================================
   Phone Formatting
   ======================================== */
if (fields.phone) {
    fields.phone.addEventListener('input', (e) => {
        // Remove all non-digit and non-plus characters
        let value = e.target.value.replace(/[^\d+]/g, '');
        
        // Ensure + is only at the start
        if (value.includes('+')) {
            const parts = value.split('');
            const plusIndex = parts.indexOf('+');
            if (plusIndex !== 0) {
                parts.splice(plusIndex, 1);
                value = parts.join('');
            }
            // Remove additional + signs
            value = value.slice(0, 1) + value.slice(1).replace(/\+/g, '');
        }
        
        e.target.value = value;
    });
}

/* ========================================
   Form Validation
   ======================================== */
function validateField(fieldName, value) {
    switch (fieldName) {
        case 'name':
            if (!value || value.length < 2) {
                return 'Имя должно содержать минимум 2 символа';
            }
            if (value.length > 100) {
                return 'Имя не должно превышать 100 символов';
            }
            if (!/^[a-zA-Zа-яА-ЯёЁ\s\-']+$/.test(value)) {
                return 'Имя должно содержать только буквы, пробелы и дефисы';
            }
            return null;
            
        case 'email':
            if (!value) {
                return 'Email обязателен';
            }
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                return 'Введите корректный email адрес';
            }
            return null;
            
        case 'phone':
            if (value) {
                // Check for letters
                if (/[a-zA-Zа-яА-ЯёЁ]/.test(value)) {
                    return 'Телефон должен содержать только цифры';
                }
                // Remove + for length check
                const digitsOnly = value.replace(/\D/g, '');
                if (digitsOnly.length < 10) {
                    return 'Телефон должен содержать минимум 10 цифр';
                }
                if (digitsOnly.length > 15) {
                    return 'Телефон не должен превышать 15 цифр';
                }
            }
            return null;
            
        case 'comment':
            if (!value || value.length < 10) {
                return 'Сообщение должно содержать минимум 10 символов';
            }
            if (value.length > 1000) {
                return 'Сообщение не должно превышать 1000 символов';
            }
            return null;
            
        default:
            return null;
    }
}

function showFieldError(fieldName, message) {
    const field = fields[fieldName];
    const error = errors[fieldName];
    
    if (field && error) {
        field.classList.add('error');
        error.textContent = message;
    }
}

function clearFieldError(fieldName) {
    const field = fields[fieldName];
    const error = errors[fieldName];
    
    if (field && error) {
        field.classList.remove('error');
        error.textContent = '';
    }
}

function clearAllErrors() {
    Object.keys(fields).forEach(fieldName => {
        clearFieldError(fieldName);
    });
}

// Real-time validation
Object.keys(fields).forEach(fieldName => {
    const field = fields[fieldName];
    if (field) {
        field.addEventListener('blur', () => {
            const error = validateField(fieldName, field.value.trim());
            if (error) {
                showFieldError(fieldName, error);
            } else {
                clearFieldError(fieldName);
            }
        });
        
        field.addEventListener('input', () => {
            if (field.classList.contains('error')) {
                const error = validateField(fieldName, field.value.trim());
                if (!error) {
                    clearFieldError(fieldName);
                }
            }
        });
    }
});

/* ========================================
   Form Submission
   ======================================== */
contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    clearAllErrors();
    
    // Validate all fields
    let isValid = true;
    const formData = {};
    
    Object.keys(fields).forEach(fieldName => {
        const value = fields[fieldName].value.trim();
        formData[fieldName] = value;
        
        const error = validateField(fieldName, value);
        if (error) {
            showFieldError(fieldName, error);
            isValid = false;
        }
    });
    
    if (!isValid) {
        showFormMessage('Пожалуйста, исправьте ошибки в форме', 'error');
        return;
    }
    
    // Remove empty phone
    if (!formData.phone) {
        delete formData.phone;
    }
    
    // Show loading state
    setLoading(true);
    hideFormMessage();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/contact`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showSuccessModal(data.data);
            contactForm.reset();
            charCount.textContent = '0';
        } else {
            // Handle validation errors from server
            if (data.details && Array.isArray(data.details)) {
                data.details.forEach(detail => {
                    const field = detail.loc[detail.loc.length - 1];
                    if (fields[field]) {
                        showFieldError(field, detail.msg);
                    }
                });
                showFormMessage('Пожалуйста, исправьте ошибки в форме', 'error');
            } else {
                showFormMessage(data.message || 'Произошла ошибка при отправке', 'error');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        showFormMessage('Ошибка соединения с сервером. Попробуйте позже.', 'error');
    } finally {
        setLoading(false);
    }
});

/* ========================================
   UI Helpers
   ======================================== */
function setLoading(loading) {
    submitBtn.disabled = loading;
    btnText.style.display = loading ? 'none' : 'inline';
    btnLoader.style.display = loading ? 'flex' : 'none';
}

function showFormMessage(message, type) {
    formMessage.textContent = message;
    formMessage.className = `form-message ${type}`;
}

function hideFormMessage() {
    formMessage.className = 'form-message';
    formMessage.textContent = '';
}

function showSuccessModal(data) {
    const aiAnalysis = document.getElementById('aiAnalysis');
    const analysisContent = aiAnalysis.querySelector('.analysis-content');
    
    if (data.ai_analysis) {
        const analysis = data.ai_analysis;
        const sentimentClass = analysis.sentiment === 'positive' ? 'positive' : 
                               analysis.sentiment === 'negative' ? 'negative' : 'neutral';
        
        analysisContent.innerHTML = `
            <div class="analysis-item">
                <span class="analysis-label">Тональность:</span>
                <span class="analysis-value ${sentimentClass}">${getSentimentText(analysis.sentiment)}</span>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Категория:</span>
                <span class="analysis-value">${getCategoryText(analysis.category)}</span>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Приоритет:</span>
                <span class="analysis-value">${getPriorityText(analysis.priority)}</span>
            </div>
        `;
        aiAnalysis.style.display = 'block';
    } else {
        aiAnalysis.style.display = 'none';
    }
    
    successModal.classList.add('active');
}

function hideSuccessModal() {
    successModal.classList.remove('active');
}

function getSentimentText(sentiment) {
    const texts = {
        positive: 'Позитивная',
        negative: 'Негативная',
        neutral: 'Нейтральная'
    };
    return texts[sentiment] || sentiment;
}

function getCategoryText(category) {
    const texts = {
        project_inquiry: 'Проект',
        collaboration: 'Сотрудничество',
        job_offer: 'Вакансия',
        general_question: 'Общий вопрос',
        feedback: 'Отзыв',
        support: 'Поддержка',
        other: 'Другое'
    };
    return texts[category] || category;
}

function getPriorityText(priority) {
    const texts = {
        high: 'Высокий',
        medium: 'Средний',
        low: 'Низкий'
    };
    return texts[priority] || priority;
}

// Modal event listeners
modalClose.addEventListener('click', hideSuccessModal);
modalBtn.addEventListener('click', hideSuccessModal);
successModal.addEventListener('click', (e) => {
    if (e.target === successModal) {
        hideSuccessModal();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && successModal.classList.contains('active')) {
        hideSuccessModal();
    }
});

/* ========================================
   Smooth Scroll for Navigation
   ======================================== */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

/* ========================================
   Navbar Scroll Effect
   ======================================== */
const navbar = document.querySelector('.navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        navbar.style.background = 'rgba(10, 10, 15, 0.95)';
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
    } else {
        navbar.style.background = 'rgba(10, 10, 15, 0.8)';
        navbar.style.boxShadow = 'none';
    }
    
    lastScroll = currentScroll;
});

/* ========================================
   Intersection Observer for Animations
   ======================================== */
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements for animation
document.querySelectorAll('.about-card, .tech-item, .project-card, .info-card').forEach(el => {
    observer.observe(el);
});

/* ========================================
   Mobile Menu Toggle
   ======================================== */
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuBtn && navLinks) {
    mobileMenuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        mobileMenuBtn.classList.toggle('active');
    });
    
    // Close menu when clicking a link
    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
            mobileMenuBtn.classList.remove('active');
        });
    });
}

/* ========================================
   Console Welcome Message
   ======================================== */
console.log('%c🚀 Developer Portfolio', 'font-size: 24px; font-weight: bold; color: #6366f1;');
console.log('%cBuilt with ❤️ using FastAPI + Vanilla JS', 'font-size: 14px; color: #a1a1aa;');