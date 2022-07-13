function recommend(id){

    $.ajax({
        type: "POST",
        url: "/api/post-recommend",
        data: {id_give: id},
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

function review_posting(id){

    let comment = $('#reviewTxtArea').val();
    if(comment == ''){
        alert('빈칸입니다.');
        return;
    }
    $.ajax({
        type: "POST",
        url: "/api/review",
        data: {comment_give: comment, id_give: id},
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
function review_delete(id){
    console.log(id)
    $.ajax({
        type: "DELETE",
        url: "/api/review",
        data: {id_give: id},
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
function review_edit_button(id){
    let review_id = '#review-' + id;
    let review_edit_id = '#review-edit-' + id;
    let review_edit_end_button = '#review-edit-end-button-' + id;
    let review_edit_cancel_button = '#review-edit-cancel-button-' + id;
    let review_edit_button = '#review-edit-button-' + id;
    let review_delete_button = '#review-delete-button-' + id;

    $(review_id).hide();
    $(review_edit_button).hide();
    $(review_delete_button).hide();
    $(review_edit_id).show();
    $(review_edit_end_button).show();
    $(review_edit_cancel_button).show();

}

function review_edit_cancel(id){
    let review_id = '#review-' + id;
    let review_edit_id = '#review-edit-' + id;
    let review_edit_end_button = '#review-edit-end-button-' + id;
    let review_edit_cancel_button = '#review-edit-cancel-button-' + id;
    let review_edit_button = '#review-edit-button-' + id;
    let review_delete_button = '#review-delete-button-' + id;

    $(review_id).show();
    $(review_edit_button).show();
    $(review_delete_button).show();
    $(review_edit_id).hide();
    $(review_edit_end_button).hide();
    $(review_edit_cancel_button).hide();

}

function review_edit(id){
    let edit_comment = '#reviewTxtArea-' + id;
    let comment = $(edit_comment).val()
    $.ajax({
        type: "PUT",
        url: "/api/review",
        data: {id_give: id, comment_give: comment},
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

function post_delete(id){
    console.log(id)
    $.ajax({
        type: "DELETE",
        url: "/api/post",
        data: {id_give: id},
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
