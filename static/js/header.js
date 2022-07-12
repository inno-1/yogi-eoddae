function logout(){
    $.removeCookie('mytoken');
    alert('로그아웃!')
    window.location.reload()
}

function check_login(){
    $.ajax({
        type: "GET",
        url: "/api/check",
        data: {},
        success: function (response) {
            if (response['result'] == 'success') {
                history.back(1)
            } else {
                // 로그인이 안되면 에러메시지를 띄웁니다.
                alert(response['msg'])
            }
        }
    })

}
