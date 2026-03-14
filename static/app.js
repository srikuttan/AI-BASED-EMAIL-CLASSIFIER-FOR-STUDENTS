const API_URL = ""; // Relative path since served from same origin

// State
let token = localStorage.getItem('token');
let userEmail = localStorage.getItem('userEmail');
let currentCategory = 'all';

// UI Elements
const screenAuth = document.getElementById('auth-screen');
const screenDashboard = document.getElementById('dashboard-screen');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const emailList = document.getElementById('email-list');
const composeModal = document.getElementById('compose-modal');

// Init
if (token) {
    showDashboard();
}

// Auth Tabs
function showAuth(type) {
    document.getElementById('login-form').style.display = type === 'login' ? 'block' : 'none';
    document.getElementById('register-form').style.display = type === 'register' ? 'block' : 'none';
    document.getElementById('tab-login').classList.toggle('active', type === 'login');
    document.getElementById('tab-register').classList.toggle('active', type === 'register');
}

// Auth Logic
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    try {
        const res = await axios.post('/auth/login', { email, password });
        handleLoginSuccess(res.data.access_token, email);
    } catch (err) {
        showToast('Login failed: ' + (err.response?.data?.detail || 'Unknown error'), true);
    }
});

registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    try {
        const res = await axios.post('/auth/register', { email, password });
        handleLoginSuccess(res.data.access_token, email);
    } catch (err) {
        showToast('Registration failed: ' + (err.response?.data?.detail || 'Unknown error'), true);
    }
});

function handleLoginSuccess(accessToken, email) {
    token = accessToken;
    userEmail = email;
    localStorage.setItem('token', token);
    localStorage.setItem('userEmail', userEmail);
    showDashboard();
}

function logout() {
    token = null;
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    screenAuth.classList.add('active');
    screenDashboard.classList.remove('active');
}

let classificationEnabled = true;

function showDashboard() {
    screenAuth.classList.remove('active');
    screenDashboard.classList.add('active');
    const emailDisplay = document.getElementById('user-email-display');
    if (emailDisplay) emailDisplay.textContent = userEmail;

    // Also update modal email
    const modalEmail = document.getElementById('modal-user-email');
    if (modalEmail) modalEmail.textContent = userEmail;

    loadClassificationState();
    loadInbox();
}

async function loadClassificationState() {
    try {
        const res = await axios.get('/config/classification', {
            headers: { Authorization: `Bearer ${token}` }
        });
        classificationEnabled = res.data.enabled;
        updateClassificationToggle();
    } catch (err) {
        if (err.response?.status === 401) logout();
        else classificationEnabled = true;
        updateClassificationToggle();
    }
}

function updateClassificationToggle() {
    const btn = document.getElementById('classification-toggle');
    const wrap = document.querySelector('.classification-toggle-wrap');
    if (!btn || !wrap) return;
    btn.setAttribute('aria-pressed', classificationEnabled ? 'true' : 'false');
    wrap.setAttribute('aria-checked', classificationEnabled ? 'true' : 'false');
}

async function toggleClassification() {
    classificationEnabled = !classificationEnabled;
    try {
        await axios.patch('/config/classification', { enabled: classificationEnabled }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        updateClassificationToggle();
        showToast(classificationEnabled ? 'AI classification turned on' : 'AI classification turned off');
    } catch (err) {
        classificationEnabled = !classificationEnabled; // revert
        updateClassificationToggle();
        showToast('Failed to update setting', true);
    }
}

function getCurrentCategory() {
    return currentCategory;
}

function escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Emails
async function loadInbox(category = 'all') {
    currentCategory = category;

    // Update active menu by data-category
    document.querySelectorAll('.menu li').forEach(li => {
        li.classList.toggle('active', (li.getAttribute('data-category') || 'all') === category);
    });

    // Update page title
    const titles = {
        all: 'Inbox',
        Assignments: 'Assignments',
        Notices: 'Notices',
        Personal: 'Personal',
        Spam: 'Spam'
    };
    const titleEl = document.getElementById('page-title');
    if (titleEl) titleEl.textContent = titles[category] || 'Inbox';

    try {
        const res = await axios.get('/emails/inbox', {
            headers: { Authorization: `Bearer ${token}` }
        });

        let emails = res.data;
        if (category !== 'all') {
            emails = emails.filter(e => e.category === category);
        }

        renderEmails(emails);
    } catch (err) {
        if (err.response?.status === 401) logout();
        else showToast('Failed to load inbox', true);
    }
}

function renderEmails(emails) {
    emailList.innerHTML = '';
    if (emails.length === 0) {
        emailList.innerHTML = '<div class="email-list-empty"><span class="email-list-empty-icon">📭</span>No emails in this folder</div>';
        return;
    }

    emails.forEach(email => {
        const div = document.createElement('div');
        div.className = 'email-item';
        div.innerHTML = `
            <div class="email-header">
                <span class="sender">${escapeHtml(email.sender_email)}</span>
                <span class="time">${escapeHtml(new Date(email.timestamp).toLocaleDateString())}</span>
            </div>
            <div class="subject">${escapeHtml(email.subject)}</div>
            <div class="preview">${escapeHtml(email.body)}</div>
            <div class="email-footer">
                <span class="tag ${escapeHtml(email.category)}">${escapeHtml(email.category)}</span>
                <div class="category-select-wrap">
                    <label for="cat-${email.id}">Change:</label>
                    <select id="cat-${email.id}" class="category-select" data-email-id="${email.id}" title="Change category">
                        <option value="Assignments"${email.category === 'Assignments' ? ' selected' : ''}>Assignments</option>
                        <option value="Notices"${email.category === 'Notices' ? ' selected' : ''}>Notices</option>
                        <option value="Personal"${email.category === 'Personal' ? ' selected' : ''}>Personal</option>
                        <option value="Spam"${email.category === 'Spam' ? ' selected' : ''}>Spam</option>
                    </select>
                </div>
            </div>
        `;

        const select = div.querySelector('.category-select');
        select.addEventListener('change', (e) => {
            const newCategory = e.target.value;
            updateEmailCategory(email.id, newCategory);
        });

        emailList.appendChild(div);
    });
}

async function updateEmailCategory(emailId, category) {
    try {
        await axios.patch(`/emails/${emailId}/category`,
            { category },
            { headers: { Authorization: `Bearer ${token}` } }
        );
        showToast('Category updated');
        loadInbox(getCurrentCategory());
    } catch (err) {
        showToast('Failed to update: ' + (err.response?.data?.detail || 'Error'), true);
    }
}

// Compose
function openCompose() {
    composeModal.classList.add('active');
    composeModal.setAttribute('aria-hidden', 'false');
}
function closeCompose() {
    composeModal.classList.remove('active');
    composeModal.setAttribute('aria-hidden', 'true');
}

document.getElementById('compose-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const recipient_email = document.getElementById('compose-to').value;
    const subject = document.getElementById('compose-subject').value;
    const body = document.getElementById('compose-body').value;

    try {
        await axios.post('/emails/send',
            { recipient_email, subject, body },
            { headers: { Authorization: `Bearer ${token}` } }
        );
        showToast('Email sent!');
        closeCompose();
        document.getElementById('compose-form').reset();
        loadInbox('all'); // Refresh
    } catch (err) {
        showToast('Failed to send: ' + (err.response?.data?.detail || 'Error'), true);
    }
});

// Utils
function showToast(msg, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.classList.remove('toast-success', 'toast-error');
    toast.classList.add('show', isError ? 'toast-error' : 'toast-success');
    setTimeout(() => toast.classList.remove('show'), 3000);
}
