// Toggle Login/Register Form
document.addEventListener('DOMContentLoaded', function () {
    const toggleForms = document.querySelectorAll('.toggle-form');
    if (toggleForms) {
        toggleForms.forEach(function (button) {
            button.addEventListener('click', function () {
                const loginForm = document.querySelector('.login');
                const registrationForm = document.querySelector('.registration');

                if (loginForm && registrationForm) {
                    loginForm.classList.toggle('d-none');
                    registrationForm.classList.toggle('d-none');
                } else {
                    console.error('Login or Registration form is missing in the DOM.');
                }
            });
        });
    }

    // Account Page Tabs
    const accountTabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    if (accountTabs) {
        accountTabs.forEach(function (tab) {
            tab.addEventListener('click', function (e) {
                e.preventDefault();
                const target = this.getAttribute('data-bs-target');

                // Hide all tab panes
                const tabPanes = document.querySelectorAll('.tab-pane');
                if (tabPanes) {
                    tabPanes.forEach(function (pane) {
                        pane.classList.remove('show', 'active');
                    });
                }

                // Activate the target tab pane
                const targetPane = document.querySelector(target);
                if (targetPane) {
                    targetPane.classList.add('show', 'active');
                } else {
                    console.error(`Tab pane with target ${target} is missing in the DOM.`);
                }

                // Update active tab
                accountTabs.forEach(function (t) {
                    t.classList.remove('active');
                });
                this.classList.add('active');
            });
        });
    }
});
