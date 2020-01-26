//themes.js
//current_theme - in global.js

function change_theme(new_theme) 
{
    var i, j;
    var elem_list = document.body.getElementsByTagName("*");
    for (i = 0; i < elem_list.length; i++)
    {
        elem_classes = elem_list[i].classList;
        for(j = 0; j < elem_classes.length; j++)
        {
            class_name = elem_classes.item(j);
            if (class_name.includes(current_theme))
            {
                elem_classes.remove(class_name);
                elem_classes.add(class_name.replace(current_theme, new_theme));
            }
        }
    }
    current_theme = new_theme;
}