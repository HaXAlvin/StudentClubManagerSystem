var bodyClass = $(".auto-hide-header"),
  lastScrollY = 0;
var navClass = $(".logo_nav");

$(document).ready(function () {
  navClass.removeClass("hideUp");
  bodyClass.addClass("hideUp");
  $.get(
    "/account_check",
    function (data) {
      console.log(data);
      if (!data.login) {
        $(".member_dropdown").hide();
      }
      if (!data.login || !data.manager) {
        $(".manager_dropdown").hide();
      }
    },
    "json"
  );
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
    navClass.removeClass("hideUp");
  } else {
    navClass.addClass("hideUp");
    if (st < lastScrollY) {
      bodyClass.removeClass("hideUp");
    } else {
      bodyClass.addClass("hideUp");
    }
  }
  lastScrollY = st;
});
// window.addEventListener("beforeunload", function (event) {
//   event.returnValue = "您即將離開此網頁";
//   //離開網頁之提示
// });
// window.onbeforeunload = function (event) {
//   event.returnValue = "您即將離開此網頁";
//   //離開網頁之提示
// };
