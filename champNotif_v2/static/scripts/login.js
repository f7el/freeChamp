$(document).ready(function(){
$(".error").hide();
 $.getScript("/static/scripts/validate.js", function(){
$("#myform").submit(function(e){
    e.preventDefault();
    var email = $("#email").val();
    var pw = $("#pw").val();
    if (isEmpty(email)){
           $("#emailBlank").show();
           error = true;
    }else if (!validateEmailFormat(email)){
                $("#emailFormat").show();
                error = true;
            }

    var gResponse = $("#g-recaptcha-response").val();
    $.ajax({
      type: "POST",
      url: "/login",
      data: { varEmail: email, varPassword: pw, varGresponse: gResponse},
      success: function(data, textStatus, jqXHR)
      {
          window.location = '/members';
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
            grecaptcha.reset();
      },
        });//ajax call
    });//submit
    });//import validate
});//doc rdy