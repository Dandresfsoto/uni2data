createjs.Sound.registerSound({src:"/static/ogg/unconvinced.ogg", id:"sound"});


Push.Permission.request();

socket.onmessage = function (event) {
    var data = JSON.parse(event.data);

    if("notifications" in data){
        for(i = 0; i < data["notifications"].length; i++){
            var promise = Push.create(data["notifications"][i].title, {
                                body: data["notifications"][i].short_description,
                                icon: data["notifications"][i].icon_notification,
                                timeout: data["notifications"][i].timeout
                            });
            promise.then(function (notification) {
                createjs.Sound.play("sound");
            });

            if(window.location.pathname == "/notificaciones/"){
                $("#container-notificaciones").prepend('' +
                '<div class="infinite-item z-depth-1 animated bounceInLeft" id="notification_'+ data["notifications"][i].id_notification +'">' +
                    '<div class="icon-notification center">' +
                        '<i class="medium material-icons ' + data["notifications"][i].color +'">' + data["notifications"][i].icon + '</i>' +
                    '</div>' +
                    '<div class="body-notification">' +
                        '<a href="#" class="close-notification-link" id="'+ data["notifications"][i].id_notification +'">' +
                            '<i class="tiny material-icons right close-notification">close</i>' +
                        '</a>' +
                        '<p class="title-notification">' + data["notifications"][i].title +
                        '</p>' +
                        '<p>' + data["notifications"][i].body +
                        '</p>' +
                        '<p class="right-align time-ago-notification">' +
                            data["notifications"][i].date +
                        '</p>' +
                    '</div>' +
                '</div>');

                $("#container-initial-message").addClass("hide");
                notification_listener();
            }

        }
    }


    if("badges_count" in data){

        var notifications_count = data['badges_count']['notifications'];
        var messages_count = data['badges_count']['messages'];


        if(notifications_count + messages_count > 0){
            $("#notifications_header").removeClass('hide');
            $("#notifications_navbar").removeClass('hide');
        }
        else{
            $("#notifications_header").addClass('hide');
            $("#notifications_navbar").addClass('hide');
        }

        $("#notifications_header").text(notifications_count + messages_count);
        $("#notifications_navbar").text(notifications_count + messages_count);


        if(notifications_count > 0){
            $("#notifications_body").removeClass('hide');
        }
        else{
            $("#notifications_body").addClass('hide');
        }

        $("#notifications_body").text(notifications_count);


        if(messages_count > 0){
            $("#message_body").removeClass('hide');
        }
        else{
            $("#message_body").addClass('hide');
        }

        $("#message_body").text(messages_count);

    }
}