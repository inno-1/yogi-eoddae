function logout(){
    $.removeCookie('mytoken');
    alert('로그아웃!')
    window.location.href='/login'
}

function login(){
    console.log('login')
    window.location.href='/login'
}

function signup(){
    console.log('signup')
    window.location.href='/register'

}