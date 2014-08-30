var data = {
  medios: []
};

var dummyData = {
  medios: [
  {
    name: "radio nacional",
    periodos: [
    {
      from: "2014-07-01",
      to: "2014-07-07",
      words: [
      {word: "fondos buitre", freq: 20},
      {word: "inflacion", freq: 14},
      {word: "dolar", freq: 7}
      ]
    },
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
  },
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
    },
    ]
  }
  ]
};

$(function() {
  bindSlider();
  findData();
});

function findData() {
  var url = "/server/week";

  $.getJSON(url, function(d) {
    data = d;

    var period = getPeriods(data)[0];
    $( "#selected-date" ).text( periodLabel(period) );
    drawTagClouds(data, period);

    $( "#dates-slider" ).slider("option", "max", getPeriods(data).length);
  });
}

function getPeriods(data) {
  var periods = data.medios.map(function(medio) {
    return medio.periodos.map(function(periodo) {
      return {from: periodo.from, to: periodo.to};
    });
  });

  return _.chain(periods)
    .flatten()
    .uniq(false, function(period) { return period.from; })
    .sortBy("from")
    .value();
}

function drawTagClouds(data, period) {
  var container = $(".medios");
  container.empty();
  console.log("1");

  _.each(data.medios, function(medio) {
    console.log(medio.name);
    var $medio = $("<li class='medio'><h2>" + medio.name + "</h2><div class='cloud' /></li>");
    container.append($medio);

    var medioPeriod = _.find(medio.periodos, function(p) {
      return p.from === period.from;
    });

    if (medioPeriod) {
      var words = medioPeriod.words.map(function(w) {
        return {text: w.word, size: w.freq};
      });

      d3.layout.cloud().size([300, 150])
      .words(words)
      .padding(5)
      .rotate(function() { return ~~(Math.random() * 2) * 90; })
      .font("Impact")
      .fontSize(function(d) { return d.size * 2; })
      .on("end", function(words) { return draw(words, $medio.find(".cloud")[0]); })
      .start();
    } else {
      $medio.append("<p>No hay datos para estas fechas en " + medio.name + "</p>");
    }
  }
  );
}

function periodLabel(period) {
  return "Desde " + period.from + " hasta " + period.to;
}

function bindSlider() {
  $( "#dates-slider" ).slider({
    range: "min",
    value: 0,
    min: 0,
    max: getPeriods(data).length - 1,
    slide: function( event, ui ) {
      var period = getPeriods(data)[ui.value];
      $( "#selected-date" ).text( periodLabel(period) );

      drawTagClouds(data, period);
    }
  });

}

var fill = d3.scale.category20();


function draw(words, elem) {
  d3.select(elem).append("svg")
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

