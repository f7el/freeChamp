function validateEmailFormat(email)
{
    var pattern = /^[a-zA-Z09+&*-]+(?:\.[a-zA-Z0-9_+&*-]+)*@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,7}$/;
	var re = new RegExp(pattern);
	return re.test(email);
}

function isEmpty(input)
{
	return input == ""
}