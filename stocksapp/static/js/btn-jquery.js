$(document).ready(function() {
	$( "#subtract" ).click(function() {
		("#count").val(10)
	});
	$('.add').click(function(){ 
		var count; 
		count = $(this).serialize(); 
		$.ajax( 
		{ 
		    type:"POST", 
		    url: "", 
		    data: count, 
		success: function( data ) 
		{ 
		    $( '#count' ).val(100);
				$( '.world' ).html('hellooooo');  } }) });
}); 