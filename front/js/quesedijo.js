var data =  {
  medios: [
  {
    name: "radiomitre",
    periodos: [
    {
      from: "2014-07-01",
      to: "2014-07-07",
      words: [
      {word: "fondos buitre", freq: 10},
      {word: "inflacion", freq: 8},
      {word: "dolar", freq: 5}
      ]
    },
    {
      from: "2014-07-08",
      to: "2014-07-14",
      words: [
      {word: "fondos buitre", freq: 12},
      {word: "inflacion", freq: 7},
      {word: "dolar", freq: 9}
      ]
    }  ,
    {
      from: "2014-07-15",
      to: "2014-07-21",
      words: [
      {word: "fondos buitre", freq: 12},
      {word: "inflacion", freq: 7},
      {word: "dolar", freq: 9}
      ]
    }  ,
    {
      from: "2014-07-22",
      to: "2014-07-28",
      words: [
      {word: "fondos buitre", freq: 17},
      {word: "inflacion", freq: 2},
      {word: "messi", freq: 18},
      {word: "dolar", freq: 8}
      ]
    }  
    ]

  }
  ]
};

Medios = {
  
}

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

  var words = data.medios[0].periodos[0].words.map(function(w) {
    return {text: w.word, size: w.freq};
  });

  d3.layout.cloud().size([300, 150])
      .words(words)
      .padding(5)
      .rotate(function() { return ~~(Math.random() * 2) * 90; })
      .font("Impact")
      .fontSize(function(d) { return d.size * 2; })
      .on("end", draw)
      .start();
  });

  var fill = d3.scale.category20();

  function draw(words) {
    d3.select(".cloud").append("svg")
        .attr("width", 300)
        .attr("height", 300)
      .append("g")
        .attr("transform", "translate(150,150)")
      .selectAll("text")
        .data(words)
      .enter().append("text")
        .style("font-size", function(d) { return d.size + "px"; })
        .style("font-family", "Impact")
        .style("fill", function(d, i) { return fill(i); })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { return d.text; });
  }

