var socket = io();

function redirect() {
    console.log('redirecting...');
    window.location.href = '/maps';
}

(function($) {
    "use strict";

    $('#send_post').submit(function(e) {
        e.preventDefault();
        console.log("sendingggggg");
        var message = $('#message_content').val();
        $.post('/newPost', {
            message: message,
        }, function(data, success) {
            console.log("I'm emitting")
            socket.emit('newsfeed', data);
            // $('.cancelBtn').click();
            // $('.close').click();
            // $('#newMessage').click();
            // redirect();
            window.location.reload();
        });
    })
})($);


// Get the modal
var modal = document.getElementById('submitModal');
var errmodal = document.getElementById('errModal');
var errmodalmsg = document.getElementById('errModalmsg');
// Get the button that opens the modal
var btn = document.getElementById("submitnewpost");
// Get the elements that closes the modal
var span = document.getElementsByClassName("cancelBtn")[0];
var okBtn = document.getElementById("okBtn");
var okBtn2 = document.getElementById("okBtn2");
// When the user clicks on the button, open the modal
btn.onclick = function() {
        console.log("helloooo");
        var message = $('#message_content').val();

        if (message != "") {
            $('#postMessage').append("'" + message + "'?");
            modal.style.display = "block";
        } else {
            errmodalmsg.style.display = "block";
        }
    }
    // When the user clicks on <span> (x), close the modal
span.onclick = function() {
    $('#postMessage').text("Are you sure you want to post: ");
    modal.style.display = "none";
}
okBtn.onclick = function() {
    console.log("ok button pressed");
    errmodal.style.display = "none";
}
okBtn2.onclick = function() {
    console.log("ok button pressed");
    errmodalmsg.style.display = "none";
}