window.onpageshow = function (event){
    // [안웅기] 로그인 후 원래화면으로 돌아갔을 때 헤더 값들이 변하지 않아 추가 리로드
    if(event.persisted || (window.performance && window.performance.navigation.type == 2)){
        window.location.reload();
    }
}
function logout(){
    
    if($.removeCookie('mytoken', {path: '/'})){
        window.location.reload()
    }
}

function check_login(){
    $.ajax({
        type: "GET",
        url: "/api/check",
        data: {},
        success: function (response) {
            if (response['result'] == 'success') {
                window.location.href = '/posting'
            } else {
                // 로그인이 안되면 에러메시지를 띄웁니다.
                alert(response['msg'])
            }
        }
    })

}
