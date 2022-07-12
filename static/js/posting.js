function posting() {
    let title = $('#title').val()
    let content = $('#content').val()
    let location = $('#location').val()

    let file = $('#file')[0].files[0]
    let form_data = new FormData()

    form_data.append("file_give", file)
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