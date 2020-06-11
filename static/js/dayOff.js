var bodyClass = $(".auto-hide-header"),
  lastScrollY = 0;

$(document).ready(function () {
  bodyClass.addClass("hideUp");
  $('#btn_dayOff').click(function() {
    let date = $('#input_date').val();
    let reason = $('#input_reason').val();
    let types = $('#day-off').val();
    let account = $('#input_account').val()
    console.log(date);
    console.log(reason);
    console.log(types);
    jQuery.ajax({ //post form資料 抓取json檔案
      type:"POST",
      url: '/send_dayOff',
      data:JSON.stringify({'account':account,'date':date,'reason':reason,'types':types}), //post form
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function(res) { //連到伺服器
        console.log(res);
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
