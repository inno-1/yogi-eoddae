function valid_check(title, location, content) {

    if(title === '') {
        alert('제목을 입력해주세요.');
        $('#title').focus();
        return false;
    }

    if(location === '') {
        alert('주소를 입력해주세요.');
        $('#location').focus();
        return false;
    }

    if(content === '') {
        alert('내용을 입력해주세요.');
        $('#content').focus();
        return false;
    }
}

function posting() {
    let title = $('#title').val();
    let content = $('#content').val();
    let location = $('#location').val();

    let file = $('#file')[0].files[0];
    let form_data = new FormData();

    valid_check(title,location,content);

    if(file) {
        form_data.append("file_give", file);
    } else {
        form_data.append("file_give", null);
    }

    form_data.append("title_give", title);
    form_data.append("content_give", content);
    form_data.append("location_give", location);

    $.ajax({
        type: "POST",
        url: "/api/post",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            if(response['result'] === 'success') {
                alert(response["msg"]);
                window.location.href = '/'
            } else {
                alert(response["msg"]);
            }
        }
    })
}

function post_edit(id){
    let title = $('#title').val();
    let content = $('#content').val();
    let location = $('#location').val();

    let file = $('#file')[0].files[0];
    let form_data = new FormData();

    valid_check(title,location,content);

    if(file) {
        form_data.append("file_give", file);
    } else {
        if($('#file_tmp').val() === "") {
            form_data.append("file_give", "");
            form_data.append("file_name_give", "");
        }
        else {
            form_data.append("file_give", $('#file_tmp').val());
            form_data.append("file_name_give", $('#file-text').val());
        }
    }

    form_data.append("id_give", id);
    form_data.append("title_give", title);
    form_data.append("content_give", content);
    form_data.append("location_give", location);

    $.ajax({
        type: "PUT",
        url: "/api/post",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            if (response['result'] == 'success') {
                window.location.href = `/detail/${id}`;
            } else {
                // 로그인이 안되면 에러메시지를 띄웁니다.
                alert(response['msg'])
            }
        }
    })
}

$(document).ready(function () {
    $('#file').on('change', function (e) {
        if(this.files[0]) {
            $('#file-text').val(this.files[0].name);
            const preview = document.querySelector('#preview');
            preview.src = URL.createObjectURL(this.files[0])
        } else {
            $('#file-text').val("");
        }
    })

    $('#file_delete_btn').on('click', function () {
        $('#file').val("");
        $('#file_tmp').val("")
        $('#file-text').val("");
        const preview = document.querySelector('#preview');
        preview.src = "https://yogi-eoddae-bucket.s3.ap-northeast-2.amazonaws.com/No_Image.jpg"
    })
})