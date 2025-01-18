const deactivate_button = document.getElementById('deactivate-user');
if (deactivate_button) {
    deactivate_button.addEventListener('click', function() {
        const user_id = window.location.pathname.split('/').pop();
        fetch(`/api/admin/users/${user_id}/deactivate`, {
            method: 'POST',
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Failed to deactivate listing');
            }
        });
    });
}

const reactivate_button = document.getElementById('reactivate-user');
if (reactivate_button) {
    reactivate_button.addEventListener('click', function() {
        const user_id = window.location.pathname.split('/').pop();
        fetch(`/api/admin/users/${user_id}/reactivate`, {
            method: 'POST',
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Failed to reactivate listing');
            }
        });
    });
}
