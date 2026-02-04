const API_URL = ""; // Relative path since served from same origin

// State
let token = localStorage.getItem('token');
let userEmail = localStorage.getItem('userEmail');

// UI Elements
const screenAuth = document.getElementById('auth-screen');
const screenDashboard = document.getElementById('dashboard-screen');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const emailList = document.getElementById('email-list');
const composeModal = document.getElementById('compose-modal');

// Init
if(token) {
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
    } catch(err) {
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
    } catch(err) {
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

function showDashboard() {
    screenAuth.classList.remove('active');
    screenDashboard.classList.add('active');
    document.getElementById('user-email-display').textContent = userEmail;
    loadInbox();
}

// Emails
async function loadInbox(category = 'all') {
    // Update active menu
    document.querySelectorAll('.menu li').forEach(li => li.classList.remove('active'));
    event?.target.classList.add('active'); // Assumption: triggered by click

    try {
        const res = await axios.get('/emails/inbox', {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        let emails = res.data;
        if(category !== 'all') {
            emails = emails.filter(e => e.category === category);
        }

        renderEmails(emails);
    } catch(err) {
        if(err.response?.status === 401) logout();
        else showToast('Failed to load inbox');
    }
}

function renderEmails(emails) {
    emailList.innerHTML = '';
    if(emails.length === 0) {
        emailList.innerHTML = '<div style="text-align:center;color:var(--text-secondary);padding:2rem;">No emails found</div>';
        return;
    }

    emails.forEach(email => {
        const div = document.createElement('div');
        div.className = 'email-item';
        div.innerHTML = `
            <div class="email-header">
                <span class="sender">${email.sender_email}</span>
                <span class="time">${new Date(email.timestamp).toLocaleDateString()}</span>
            </div>
            <div class="subject">${email.subject}</div>
            <div class="preview">${email.body}</div>
            <span class="tag ${email.category}">${email.category}</span>
        `;
        emailList.appendChild(div);
    });
}

// Compose
function openCompose() { composeModal.classList.add('active'); }
function closeCompose() { composeModal.classList.remove('active'); }

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
    } catch(err) {
        showToast('Failed to send: ' + (err.response?.data?.detail || 'Error'), true);
    }
});

// Utils
function showToast(msg, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.style.background = isError ? '#ef4444' : '#10b981';
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}
