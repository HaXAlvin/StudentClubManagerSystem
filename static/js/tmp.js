var bodyClass = $(".auto-hide-header"),
  lastScrollY = 0;

$(document).ready(function () {
  bodyClass.addClass("hideUp");
  // jQuery.ajax({ //post form資料 抓取json檔案
  //     type: "GET",
  //     url: '/',
  //     data: JSON.stringify({'account': account, 'password': password, 'next': next}), //post form
  //     contentType: "application/json; charset=utf-8",
  //     dataType: "json",
  //     success: function (res) { //連到伺服器
  //         console.log(res['login']);
  //         console.log(res['next']);
  //         if (res['login'] == true) {
  //             $(location).attr('href', res['next']);
  //         }
  //     }
  // });
  $.get("/account_check", function( data ) {
    console.log(data);
    if(!data.login) {
      $(".member_dropdown").hide();
    }
    if(!data.login||!data.manager){
      $(".manager_dropdown").hide();
    }
  }, "json" );
});

// var bodyClass = document.body.classList,
// lastScrollY = 0;
window.addEventListener("scroll", function () {
  var st = this.scrollY;
  // this.console.log(this.scrollY);
  // bodyClass.addClass("hideUp");
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
