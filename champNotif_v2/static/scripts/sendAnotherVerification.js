$(document).ready(function(){
    function checkSendLimit(email){
        $.ajax({
            type:"POST",
            url: "/checkSendLimit.py",
            data= {varEmail: email},
            success: function(data){
                if (data == "True"){
                    return true;
                }//end if
                else{
                    return false;
                }//end else
            }//end success
        }
    }


    $('.error').hide();
     $("#submit").click(function(){
        var email=$("#email").val();
        if (email == "") {
            $("#invalidInput").show();
            return false;
        }

         var formData = {varEmail: email};
        $.ajax({
            type: "POST",
            url: "/verifyEmail.py",
            data: formData,
            success: function(data){
                #if the email is a valid format, check if they have exceeded their send limit
                if (data == "True"){
                    var notExceeded = checkSendLimit(email);

                    //if send limit has not been exceeded, send another verification token
                    if (notExceeded){

                    }//end if

                }
                else{
                    $("#invalidInput").show()
                }
              }

              if (

        });//end ajax
        return false;

     });//end submit

});//end doc rdy
