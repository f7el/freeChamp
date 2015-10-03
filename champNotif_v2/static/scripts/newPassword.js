$(document).ready(function(){
$("#myform").submit(function(e){
    e.preventDefault();
$(".error").hide();
var password = $("#pw").val();
var password2 = $("#pw2").val();
//if the passwords match, make a call that updates the users password to the new value
if (password == password2 ){


$.ajax({
  type: "POST",
  url: "/updatePassword",
  data: { varPw: password},
  success: function(jqXHR, status, data)
  {
      alert("Password updated");
  },
  error: function(jqXHR, textStatus, error)
  {

      var status = jqXHR.status;
      if (status == "500"){
      alert("server error");
                        }
  },
        });//ajax call
        }//end if
        });//submit
});//doc rdy