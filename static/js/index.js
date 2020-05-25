// const acc = document.cookie.replace(/(?:(?:^|.*;\s*)csrf_access_token\s*\=\s*([^;]*).*$)|^.*$/, "$1");
// const ref = document.cookie.replace(/(?:(?:^|.*;\s*)csrf_refresh_token\s*\=\s*([^;]*).*$)|^.*$/, "$1");
// jQuery.ajax({ //post form資料 抓取json檔案
//     type:"POST",
//     url: '/refresh',
//     data:JSON.stringify({'csrf_access_token':acc,'csrf_refresh_token':ref}), //post form
//     contentType: "application/json; charset=utf-8",
//     dataType: "json",
//     beforeSend: function (xhr) {   //Include the bearer token in header
//         xhr.setRequestHeader("X-CSRF-TOKEN",acc);
//     },
//     success: function(res) { //連到伺服器
//         console.log(res);
//         // if (res['login'] == true){
//         //     $(location). attr('href','/index');
//         // }
//     },
//     failure: function () {
//         console.log(333333)
//     }
// });