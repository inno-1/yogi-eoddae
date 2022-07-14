function post_detail(id){

    window.location.href=`/detail/${id}`
}

$(document).ready(function () {
    $('.intro_wrap').addClass('show');

    setTimeout(function () {
        $('.intro_wrap').addClass('hide');
    }, 2000);
})

function mypost(){
    let cur_href = document.location.search;
    const urlParams = new URLSearchParams(cur_href);
    let check = $('#viewOnlyMyPost').is(":checked");
    if(urlParams.has('mypost')){
        if(check){
            urlParams.set('mypost', '1');
        }else{
            urlParams.set('mypost', '0');
        }
    }else{
        if(check){
            urlParams.append('mypost', '1');
        }else{
            urlParams.append('mypost', '0');
        }
    }
    window.location.href = '/?' + urlParams.toString();
}

function post_sort(order){
    let cur_href = document.location.search;
    const urlParams = new URLSearchParams(cur_href);
    if(urlParams.has('orderby')){
        if(order=='new'){
            urlParams.set('orderby', 'new');
        }else if(order=='recommend'){
            urlParams.set('orderby', 'recommend');
        }else if(order=='view'){
            urlParams.set('orderby', 'view');
        }
    }else{
        if(order=='new'){
            urlParams.append('orderby', 'new');
        }else if(order=='recommend'){
            urlParams.append('orderby', 'recommend');
        }else if(order=='view'){
            urlParams.append('orderby', 'view');
        }
    }
    window.location.href = '/?' + urlParams.toString();
}