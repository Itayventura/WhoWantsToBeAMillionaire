window.onload = start_clock(30);

function start_clock(time_length)
{
    this.setInterval(check_clock, 1000);
    
    function check_clock()
    {
        if (time_length == 0)
        {
            return end_game("Game_over! Time is out!");
        }
        var str = "";
        str += time_length;
        document.getElementById("timer").innerHTML = str.padStart(2, '0');
        time_length--;
    }
}

var current_answer;

function send_answer(answer, url){
    var xhttp = new XMLHttpRequest();
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
        var dict = JSON.parse(this.responseText);
        if (dict.correct == "false")
        {
            document.getElementById(current_answer).style.backgroundColor = "red";
            setTimeout(end_game, 300, "Sorry! Game over!");
            setTimeout(refresh_question, 400);
            return;
        }
        document.getElementById(current_answer).style.backgroundColor = "green";
        if (dict.win == "true")
        {
            return end_game("Congradulations! you Won!");
        }
        setTimeout(start_clock, 500, 30);
        setTimeout(refresh_question, 490);
        function refresh_question()
        {
            document.getElementById(current_answer).style.boxShadow = "0 2px 7px 0 rgb(18, 19, 19)";
            document.getElementById(current_answer).style.backgroundColor = "rgb(87, 87, 182)";
            document.getElementById("question").innerHTML = dict.question;
            document.getElementById("answer_a").innerHTML = dict.answer_a;
            document.getElementById("answer_b").innerHTML = dict.answer_b;
            document.getElementById("answer_c").innerHTML = dict.answer_c;
            document.getElementById("answer_d").innerHTML = dict.answer_d;
        }
        //start_clock(30);
    }
}
function end_game(message)
{
    console.log("game over:message");
    console.log(message);
    //location.reload(true);
}
