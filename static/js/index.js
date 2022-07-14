function post_detail(id){

    window.location.href=`/detail/${id}`
}


function select_type(option) {
    document.querySelector('.selected').textContent = option.textContent
    document.querySelector('#selected').value = $(option).attr('value')

    let type = document.querySelector('#selected').value
    let check = document.querySelector('#viewOnlyMyPost').checked

    alert(check)

    $.ajax({
        type: "POST",
        url: "/",
        data: {'type_give': type, 'check_give': check},
        success: function (response) {
            if (response['result'] == 'success') {
                re_posts()
            } else {
                // 로그인이 안되면 에러메시지를 띄웁니다.
                // alert(response['msg'])
            }
        }
    })
}

// function onClickOption(e) {
//     const selectedValue = e.currentTarget.innerHTML;
//     document.querySelector(".selected").innerHTML = selectedValue;
// }
//
// let optionList = document.querySelectorAll(".dropdown-item");
// for (let i = 0; i < optionList.length; i++) {
//     let option = optionList[i];
//     option.addEventListener("click", onClickOption);
// }

function re_posts() {
    $('#posts').load(location.href+' #posts');
}