$(document).ready(function(){
$(".error").hide();
$("#myform").submit(function(e){
    e.preventDefault();
    var email = $("#email").val();
    var pw = $("#pw").val();
    var gResponse = $("#g-recaptcha-response").val();
    $.ajax({
      type: "POST",
      url: "/login",
      data: { varEmail: email, varPassword: pw, varGresponse: gResponse},
      success: function(data, textStatus, jqXHR)
      {
          $.getScript("/static/scripts/server.js", function(){
          window.location = devServer.concat('/members'); });


      },
      error: function(jqXHR, data,textStatus)
      {

            var status = jqXHR.status;
            if (jqXHR.responseText == "Invalid captcha"){
                $("#captcha").show();
            }
            else if(status == "401"){
                $("#401").show();
            }
            else if (status == "403"){
                $("#403").show();
            }
            $("#pw").val('');
      },
        });//ajax call
    });//submit
});//doc rdy