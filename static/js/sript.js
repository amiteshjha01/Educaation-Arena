// Toggle Login/Register Form
document.addEventListener('DOMContentLoaded', function() {
    const toggleForms = document.querySelectorAll('.toggle-form');
    if (toggleForms) {
        toggleForms.forEach(button => {
            button.addEventListener('click', function() {
                document.querySelector('.login').classList.toggle('d-none');
                document.querySelector('.signup').classList.toggle('d-none');
            });
        });
    }

    // Account Page Tabs
    const accountTabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    if (accountTabs) {
        accountTabs.forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                const target = this.getAttribute('data-bs-target');
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('show', 'active');
                });
                document.querySelector(target).classList.add('show', 'active');

                accountTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
});