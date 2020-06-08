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
    email = $('input[name="email"]').val()
    psw_old = $('input[name="password_old"]').val()
    psw_new_one = $('input[name="password_new_one"]').val()
    psw_new_two = $('input[name="password_new_two"]').val()
    date = $('input[name="date"]').val()
    // console.log(password_new_one)
    if (psw_new_one!=psw_new_two||!psw_old||!psw_new_one||!psw_new_two||!email||!date){
      return;
    }
    jQuery.ajax({ //post form資料 抓取json檔案
      type:"POST",
      url: '/enterIntroduce',
      data:JSON.stringify({'email':email,'psw_old':psw_old, 'psw_new':psw_new_one,'date':date,'male':male}),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(res) { //連到伺服器
        console.log(123);
      }
    });
    console.log(male);
    // $('#huey').prop("checked",true);
  });
  // $("input[name='password_new_one']").keyup(function(){
  //   updateError(checkSame());
  // });
  // $("input[name='password_new_two']").keyup(function(){
  //   updateError(checkSame());
  // });
});

// var bodyClass = document.body.classList,
//   lastScrollY = 0;
window.addEventListener("scroll", function () {
  var st = this.scrollY;
  //   this.console.log(this.scrollY);
  //bodyClass.addClass("hideUp");
  // 判斷是向上捲動，而且捲軸超過 200px
  if (st == 0) {
    this.console.log("logoUnHideUp");
    bodyClass.addClass("hideUp");
  } else {
    this.console.log("logoHideUp");
    if (st < lastScrollY) {
      this.console.log(1);
      bodyClass.removeClass("hideUp");
    } else {
      this.console.log(2);
      bodyClass.addClass("hideUp");
    }
  }
  lastScrollY = st;
});
