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


      console.log("test");
      //alert (dataString);return false;
      $.ajax({
        type: "POST",
        url: "/login",
        data:  {varEmail: email, varPassword: pw},
        success: function(data) {
        alert("success");

        }
    });//ajax call



    });//click function
});//doc rdy

