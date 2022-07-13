function post_detail(id){

    window.location.href=`/detail/${id}`
}

$(document).ready(function () {
    $('.intro_wrap').addClass('show');

    setTimeout(function () {
        $('.intro_wrap').addClass('hide');
    }, 2000);
})