$(function() {
    $( "#dates-slider" ).slider({
      range: "min",
      value: 37,
      min: 1,
      max: 700,
      slide: function( event, ui ) {
        $( "#selected-date" ).text( ui.value );
      }
    });
    $( "#selected-date" ).text( $( "#dates-slider" ).slider( "value" ) );
  });
