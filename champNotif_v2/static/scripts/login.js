$(document).ready(function(){
    $('#error').hide();
    $("#submit").click(function(){
        var email = $("#email").val();
  		if (email == "") {
        $("#error").show();
        return false;
      }
      var pw = $("#pw").val();
      if(pw == ""){
        $("#error").show();
        return false;
      }

      var formData = {varEmail: email, varPw: pw};
      //alert (dataString);return false;
      $.ajax({
        type: "POST",
        url: "/checkLogin.py",
        data: formData,
        success: function(data) {

        }
    });
  return false;


    });//click function
});//doc rdy

