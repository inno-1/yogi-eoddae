function post_detail(id){

    window.location.href=`/detail/${id}`
}

$(document).ready(function () {
    // [양명규] 메인페이지 등장모션 효과
    $('.intro_wrap').addClass('show');

    setTimeout(function () {
        $('.intro_wrap').addClass('hide');
    }, 2000);
})

function mypost(){
    // [안웅기] query string으로 게시물 정렬을 위한 query string 작업
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

    // [양명규] - 내가 쓴 글 스위치의 css transition-duration : 0.15s 후에 자연스럽게 주소 이동
    setTimeout(function () {
        window.location.href = '/?' + urlParams.toString();
    }, 150);
}

function post_sort(order){
    // [안웅기] query string으로 게시물 정렬을 위한 query string 작업
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