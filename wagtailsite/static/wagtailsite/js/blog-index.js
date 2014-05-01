(function(){
    var cache = {};
    var initialUrl = location.href;
    var initialTitle = document.title;

    History.Adapter.bind(window, 'statechange', function(){ // Note: We are using statechange instead of popstate

        var state = History.getState(); // Note: We are using History.getState() instead of event.state

        hideBlogPosts();
        if(initialUrl == state.url){
            return;
        }

        showBlogPost();

        // var contents = cache[state.url];
        //
        // if(contents){
        //     showBlogPost(contents);
        // }else{
        //     $.ajax({
        //         // use different url for ajax in order to avoid the browser caching the ajax response,
        //         // and displaying it instead of the real page
        //         url: state.url + '?_ajax=1',
        //         success: function(data, status, xhr){
        //             var url = this.url.replace('?_ajax=1', '');
        //             cache[url] = data;
        //             showBlogPost(data);
        //         },
        //         complete:function(){
        //         }
        //     });
        // }
    });

    function hideBlogPosts(){
        $('.post').removeClass('post-selected');

        $('.post-body-and-footer').slideUp('fast', function(){});
    }

    function showBlogPost(){
        var $anchor = $('a[href="' + location.pathname + '"]');

        $anchor.closest('.post').addClass('post-selected');

        $anchor
            .closest('.post')
            .find('.post-body-and-footer')
            .slideDown('slow');
    }

    $(function(){
        $('a.post-header-anchor').on('click', function(e){
            // go back to index page if clicked on an already opened post
            if($(this).closest('.post').hasClass('post-selected')){
                History.pushState({}, initialTitle, initialUrl);
            }else{
                History.pushState({}, $(this).text(), $(this).attr('href'));
            }
            return false;
        });
    });

}());