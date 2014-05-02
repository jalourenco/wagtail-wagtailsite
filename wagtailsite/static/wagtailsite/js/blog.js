(function(){
    var cache = {};
    var initialUrl = location.href;
    var initialTitle = document.title;

    History.Adapter.bind(window, 'statechange', function(){ // Note: We are using statechange instead of popstate

        var state = History.getState(); // Note: We are using History.getState() instead of event.state

        var isIndexPage = new RegExp(blogIndexPageUrl + '$');

        // if there was a full reload after and the history api had been used then
        // we might need to do a full reload again when the back button is pressed
        if(!$('.post a[href="' + location.pathname + '"]').length){
            if(!(location.pathname.match(isIndexPage) && initialUrl.match(isIndexPage))){
                window.location.href = state.url;
                return;
            }
        }

        // going back to the index page, the posts are already hidden
        if(initialUrl == state.url){
            hideBlogPosts();
            return;
        }else{
            showBlogPost();
        }

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
        $('.post-body-and-footer:visible').slideUp(300, function(){
            $('.post').removeClass('post-selected-solid-bg');
        });
    }

    function showBlogPost(){
        var $anchor = $('a[href="' + location.pathname + '"]');

        $('body').scrollTop($('body').scrollTop() - $('.post-body-and-footer:visible').outerHeight());
        $('.post').removeClass('post-selected post-selected-solid-bg');
        $('.post-body-and-footer').hide();

        $anchor.velocity("scroll", {offset: -60, duration: 500, easing: 'swing'});

        $anchor.closest('.post').addClass('post-selected-solid-bg post-selected');

        $anchor
            .closest('.post')
            .find('.post-body-and-footer')
            .slideDown(500,  function(){
            });
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