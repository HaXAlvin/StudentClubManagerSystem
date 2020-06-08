var bodyClass = $(".auto-hide-header"),
  lastScrollY = 0;

$(document).ready(function () {
  bodyClass.addClass("hideUp");
  let anno = `
    <div class="row">
      <div class="col-2" style="text-align: center;">
        <img
          src="data:image/png;base64,{src}"
          alt="{alt}"
          style="width: 70px;"
        />
      </div>
      <div class="col-sm-10">
        <div class="row">
          <h4>{title}</h4>

        </div>
        <div class="row annousement-context">
          <p>{content}</p>
        </div>
        <div class="row time-height">
          <div class="col-sm-4"></div>
          <div class="col-sm-4 down-line">
            <p>日期 &nbsp {date}</p>
          </div>
          <div class="col-sm-4">
            <p class="click-percent">
              點擊率 &nbsp {view}
            </p>
          </div>
        </div>
      </div>
    </div>
    <hr class="gradient" />`;
  $.ajax({
    type: "POST",
    url: "/announcement_data",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function (res) {
      if (res === null) {
        return;
      }
      let i;
      for (i = 0; i < res["len"]; i++) {
        let newanno = anno;
        newanno = newanno.replace("{src}", res["src"][i]);
        newanno = newanno.replace("{alt}", res["alt"][i]);
        newanno = newanno.replace("{title}", res["title"][i]);
        newanno = newanno.replace("{content}", res["content"][i]);
        newanno = newanno.replace(/\\n/g,"");
        newanno = newanno.replace("{date}", res["date"][i]);
        newanno = newanno.replace("{view}", res["view"][i]);
        $("#annos").append(newanno);
      }
    },
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
