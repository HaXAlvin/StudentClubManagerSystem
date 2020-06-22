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
      <div>
       <P>借用設備&nbsp{device_name} {device_count}{device_unit}</P>
      </div>
      <div class="row annousement-context row text-padding">
        <p>借用原因&nbsp{reason}</p>
      </div>
      <div class="row text-padding text-padding">
        <p>日期&nbsp{start_date}-{end_date}</p>
      </div>
      <section>
        <div class="center-content">
          <div class="center-content-inner">
            <div class="content-section content-section-margin">
              <div class="content-section-grid clearfix">
                <a onclick="send_id({bd_id})" href="#" class="df_check button nav-link">
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
    url: "/Audit_borrowed_data",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    headers:{
      'X-CSRF-TOKEN': readCookie('csrf_access_token')
    },
    success: function (res) {
      console.log(res);
      if (res === null) {
        $('#container').append("<h1>沒有人要借設備</h1>");
        return;
      }
      let i;
      var newcont = container;
      for (i = 0; i < res["len"]; i++) {
        newcont = newcont.replace('{data_'+ i%2 +'}',data);
        newcont = newcont.replace('{department}',res['department'][i]);
        newcont = newcont.replace('{name}',res['name'][i]);
        newcont = newcont.replace('{reason}',res['reason'][i]);
        newcont = newcont.replace('{start_date}',res['start_date'][i]);
        newcont = newcont.replace('{end_date}',res['end_date'][i]);
        newcont = newcont.replace('{device_name}',res['device_name'][i]);
        newcont = newcont.replace('{device_count}',res['device_count'][i]);
        newcont = newcont.replace('{device_unit}',res['device_unit'][i]);
        newcont = newcont.replace('{bd_id}',res['bd_id'][i]);
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
function send_id(id) {
  $.ajax({
    type: "POST",
    url: '/Audit_borrowed_Accept',
    data: JSON.stringify({'borrow_device_id': id}), //post form
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    headers:{
      'X-CSRF-TOKEN': readCookie('csrf_access_token')
    },
    success: function (res) { //連到伺服器
      Swal.fire({
          icon: 'success',
          title: "已審核",
          text: "讚讚?",
          timer: 3000
      }).then((result) => {
          location.reload();
      })
    },
    error: function (res) {
      console.log(res);
      Swal.fire({
          icon: 'error',
          title: "有東西壞惹",
          text: "稍後再試一次"
      });
    }
  });
  return false;
};
function readCookie(name) {
   var nameEQ = name + "=";
   var ca = document.cookie.split(';');
   for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
   }
   return null;
};