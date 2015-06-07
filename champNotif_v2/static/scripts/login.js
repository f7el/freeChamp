$(document).ready(function(){
$(".error").hide();
$("#myform").submit(function(e){
    e.preventDefault();
    var email = $("#email").val();
    var pw = $("#pw").val();
    $.ajax({
      type: "POST",
      url: "/login",
      data: { varEmail: email, varPassword: pw},
      success: function(data, textStatus, jqXHR)
      {
          alert("email verification sent");


      },
      error: function(jqXHR, data,textStatus)
      {
            var status = jqXHR.status;
            if (status == "401"){
                $("#401").show();
            } else if (status == "403"){
                $("#403").show();
            }


      },
        });//ajax call
    });//submit
});//doc rdy