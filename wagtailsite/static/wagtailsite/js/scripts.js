
$(document).ready(function() {

    // WARNING: the addBindings function in jquery.colorbox.js has been modified to prevent redirecting to vimeo
    $('.youtube').each(function(){
        $(this).colorbox({
            iframe: true,
            width: 1280,
            height: 720,
            href: function(){
                var videoId = new RegExp('[\\?&]v=([^&#]*)').exec(this.href);
                if (videoId && videoId[1]) {
                    return 'http://youtube.com/embed/'+videoId[1]+'?rel=0&wmode=transparent';
                }
            }
        });
    });

});