window.onload = function() {
    var sec = 30;
    var str = "";
    var expired = false;
    this.setInterval(function () {
        if (expired === false){
            str = "";
            str += sec;
            document.getElementById("timer").innerHTML = str.padStart(2, '0')
            if (sec == 0)
            {
                expired = true;
            }
            sec--;
        }
    }, 1000);
}

function send_answer(answer, url){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = handle_response;
    xhttp.open('POST', url, true);
    xhttp.send(answer);
}

function handle_response()
{
    if (this.readyState == 4 && this.status == 200)
    {
        var dict = JSON.parse(this.responseText);
        if (dict.correct == "false")
        {
            return end_game("Sorry! Game over!");
        }
        if (dict.win == "true")
        {
            return end_game("Congradulations! you Won!");
        }
        document.getElementById("question").innerHTML = dict.question;
        document.getElementById("answer-a").innerHTML = dict.answer_1;
        document.getElementById("answer-b").innerHTML = dict.answer_2;
        document.getElementById("answer-c").innerHTML = dict.answer_3;
        document.getElementById("answer-d").innerHTML = dict.answer_4;
    }
}
