$(document).ready(function(){
    $("#myform").submit(function(e){
        e.preventDefault();
        var email = $("#email").val();
        sendVerification(email);

    });//end submit
});//end doc rdy
 function sendVerification(email){
        $.ajax({
            type:"GET",
            url: "/sendAnotherVerification",
            data: {varEmail: email},
            success: function(data){
                if (data == "OK"){
                    alert("verification email sent");
                }//end if
                else if (data == "not in users database")
                {
                    alert("Please perform initial registration");
                }
                else if (data == "user has surpassed the send limit")
                {
                    alert("email send limit reached")
                }

                else{
                    alert("Please use the initial registration form.")
                }//end else
            }//end success
        });//end ajax
}