$(document).ready(function(){

    //Manage click on Config Update
    $("input#config_autoupdt").click(function(){
        var data = {}
        data.config_autoupdate = $("input#config_autoupdt").prop("checked");
        $.ajax({
            type : "POST",
            //url : "{{ url_for('mod.load_ajax') }}",
            url : "/setConfig",
            async : 'false',
            contentType: 'application/json;charset=UTF-8',
            // Encode data as JSON.
            data: JSON.stringify(data),
            success: function(result){
                console.log(result);
                }
        });
    }
    );

});

function createSearchWindow(but_del_vis, sub_but_text) {
   var wind = document.getElementById('mw_search');
   var button_del = document.getElementById('but_del');
    if (wind.style.display === 'block') {
        wind.style.display = 'none';
    } else {
        wind.style.display = 'block';
    }
    if (but_del_vis == 'false') {
        input_url.readOnly = false;
        button_del.style.display = 'none';
    } else {
        button_del.style.display = 'inline';
        var input_url = document.getElementById('i_url');
        input_url.readOnly = true;
    }

   var button = document.getElementById('but_cre');
   button.setAttribute("value", sub_but_text);
}

//Function to update the result list
function createConfigWindow() {
    //get the config from server
    var config_json;
     $.ajax({
        type : "GET",
        async : "false",
        //url : "{{ url_for('mod.load_ajax') }}",
        url : "/getConfig",
        dataType: 'json',
        success: function(result, config_json) {
            console.log(result);
            config_json = result;
            //fill the  switch
            $("input#config_autoupdt").prop("checked", config_json.config_autoupdate);
        },
        error: function(jqXHR, exception) {
            window.alert('Error');
        }
    });

    var wind = document.getElementById('mw_config');
        if (wind.style.display === 'block') {
            wind.style.display = 'none';
        } else {
            wind.style.display = 'block';
        }
}


//Function to update the result list
function updateResults() {
    var updt_url = new URL(location.href + '/update');
    window.location.href = updt_url;
}

//Function to empty the result list
function emptyResults() {
    var delete_url = new URL(location.href + '/delete');
    window.location.href = delete_url;
}