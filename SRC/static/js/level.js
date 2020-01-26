//level.js

function choose_level(new_level)
{
	if (new_level == "easy")
	{
		document.getElementById("medium").removeAttribute("style");
		document.getElementById("hard").removeAttribute("style");
	}
	if (new_level == "medium")
	{
		document.getElementById("hard").removeAttribute("style");
		document.getElementById("medium").style.boxShadow = "0 2px 7px 0 rgb(18, 19, 19)";
	}
	if (new_level == "hard")
	{
		document.getElementById("medium").style.boxShadow = "0 2px 7px 0 rgb(18, 19, 19)";
		document.getElementById("hard").style.boxShadow = "0 2px 7px 0 rgb(18, 19, 19)";
	}
	current_level = new_level;
	var xhttp = new XMLHttpRequest();
	xhttp.open('POST', level_url);
	xhttp.send(current_level);
}

	function set_hover()
	{
		document.getElementById('medium').style.boxShadow = "0 2px 7px 0 rgb(18, 19, 19)";
	}
	function unset_hover()
	{
		if (current_level == "easy")
		{
			document.getElementById('medium').removeAttribute("style");
		}
	}

