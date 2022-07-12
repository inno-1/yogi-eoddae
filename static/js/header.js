function logout(){
    if($.removeCookie('mytoken')){

        alert('로그아웃!')
        window.location.reload()
    }
    console.log($.cookie('mytoken'))
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
