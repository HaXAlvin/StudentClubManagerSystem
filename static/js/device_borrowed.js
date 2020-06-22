$(document).ready(function () {
    var devices = [];
    $.ajax({
        type: "POST",
        url: "/device_borrowed_data",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        headers:{
            'X-CSRF-TOKEN': readCookie('csrf_access_token')
        },
        success: function (res) {
            console.log(res);
            for (var i in res) {
                devices.push(res[i]);
                $("#device-name-select").append('<option value="'+res[i]['id']+'">'+res[i]['name']+'</option>');
            }
            for (i=1;i<=devices[0]['count'];i++) {
                console.log(123);
                $('#device-count-select').append('<option value="'+i+'">'+i+'</option>');
            }
            console.log(devices);
        },
    });
    $("#device-name-select").change(function () {
        $('#device-count-select').html('');
        var val = $(this).val();
        for (var i in devices){
            if (val == devices[i]['id']){
                for (j=1;j<=devices[i]['count'];j++) {
                    $('#device-count-select').append('<option value="'+j+'">'+j+'</option>');
                }
                break;
            }
        }
    });
    $('#btn_borrow').click(function() {
        let start_date = $('#start-date').val();
        let end_date = $('#end-date').val();
        let device = $('#device-name-select :selected').val();
        let count = $("#device-count-select :selected").val();
        let phone = $('#input_phone').val();
        let reason = $('#input_reason').val();
        let account = $('#input_account').val();
        console.log(count);
        jQuery.ajax({ //post form資料 抓取json檔案
            type:"POST",
            url: '/send_borrow',
            headers:{'X-CSRF-TOKEN': readCookie('csrf_access_token')},
          data:JSON.stringify({
              'start_date':start_date,
              'reason':reason,
              'end_date':end_date,
              'device':device,
              'count':count,
              'account':account,
              'phone':phone,
          }), //post form
          contentType: "application/json; charset=utf-8",
          dataType: "json",
          success: function(res) { //連到伺服器
            console.log(res);
            Swal.fire({
              icon: 'success',
              title: "設備借用申請已送出",
              text: "社團將在三日內審核，請至信箱查收！"
             });
          },
          error: function (res) {
            console.log(res);
            Swal.fire({
              icon: 'error',
              title: "你是奇丁嗎？",
              text: "不，我是喜瑞爾斯。請稍後再試一次。"
            });
          }
        });
    });
});
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