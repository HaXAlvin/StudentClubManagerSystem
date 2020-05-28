var bodyClass = $(".auto-hide-header"),
  lastScrollY = 0;

$(document).ready(function () {
  bodyClass.addClass("hideUp");
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
