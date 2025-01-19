/*
    JS for listing page (templates/profile.html)
    * - Handles deactivating and reactivating users
*/

import confirmModal from './confirmModal.js';
import { deactivate as deactivateUser, reactivate as reactivateUser } from './activationFunctions.js';


const deactivate_button = document.getElementById('deactivate-user');
if (deactivate_button) {
    deactivate_button.addEventListener('click', function() {
        confirmModal('Deactivate User', 'Are you sure you want to deactivate this user?\nThis will also deactivate all their listings', "users", deactivateUser);
    });
}

const reactivate_button = document.getElementById('reactivate-user');
if (reactivate_button) {
    reactivate_button.addEventListener('click', function() {
        confirmModal('Reactivate User', 'Are you sure you want to reactivate this user?\nThis will not reactivate their listings', "users",reactivateUser);
    });
}
