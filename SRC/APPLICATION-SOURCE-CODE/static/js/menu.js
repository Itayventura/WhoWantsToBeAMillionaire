
function toggle_menu()
{
	if (menu_on)
	{
		document.getElementById("menu").style.display = "none";
		document.getElementById(caller).style.display = "block";
		menu_on = false;
		return;
	}
	var containers = document.getElementsByClassName("content-container");
	var i;
	for (i = 0; i < containers.length; i++)
	{
		containers[i].style.display = "none";
	}
	document.getElementById("menu").style.display = "block";
	menu_on = true;
}

function change_page(target)
{
	caller = target;
	toggle_menu();
}

function new_game()
{

	var xhttp = new XMLHttpRequest();
	var url = new_url;
	
	xhttp.onreadystatechange = handle_new;
	xhttp.open('POST', url, true);
	xhttp.send("");

	time_length = 30;
	clearInterval(t)
	start_clock();

	caller = 'game';
	if (menu_on)
	{
	    toggle_menu();
	}
	else
	{
	    document.getElementById("game").style.display = "block";
            document.getElementById("game-over").style.display = "none";
	}
}

function handle_new()
{
    if (this.readyState == 4 && this.status == 200)
    {
		dict = JSON.parse(this.responseText);
		document.getElementById('lives').innerHTML = '<strong>'+dict.lives+'</strong>';
	//in main.js
        setTimeout(refresh_question, 3);
    }
}
