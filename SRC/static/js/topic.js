//topic.js

function choose_topic(el_id)
{
    if (document.getElementById(el_id).hasAttribute('style'))
    {
        document.getElementById(el_id).removeAttribute('style');
    }
    else
    {
        document.getElementById(el_id).style.boxShadow = "none";
        document.getElementById(el_id).style.backgroundColor = "rgb(107, 107, 192)";
    }
    
	var xhttp = new XMLHttpRequest();
	xhttp.open('POST', topics_url);
    xhttp.send(el_id + " " + "remove");
    xhttp.send(el_id + " " + "add");
}
function reset_topic()
{
    elements = document.getElementsByClassName("topic");
    var i;
    for(i = 0; i < elements.length; i++)
    {
        choose_topic(elements[i].id);
    }
}

