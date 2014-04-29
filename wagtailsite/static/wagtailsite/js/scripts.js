
$( document ).ready(function() {
  $(".post-header").click(function () {

    
      if ($(this).next().css('display') == 'none') {
          $(".post-body").css('display', 'none');
          $(this).next().css('display', 'block');
          $(".post-header").removeClass('post-header__active');
          $(this).addClass('post-header__active');
      } else {
          $(this).next().css('display', 'none');
          $(this).removeClass('post-header__active');
      }
      
      
//      if ($(this).hasClass('blurb-big')) {
//        $(".blurb").removeClass('blurb-big');
//      } else {
//        $(".blurb").removeClass('blurb-big');
//	   $(this).addClass('blurb-big');
//      }
      
//      $(this).next().css('display','block');
      
      /* if ($(this).next().css('display') == 'none') {
          $(".blogpost-content").css('display', 'none');
          $(this).next().css('display', 'block');
      } else {
          $(this).next().css('display', 'none');
      } */
      
    });
    
     $("#hamburger").click(function () {
    if ($('#mobilenav').css('display') == 'none') {
          $("#mobilenav").css('display', 'block');
      } else {
          $('#mobilenav').css('display', 'none');
      }
    });
    
//    $("#hamburger").click(function () {
//    if ($('#mobilenav').css('margin-top') == '-200px') {
//          $("#mobilenav").css('margin-top', '0');
//      } else {
//          $('#mobilenav').css('margin-top', '-200px');
//      }
//    });
    
});