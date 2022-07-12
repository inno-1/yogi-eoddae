function posting() {
    let title = $('#title').val()
    let content = $('#content').val()
    let location = $('#location').val()

    let file = $('#file')[0].files[0]
    let form_data = new FormData()

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

    if(file) {
        form_data.append("file_give", file);
    } else {
        form_data.append("file_give", null);
    }

    form_data.append("title_give", title)
    form_data.append("content_give", content)
    form_data.append("location_give", location)

    $.ajax({
        type: "POST",
        url: "/api/post",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            alert(response["msg"])
            window.location.href = '/'
        }
    })
}

$(document).ready(function () {
    $('#file').on('change', function (e) {
        if(this.files[0]) {
            $('#file-text').val(this.files[0].name);
        } else {
            $('#file-text').val("");
        }

    })
})