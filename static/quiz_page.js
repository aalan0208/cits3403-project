$(document).ready(function () {
    $('#account').click(function () {
        $('#sub_panel').toggleClass('d-none');
        $('#accountInfo').toggleClass('d-none');
    });

    $('#setting').click(function () {
        $('#setting_detail').toggleClass('d-none');
    });

    $('#setting_detail').click(function () {
        $('body').toggleClass('dark-background');
    });

    $('#logout').click(function () {
        $('#yesno').toggleClass('d-none');
        $('#setting_detail').addClass('d-none');
        $('#about_contact').addClass('d-none');
    });

    $('#no').click(function () {
        $('#yesno').toggleClass('d-none');
    })

    $('#yes').click(function () {
        // Perform logout here

        // Redirect to the login page
        window.location.href = 'Login.html';
    });

    $('#about').click(function () {
        $('#about_contact').toggleClass('d-none');
    });
});