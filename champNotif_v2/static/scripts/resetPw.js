$(document).ready(function(){
$("#myform").submit(function(e){
    e.preventDefault();
$(".error").hide();
var email = $("#email").val();
$.ajax({
  type: "GET",
  url: "/sendResetPassword",
  data: { varEmail: email},
  success: function(jqXHR, status, data)
  {
      alert("password reset request sent");
  },
  error: function(jqXHR, textStatus, error)
  {

      var status = jqXHR.status;
      if (status == "500"){
          alert("server error");
                        }
      else if(status == "403"){
          alert("daily send limit reached");
      }
  },
        });//ajax call
        });//submit
});//doc rdy