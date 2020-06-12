var bodyClass = $(".auto-hide-header"),
  lastScrollY = 0;

$(document).ready(function () {
  bodyClass.addClass("hideUp");
  var male = 1;
  $('#huey').click(function () {
    male = 1;
  });
  $('#dewey').click(function () {
    male = 0;
  });
  $('#btn_send').click(function () {
    email = $('input[name="email"]').val();
    psw_old = $('input[name="password_old"]').val();
    psw_new_one = $('input[name="password_new_one"]').val();
    psw_new_two = $('input[name="password_new_two"]').val();
    date = $('input[name="date"]').val();
    account = $('input[name="account"]').val();
    if (!psw_old||!psw_new_one||!psw_new_two||!email||!date){
      Swal.fire({
            icon: 'error',
            title: "你是奇丁嗎？",
            text: "空著幹嘛啦，討厭>3<"
      });
      return;
    }
    $.ajax({
      type:"POST",
      url: '/updateIntroduce',
      data:JSON.stringify({
        'email':email,
        'psw_old':psw_old,
        'psw_new_one':psw_new_one,
        'psw_new_two':psw_new_two,
        'date':date,
        'male':male,
        'account':account
      }),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(res) {
        console.log(res);
        if(res['login'] == true && res['update'] == true){
          $(location). attr('href','/login');
        }
      },
      error: function (res) {
        msg = res.responseJSON.msg;
        var text = "你確定你記得你的密碼嗎？"
        if (msg == "email"){
          text = "Email怪怪的餒？"
        }else if(msg == "password"){
          text = "打兩次很難ㄇ"
        }
        Swal.fire({
            icon: 'error',
            title: "你是奇丁嗎？",
            text: text
        });
      }
    });
  });
});

// var bodyClass = document.body.classList,
//   lastScrollY = 0;
window.addEventListener("scroll", function () {
  var st = this.scrollY;
  //   this.console.log(this.scrollY);
  //bodyClass.addClass("hideUp");
  // 判斷是向上捲動，而且捲軸超過 200px
  if (st == 0) {
    bodyClass.addClass("hideUp");
  } else {
    if (st < lastScrollY) {
      bodyClass.removeClass("hideUp");
    } else {
      bodyClass.addClass("hideUp");
    }
  }
  lastScrollY = st;
});
