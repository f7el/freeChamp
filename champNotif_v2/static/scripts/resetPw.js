$(document).ready(function(){
$(".error").hide();
var email = $("#email").val();
$.ajax({
  type: "GET",
  url: "/processResetPassword",
  data: { varEmail: email},
  success: function(data, textStatus, jqXHR)
  {
      alert("password reset request sent");
  },
  error: function(jqXHR, data,textStatus)
  {

      var status = jqXHR.status;
      if (jqXHR == "INTERNAL SERVER ERROR"){
      alert("server error");
                        }
  },
        });//ajax call
});//doc rdy