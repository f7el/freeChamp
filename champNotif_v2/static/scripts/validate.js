function validateEmailFormat(email)
{
    var pattern = /^[a-zA-Z0-9+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$/;
	var re = new RegExp(pattern);
	return re.test(email);
}

//4 to 8 character password requiring numbers and both lowercase and uppercase letters
function validatePassword(password)
{
    var pattern = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{4,8}$/;
    var re = new RegExp(pattern);
    return re.test(password);
}

function isEmpty(input)
{
	return input == ""
}