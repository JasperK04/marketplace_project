export default function confirmModal(title, message, callback) {
    const modal = document.getElementById('confirm-modal');
    const confirm_button = document.getElementById('confirm-purchase');
    const cancel_button = document.getElementById('cancel-purchase');
    const close_button = document.getElementById('close-modal');
    const modal_title = document.getElementById('modal-title');
    const modal_message = document.getElementById('modal-message');

    modal_title.innerText = title;
    modal_message.innerText = message;

    confirm_button.addEventListener('click', function() {
        callback();
        modal.close();
    });

    cancel_button.addEventListener('click', function() {
        modal.close()
    });

    close_button.addEventListener('click', function() {
        modal.close()
    });

    modal.showModal();
}
