$(document).ready(function () {
  let container = `
    <div class="row justify-content-center">
      <div class="col-1"></div>
      {data_0}
      {data_1}
      <div class="col-1"></div>
    </div>
   `
  let data = `
    <div class="col-5">
      <hr class="gradiant" />
      <div class="row row text-padding">
        <h5>{department} {name}</h5>
      </div>
      <div class="row annousement-context row text-padding">
        <p>請假原因&nbsp{reason}</p>
      </div>
      <div class="row text-padding text-padding">
        <p>日期&nbsp{date}</p>
      </div>
      <section>
        <div class="center-content">
          <div class="center-content-inner">
            <div class="content-section content-section-margin">
              <div class="content-section-grid clearfix">
                <a href="#" class="button nav-link">
                  <div class="bottom"></div>
                  <div class="top">
                    <div class="label">好哇 &nbsp; 給你請</div>
                    <div class="button-border button-border-left"></div>
                    <div class="button-border button-border-top"></div>
                    <div class="button-border button-border-right"></div>
                    <div class="button-border button-border-bottom"></div>
                  </div>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  `
  $.ajax({
    type: "POST",
    url: "/Audit_DayOff_data",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function (res) {
      console.log(res);
      if (res === null) {
        return;
      }
      let i;
      var newcont = container;
      for (i = 0; i < res["len"]; i++) {
        newcont = newcont.replace('{data_'+ i%2 +'}',data);
        newcont = newcont.replace('{department}',res['department'][i]);
        newcont = newcont.replace('{name}',res['name'][i]);
        newcont = newcont.replace('{reason}',res['reason'][i]);
        newcont = newcont.replace('{date}',res['date'][i]);
        if(i == res['len']-1) {
          newcont = newcont.replace('{data_1}', "<div class='col-5'></div>");
          $('#container').append(newcont);
        } else if((i%2)){
          $('#container').append(newcont);
          newcont = container;
        }
      }
    },
  });
});