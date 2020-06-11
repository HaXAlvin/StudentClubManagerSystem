var bodyClass = $(".auto-hide-header"),
  lastScrollY = 0;

function validateEmail($email) {
  var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,6})?$/;
  return ($email.length > 0 && emailReg.test($email));
}

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
    // console.log(password_new_one);
    if (!validateEmail(email)&&(psw_new_one!=psw_new_two||!psw_old||!psw_new_one||!psw_new_two||!email||!date||!account)){
      return;
    }
    console.log(email);
    console.log(psw_old);
    console.log(psw_new_two);
    console.log(psw_new_one);
    console.log(date);
    console.log(male);
    console.log(account);
    $.ajax({
      type:"POST",
      url: '/updateIntroduce',
      data:JSON.stringify({
        'email':email,
        'psw_old':psw_old,
        'psw_new':psw_new_one,
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
