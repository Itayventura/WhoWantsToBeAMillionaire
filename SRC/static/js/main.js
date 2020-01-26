
document.addEventListener('DOMContentLoaded',start_clock, false);


function start_clock()
{
    t = window.setInterval(check_clock, 1000);
    
    function check_clock()
    {
        if (time_length == 0)
        {
	        clearInterval(t)
            return end_game("Game over!");
        }
        var str = "";
        str += time_length;
        document.getElementById("timer").innerHTML = str.padStart(2, '0');
        time_length--;
    }
}


function send_answer(answer){
    if (clicked)
    {
	return;
    }
    clicked = true;
    var xhttp = new XMLHttpRequest();
    var url = answer_url;
    current_answer = answer;
    document.getElementById(current_answer).style.boxShadow = "none";
    xhttp.onreadystatechange = handle_response;
    xhttp.open('POST', url, true);
    console.log(answer);
    xhttp.send(answer);
}

function handle_response()
{
    if (this.readyState == 4 && this.status == 200)
    {
        dict = JSON.parse(this.responseText);
        if (dict.correct == "false")
        {
            document.getElementById(current_answer).style.backgroundColor = "red";
            document.getElementById(current_answer.replace('answer', 'mirror')).style.backgroundColor = "red";
            document.getElementById(dict.answer.replace('answer', 'mirror')).style.backgroundColor = "green";
            setTimeout(end_game, 3, "Game over!");
            return;
        }
        document.getElementById(current_answer).style.backgroundColor = "green";
        document.getElementById(current_answer.replace('answer','mirror')).style.backgroundColor = "green";
        if (dict.win == "true")
        {
            return end_game("You Won!");
        }
        setTimeout(refresh_question, 300);
    }
}

function refresh_question()
{
    time_length = 30;
    var x = document.getElementsByClassName("answer");
    var i;
    for (i = 0; i < x.length; i++)
    {
        if (x[i].hasAttribute('style'))
        {
            x[i].removeAttribute("style");
        }
        var mirror = document.getElementById(x[i].id.replace('answer', 'mirror'));
        if (mirror.hasAttribute('style'))
        {
            mirror.removeAttribute('style');
        }
    }
    x = document.getElementsByClassName("number");
    for (i = 0; i < x.length; i++)
    {
        if (x[i].id > dict.number)
        {
            x[i].style.backgroundColor = 'brown';
        }
        else
        {
            x[i].style.backgroundColor = 'SandyBrown';
        }
    }
    document.getElementById("question").innerHTML = dict.question;
    document.getElementById("answer_a").innerHTML = "A. " + dict.answer_a;
    document.getElementById("answer_b").innerHTML = "B. " + dict.answer_b;
    document.getElementById("answer_c").innerHTML = "C. " + dict.answer_c;
    document.getElementById("answer_d").innerHTML = "D. " + dict.answer_d;
    document.getElementById("mirror_a").innerHTML = "A. " + dict.answer_a;
    document.getElementById("mirror_b").innerHTML = "B. " + dict.answer_b;
    document.getElementById("mirror_c").innerHTML = "C. " + dict.answer_c;
    document.getElementById("mirror_d").innerHTML = "D. " + dict.answer_d;
    clicked = false;
}


function end_game(message)
{
    console.log("game over:message");
    console.log(message);
    clearInterval(t);
    document.getElementById('game').style.display = 'none';
    document.getElementById('game-end-maessage').innerHTML = message;
    if (caller == 'game')
    {
        caller = 'game-over';
    }
    if (!menu_on && caller == 'game-over')
    {
        document.getElementById('game-over').style.display = 'block';
    }
}
