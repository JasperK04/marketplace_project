export function reactivate (type) {
    const id = window.location.pathname.split('/').pop();
    fetch(`/api/admin/${type}/${id}/reactivate`, {
        method: 'POST',
    })
    .then(response => {
        if (response.ok) {
            window.location.reload();
        } else {
            alert(`Failed to reactivate ${type}`);
        }
    });

}

export function deactivate(type) {
    const id = window.location.pathname.split('/').pop();
    fetch(`/api/admin/${type}/${id}/deactivate`, {
        method: 'POST',
    })
    .then(response => {
        if (response.ok) {
            window.location.reload();
        } else {
            alert(`Failed to deactivate ${type}`);
        }
    });
}
