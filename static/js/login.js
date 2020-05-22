function login() {
  alert("歡迎進入 iOS Club");
  // if document.accpass.account
}
$(document).ready(function() {
    document.cookie = "access_token_cookie="
    $('#btn_login').click(function() {
        let account = $('#input_account').val();
        let password = $('#input_pwd').val();
        jQuery.ajax({ //post form資料 抓取json檔案
            type:"POST",
            url: '/loginAccount',
            data:JSON.stringify({'account':account,'password':password}), //post form
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(res) { //連到伺服器
                console.log(res['login']);
                if (res['login'] == true){
                    $(location). attr('href','/index');
                }
            }
        });
     });
});