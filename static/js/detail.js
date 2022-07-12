function review_posting(){

    let comment = $('#reviewTxtArea').val();
    if(comment == ''){
        alert('빈칸입니다.');
        return;
    }
    $.ajax({
        type: "POST",
        url: "/api/review",
        data: {comment_give: comment},
        success: function (response) {
            if (response['result'] == 'success') {
                window.location.reload();
            } else {
                // 로그인이 안되면 에러메시지를 띄웁니다.
                alert(response['msg'])
            }
        }
    })
}