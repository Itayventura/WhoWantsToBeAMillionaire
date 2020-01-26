//globals.js

//api urls
var answer_url;
var level_url;
var topics_url;
var new_url;

//state variables
var time_length = 30;
var current_answer;
var mode = 'regular';

//level.js, themes.js
var current_level = 'easy';
var current_theme = 'classic';
//menu.js
var menu_on = false;
var caller = "game";

//main.js
var clicked = false
var t;
var dict;

function set_urls(answers, level, topics, new_game)
{
    answer_url = answers;
    level_url = level;
    topics_url= topics;
    new_url = new_game;
}
