$(document).ready(function(){
    $(".error").hide();
    $.getScript("/static/scripts/validate.js", function(){
        $("#submit").click(function(){
            //returns false if no errors exist in form validation
            var error = false;
            $(".error").hide();

            var email=$("#email").val();
            if (isEmpty(email)) {
                $("#emailBlank").show();
                error = true;

              //returns true if email is properly formatted
            } else if (!validateEmailFormat(email)){
                $("#emailFormat").show();
                error = true;
            }

            var pw = $("#password").val();
            if (isEmpty(pw)) {
                $("#pwBlank").show();
                error = true;
            }
            else if (!validatePassword(pw)){
                $("#pwFormat").show();
                error=true;
            }


            var verifyPw = $("#password2").val();
            if (isEmpty(verifyPw)) {
                $("#pw2Blank").show();
                error = true;
            }

            if (pw != verifyPw) {
                error = true;
                $("#pwMismatch").show();
            }
            //if player is new
            if ($("[type=checkbox]").prop("checked") == true){
                var newPlayer = 1;
            } else {
                var newPlayer = 0;
            }
            if (error == false) {
                $.ajax({
                  type: "POST",
                  url: "/processRegister",
                  data: { varEmail: email, varPassword: pw, varNewPlayer: newPlayer}, 
                  success: function(data, textStatus, jqXHR)
                  {
                      alert("email verification sent");
                  },
                  error: function(jqXHR,textStatus, data)
                  {
                        var status = jqXHR.status;
                        if (status == "500"){
                            alert("server error");
                        }
                        else if (status == "401"){
                            alert("This email already exists.");
                        }

                  },
                });//ajax call
            }//end if
        });//submit
    });//load validate.js
});//doc rdy